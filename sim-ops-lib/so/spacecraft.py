
import threading, random, copy
from dataclasses import dataclass, field, asdict
from skyfield.api import load, wgs84, EarthSatellite, Timescale
from skyfield.positionlib import Geocentric
from datetime import datetime
import numpy as np
from numpy import cos, pi, log10, sinc, sqrt, arccos, degrees, radians
import pytz
from scipy.spatial.transform import Rotation

from .core import Scenario, Status, TTCModes, AOCSTarget, TTCState, OverrideState, custom_dict_factory

@dataclass
class SpacecraftState:
    ts: float = 0.0
    position: Geocentric = None
    is_sunlit: bool = None

    aocs_valid: Status = Status.unkown
    aocs_chain: str = 'A'
    aocs_mode: AOCSTarget = AOCSTarget.NADIR
    aocs_prev_mode: AOCSTarget = AOCSTarget.NADIR
    aocs_rotation: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    aocs_rates: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    aocs_sun_angle: float = 0.0
    aocs_nadir_angle: float = 0.0
    aocs_damp: float = 1.0

    ttc_chain: str = 'A'
    ttc_mode: TTCModes = TTCModes.SHBR
    ttc_snr_ul: float = 12
    ttc_state_ul: TTCState = TTCState.NO_RF
    ttc_coherent: bool = False
    ttc_tx_status: Status = Status.on
    ttc_ping_ack: int = 0

    pts_chain: str = 'A'
    pts_net_power: float = 0.0
    pts_sol_array: list[Status] = field(default_factory=lambda: [Status.nominal, Status.nominal])
    pts_battery_dod: float = 50.0
    pts_temperature: float = 40.0

    dhs_chain: str = 'A'
    dhs_obsw_mode: Status = Status.nominal
    dhs_mem_dump_enabled: bool = False
    dhs_memory: float = 50
    dhs_tm_counter: int = 0
    dhs_tc_counter: int = 0
    dhs_tm_window: list[str] = field(default_factory=list)
    dhs_tc_history: list[str] = field(default_factory=list)
    dhs_uploaded: list[str] = field(default_factory=list)

    pl_gps_status: Status = Status.off
    pl_gps_pos: list[Status] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    pl_camera_status: Status = Status.off
    pl_camera_config: str = 'LE'
    pl_sdr_status: Status = Status.off
    pl_sdr_config: str = 'BCN'

    # book-keeping
    gs_carrier_ul = Status.off
    gs_position: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    status_dl: TTCState = TTCState.NO_RF
    sweep_done: bool = False

    def to_dict(self):
        return asdict(self, dict_factory=custom_dict_factory)


class SpacecraftSim:
    def __init__(self, scenario: Scenario, initial_state: SpacecraftState = None) -> None:
        self.scenario = scenario
        self.time_scale = load.timescale()

        self.ephemeris = load('de421.bsp')
        self.earth = self.ephemeris['earth']
        self.sun = self.ephemeris['sun']
        lines = [x.strip() for x in self.scenario.tle.split("\n") if len(x) > 0]
        self.satellite = EarthSatellite(lines[1], lines[2], lines[0])

        # store previous values for after removing overries
        self.prev_states = {}

        # start with the initial state argument if available
        if initial_state:
            self.state = initial_state
        # otherwise start with new state
        else:
            self.state = SpacecraftState(ts=datetime.fromisoformat(self.scenario.begin).timestamp())

        # update initial state with params defined in the scenario
        if scenario.sc_initial_state:
            for k, v in scenario.sc_initial_state.items():
                self.state.__setattr__(k, v)

        self.lock = threading.Lock()

    def _updates_from_gs_state(self, _state: SpacecraftState, gs_state) -> SpacecraftState:

        if gs_state:
            _state.gs_carrier_ul = gs_state.carrier_ul
            # update D/L status from ground station if spacecraft transmistter is on
            if _state.ttc_tx_status == Status.on:
                _state.status_dl = gs_state.status_dl
            else:
                _state.status_dl = TTCState.NO_RF
            _state.sweep_done = gs_state.sweep_done

        else:
            _state.gs_carrier_ul = None

        if gs_state and len(gs_state.position)>1:
            _state.gs_position = gs_state.position
        else:
            _state.gs_position = [0.0, 0.0, 0.0]
        
        return _state

    def _handle_overrides(self, _state: SpacecraftState, ov_state: OverrideState) -> SpacecraftState:

        if ov_state is not None and ov_state.tx_status is not None:
            if 'tx_status' not in self.prev_states:
                self.prev_states['tx_status'] = _state.ttc_tx_status
            _state.ttc_tx_status = ov_state.tx_status
        else:
            if 'tx_status' in self.prev_states:
                _state.ttc_tx_status = self.prev_states['tx_status']
                del self.prev_states['tx_status']

        return _state

    def _update_position(self, _state: SpacecraftState, ts: float) -> SpacecraftState:
        dt = datetime.fromtimestamp(ts, tz=pytz.UTC)
        t = self.time_scale.from_datetime(dt)

        _state.position = self.satellite.at(t)
        _state.is_sunlit = bool(_state.position.is_sunlit(self.ephemeris))

        if self.state.pl_gps_status == Status.on:
            pos = wgs84.geographic_position_of(_state.position)
            _state.pl_gps_pos = [pos.latitude.degrees, pos.longitude.degrees, pos.elevation.km]
        else:
            _state.pl_gps_pos = [0,0,0]
        return _state

    # AOCS
    def _simulate_aocs(self, _state: SpacecraftState, ts: float) -> SpacecraftState:
        dt = datetime.fromtimestamp(ts, tz=pytz.UTC)
        t = self.time_scale.from_datetime(dt)

        sat_pos = _state.position.position.km
        earth_pos = self.earth.at(t).observe(self.earth).position.km
        sun_pos = self.earth.at(t).observe(self.sun).position.km

        nadir_dir = earth_pos - sat_pos
        sun_dir = sun_pos - sat_pos

        if _state.aocs_mode != _state.aocs_prev_mode:
            _state.aocs_damp = 0.0
            _state.aocs_prev_mode = _state.aocs_mode

        if _state.aocs_damp < 1.0:
            _state.aocs_damp += 0.05
        if _state.aocs_damp > 1.0:
            _state.aocs_damp = 1.0

        if _state.aocs_mode == AOCSTarget.NADIR:
            new_rotation = self._aocs_euler_angles(nadir_dir, np.array([0, 0, -1]))
            _state.aocs_nadir_angle = self._aocs_calc_angle(nadir_dir, nadir_dir) + (1-_state.aocs_damp)*_state.aocs_nadir_angle
            _state.aocs_sun_angle = self._aocs_calc_angle(sun_dir, nadir_dir) * _state.aocs_damp

        if _state.aocs_mode == AOCSTarget.SUN:
            new_rotation = self._aocs_euler_angles(sun_dir, np.array([0, 0, -1]))
            _state.aocs_nadir_angle = self._aocs_calc_angle(nadir_dir, sun_dir) * _state.aocs_damp
            _state.aocs_sun_angle = self._aocs_calc_angle(sun_dir, sun_dir) + (1-_state.aocs_damp)*_state.aocs_sun_angle

        _state.aocs_rates = list(np.absolute(np.array(new_rotation)*_state.aocs_damp) - np.absolute(np.array(_state.aocs_rotation)))
        _state.aocs_rotation = list(np.array(new_rotation)*_state.aocs_damp)

        return _state

    def _aocs_calc_angle(self, v1, v2):
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)

        angle_rad = np.arccos(np.dot(v1, v2))
        angle_deg = np.degrees(angle_rad)

        if np.isnan(angle_deg):
            angle_deg = 0.0

        return angle_deg

    def _aocs_euler_angles(self, v1, v2):
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)

        dot_product = np.dot(v1, v2)
        angle = np.arccos(dot_product)

        axis = np.cross(v1, v2)
        axis /= np.linalg.norm(axis)

        w = np.cos(angle / 2)
        x, y, z = axis * np.sin(angle / 2)
        t0 = 2.0 * (w * x + y * z)
        t1 = 1.0 - 2.0 * (x**2 + y**2)
        roll = np.arctan2(t0, t1)

        t2 = 2.0 * (w * y - z * x)
        t2 = 1 if t2 > 1 else t2
        t2 = -1 if t2 < -1 else t2
        pitch = np.arcsin(t2)

        t3 = 2.0 * (w * z + x * y)
        t4 = 1.0 - 2.0 * (y**2 + z**2)
        yaw = np.arctan2(t3, t4)

        return np.degrees([roll, pitch, yaw])

    # TTC
    def _update_ttc(self, _state: SpacecraftState, gs_state) -> SpacecraftState:

        # update U/L snr
        _distance = np.linalg.norm(_state.gs_position)
        _ul_power = gs_state.power_ul * int(gs_state.carrier_ul == Status.on) if gs_state else 50
        _state.ttc_snr_ul = self._calculate_snr_ul(_distance, _ul_power)


        # update U/L state
        _state.ttc_state_ul = TTCState.NO_RF
        if _state.ttc_tx_status == Status.on:
            if _state.ttc_snr_ul > 11.8:
                _state.ttc_state_ul = TTCState.FRAME_LOCK
            elif _state.ttc_snr_ul > 8:
                _state.ttc_state_ul = TTCState.BIT_LOCK
            elif _state.ttc_snr_ul > -3:
                _state.ttc_state_ul = TTCState.PSK_LOCK
            elif _state.ttc_snr_ul > -4:
                _state.ttc_state_ul = TTCState.PLL_LOCK
        
        if(not _state.sweep_done):
            _state.ttc_state_ul = TTCState.NO_RF

        if int(_state.ttc_state_ul) < int(TTCState.PLL_LOCK) or int(_state.status_dl) < int(TTCState.PLL_LOCK):
            _state.ttc_coherent = False
        
        

        return _state

    def _calculate_snr_ul(self, distance, ul_pwr):
        if distance and distance > 0:
            return -20 * log10(distance) + 28 + ul_pwr
        else:
            return 0

    # PTS
    def _update_pts(self, _state: SpacecraftState, ts: float) -> SpacecraftState:
        _state.pts_net_power = self._calc_net_power(_state)

        # update battery dod
        if _state.ts > 0:
            _state.pts_battery_dod = _state.pts_battery_dod - (_state.pts_net_power*(ts-_state.ts))

        if _state.pts_battery_dod >= 100:
            _state.pts_battery_dod = 100
        if _state.pts_battery_dod <= 0:
            _state.pts_battery_dod = 0
        if _state.pts_battery_dod >= 98:
            _state = self.trigger_safe_mode(_state)

        # update temperature
        equilibrium_temp = 10
        eclipse_temp = 20
        transmitter_on_temp = 10
        gps_on_temp = 10
        cam_on_temp = 10
        target_temp = equilibrium_temp + int(_state.ttc_tx_status==Status.on)*transmitter_on_temp + int(_state.is_sunlit)*eclipse_temp+\
            int(self.state.pl_gps_status==Status.on)*gps_on_temp + int(self.state.pl_camera_status==Status.on)*cam_on_temp

        _state.pts_temperature = self.state.pts_temperature - (_state.pts_temperature-target_temp)*self.scenario.time_step*0.005 + random.random()-0.5

        if _state.pts_temperature >= 60:
            _state = self.trigger_safe_mode(_state)

        return _state

    def _calc_net_power(self, _state: SpacecraftState) -> float:
        _power = -2.0 # base comsumption

        if _state.pts_sol_array[0] == Status.nominal:
            _power += 5 * int(_state.is_sunlit)
        if _state.pts_sol_array[1] == Status.nominal:
            _power += 5 * int(_state.is_sunlit)
        if _state.pl_gps_status == Status.on:
            _power -= 0.5
        if _state.pl_camera_status == Status.on:
            _power -= 4
        if _state.ttc_tx_status == Status.on:
            _power -= 5

        return _power/100

    # DHS
    def _update_dhs(self, _state: SpacecraftState, gs_state, ts: float) -> SpacecraftState:
        # update onboard memory
        _state.dhs_tm_counter = self.state.dhs_tm_counter + 1

        newTM = []
        newTM.append(f"{str(_state.dhs_tm_counter)}\t{datetime.fromtimestamp(ts).isoformat().replace('+00:00', '')}\tReceived TM Packet")
        if self.state.dhs_mem_dump_enabled:
            for i in range(int(self.state.ttc_mode)-2):
                newTM.append(f"\t{(datetime.fromtimestamp(ts)).isoformat().replace('+00:00', '')}\tReceived Memory Packet")
        _state.dhs_tm_window = newTM + self.state.dhs_tm_window[0:12-len(newTM)]

        _state = self._update_memory(_state, gs_state, ts)

        return _state

    # FIXME: enable automatic memory dump with X band
    def _update_memory(self, _state: SpacecraftState, gs_state, ts: float):

        # if no frame lock
        if gs_state and not gs_state.status_dl == TTCState.FRAME_LOCK:
            _state.dhs_mem_dump_enabled = False

        # reset memory dump
        if _state.dhs_memory < 0.1:
            _state.dhs_mem_dump_enabled = False

        # update on board memory
        _mod = 0.0
        if _state.dhs_mem_dump_enabled is True:
            _mod = 0.1
            if _state.ttc_mode == TTCModes.XLBR:
                _mod = 1.1
            if _state.ttc_mode == TTCModes.XHBR:
                _mod = 1.8
        _mod -= 0.0001 # memory fills with basic TM 
        if _state.pl_camera_status == Status.on:
            _mod -= 0.001 # memory fills with Camera data
        if _state.pl_gps_status == Status.on:
            _mod -= 0.0005 # memory fills with GPS data

        _state.dhs_memory -= _mod * (ts-_state.ts)

        if _state.dhs_memory <= 0:
            _state.dhs_memory = 0
        if _state.dhs_memory >= 100:
            _state.dhs_memory = 100
            _state.pl_camera_status = Status.off
            _state.pl_gps_status = Status.off

        return _state

    def ping(self, ts: float, gs_state = None, ov_state: OverrideState = None) -> SpacecraftState:

        # start new state from previous state
        _state = copy.deepcopy(self.state)

        # updates from ground station state
        _state = self._updates_from_gs_state(_state, gs_state)

        # handle overrides
        _state = self._handle_overrides(_state, ov_state)

        # update position and related properties
        _state = self._update_position(_state, ts)

        # update AOCS
        _state = self._simulate_aocs(_state, ts)

        # update TTC
        _state = self._update_ttc(_state, gs_state)

        # update PTS
        _state = self._update_pts(_state, ts)

        # update DHS
        _state = self._update_dhs(_state, gs_state, ts)

        # update ts
        _state.ts = ts

        # update current state
        self.lock.acquire()
        try:
            self.state = _state
        finally:
            self.lock.release()

        # pong
        return self.state
    
    def _set_state(self, settings, idx=None):
        self.lock.acquire()
        try:
            for attr, value in settings:
                if idx is not None:  # FIXME
                    _val = getattr(self.state, attr)
                    _val[idx] = value
                    setattr(self.state, attr, _val)
                else:
                    setattr(self.state, attr, value)
        finally:
            self.lock.release()

    def control(self, data, ov_state=None, admin=False):
        _ok = { 'status': 'g:REL g:ACC g:OK' }
        _fail = { 'status': 'g:REL g:ACC r:FAIL' }

        # overrides
        if ov_state and ov_state.no_tc is True:
            return { 'status': 'g:REL w:ACC w:UNK' }
        if ov_state and ov_state.no_tm is True:
            _ok = { 'status': 'g:REL g:ACC w:UNK' }
            _fail = { 'status': 'g:REL g:ACC w:UNK' }

        # admin actions
        if data['control'] == 'safe_mode':
            _state = self.trigger_safe_mode(self.state)
            self.lock.acquire()
            try:
                self.state = _state
            except:
                return _fail
            finally:
                self.lock.release()
                return _ok

        # need at least ground station U/L carrier enabled
        if admin is False:
            if self.state.gs_carrier_ul is None or self.state.gs_carrier_ul == Status.off:
                return _fail

        # AOCS
        if data['control'] == 'aocs_mode':
            if data['value'] in ['SUN', 'TARGET', 'NADIR', 'RATEDAMPING', 'MONITORING']:
                self._set_state([('aocs_mode', AOCSTarget[data['value']])])
                return _ok
            else:
                return _fail
        if data['control'] == 'aocs_chain':
            if data['value'] in ['A', 'B']:
                self._set_state([('aocs_chain', data['value'])])
                return _ok
            else:
                return _fail
        if data['control'] == 'aocs_valid':
            if data['value'] in ['valid', 'not_valid', 'unknown']:
                self._set_state([('aocs_valid', data['value'])])
                return _ok
            else:
                return _fail

        # TTC
        if data['control'] == 'ttc_mode':
            if data['value'] in ['SLBR', 'SHBR', 'XLBR', 'XHBR']:
                self._set_state([('ttc_mode', TTCModes[data['value']])])
                return _ok
            else:
                return _fail

        if data['control'] == 'ttc_chain':
            if data['value'] in ['A', 'B']:
                self._set_state([('ttc_chain', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'ttc_ping_ack':
            self._set_state([('ttc_ping_ack', self.state.ttc_ping_ack+1)])
            return _ok

        if data['control'] == 'ttc_coherent':
            self._set_state([('ttc_coherent', data['value'])])
            return _ok

        if data['control'] == 'ttc_tx_status':
            if data['value'] in ['on', 'off']:
                self._set_state([('ttc_tx_status', Status[data['value']])])
                return _ok
            else:
                return _fail

        # PTS
        if data['control'] == 'pts_chain':
            if data['value'] in ['A', 'B']:
                self._set_state([('pts_chain', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'pts_sol_array__0' or data['control'] == 'pts_sol_array__1':
            if data['value'] in ['nominal', 'enabled', 'disabled']:
                _idx = int(data['control'].split('__')[-1])
                if _idx in [0, 1]:
                    self._set_state([('pts_sol_array', Status[data['value']])], idx=_idx)
                    return _ok
            return _fail

        # DHS
        if data['control'] == 'dhs_chain':
            if data['value'] in ['A', 'B']:
                self._set_state([('dhs_chain', data['value'])])
                return _ok
            else:
                return _fail
        if data['control'] == 'dhs_obsw_mode':
            if data['value'] in ['safe', 'nominal']:
                self._set_state([('dhs_obsw_mode', Status[data['value']] )])
                return _ok
            else:
                return _fail
        if data['control'] == 'dhs_mem_dump_enabled':
            if data['value'] in [True, False]:
                self._set_state([('dhs_mem_dump_enabled', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'dhs_uploaded':
            if ov_state.no_uploads is not None and ov_state.no_uploads is True:
                return _fail
            else:
                self._set_state([('dhs_uploaded', self.state.dhs_uploaded + [data['value']])])
                return _ok

        # Payload
        if data['control'] == 'pl_gps_status':
            if self.state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    self._set_state([('pl_gps_status', Status[data['value']] )])
                return _ok
            else:
                return _fail
        
        if data['control'] == 'pl_camera_status':
            if self.state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    self._set_state([('pl_camera_status', Status[data['value']] )])
                return _ok
            else:
                return _fail

        if data['control'] == 'pl_sdr_status':
            if self.state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    self._set_state([('pl_sdr_status', Status[data['value']] )])
                return _ok
            else:
                return _fail

        # control not found
        return _fail

    def trigger_safe_mode(self, _state : SpacecraftState) -> SpacecraftState:
        _state.aocs_valid = Status.unkown
        _state.aocs_chain = 'B'
        _state.aocs_mode = AOCSTarget.SUN
        _state.ttc_chain = 'B'
        _state.ttc_mode = TTCModes.SLBR
        _state.pts_chain = 'B'
        _state.dhs_chain = 'B'
        _state.dhs_obsw_mode = Status.safe
        _state.pl_gps_status = Status.off
        _state.pl_camera_status = Status.off

        return _state

    def tc_history(self, data, result) -> None:
        if 'command' not in data or data['command'] is None:
            return None

        self.lock.acquire()
        try:
            self.state.dhs_tc_counter += 1
            _count = str(self.state.dhs_tc_counter).zfill(3)
            _time_stamp = datetime.fromtimestamp(self.state.ts, tz=pytz.UTC).isoformat().replace('+00:00', '')
            self.state.dhs_tc_history.append(f"{_count}\t{_time_stamp}\t{data['command']}")
            # FIXME TC history length
            # if len(self.state.dhs_tc_history) > 12:
            #     self.state.dhs_tc_history = self.state.dhs_tc_history[-12:]
        finally:
            self.lock.release()

