
import threading, random, copy, struct
from dataclasses import dataclass, field, asdict
from skyfield.api import load, wgs84, EarthSatellite, Timescale
from skyfield.positionlib import Geocentric
from datetime import datetime
import numpy as np
from numpy import cos, pi, log10, sinc, sqrt, arccos, degrees, radians
import pytz
from scipy.spatial.transform import Rotation
from minsp import SpacePacket

from .core import Scenario, Status, TTCModes, TTCAntenna, AOCSTarget, TTCState, OverrideState, custom_dict_factory, HPTC, Quality

@dataclass
class SpacecraftState:
    ts: float = 0.0
    position: Geocentric = None
    is_sunlit: bool = None

    aocs_chain: str = 'A'
    aocs_mode: AOCSTarget = AOCSTarget.NADIR
    aocs_valid: Status = Status.unkown
    aocs_prev_mode: AOCSTarget = AOCSTarget.NADIR
    aocs_rotation: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    aocs_rates: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    aocs_sun_angle: float = 0.0
    aocs_nadir_angle: float = 0.0
    aocs_damp: float = 1.0

    ttc_chain: str = 'A'
    ttc_obc: Status = Status.nominal
    ttc_mode: TTCModes = TTCModes.S_Sub_LBR
    ttc_s_antenna: TTCAntenna = TTCAntenna.LGA_RHC
    ttc_x_antenna: TTCAntenna = TTCAntenna.MGA
    ttc_snr_ul: float = 12
    ttc_state_ul: TTCState = TTCState.NO_RF
    ttc_coherent: Status = Status.disabled
    ttc_tx_status: Status = Status.on
    ttc_ping_ack: int = 0
    ttc_ranging: Status = Status.disabled

    eps_chain: str = 'A'
    eps_net_power: float = 0.0
    eps_sol_array: list[Status] = field(default_factory=lambda: [Status.nominal, Status.nominal])
    eps_battery_dod: float = 50.0
    eps_temperature: float = 40.0
    eps_acu: Status = Status.nominal
    eps_pdu: Status = Status.nominal

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
    ov_no_tm: bool = False
    frame_quality: Quality = Quality.unknown
    frame_checks: Status = Status.enabled

    def to_dict(self):
        return asdict(self, dict_factory=custom_dict_factory)

    def scrub(self):
        _state = copy.deepcopy(self)

        _state.aocs_chain = '0'
        _state.aocs_mode = AOCSTarget.NADIR
        _state.aocs_valid = Status.unkown
        _state.aocs_rotation = [0.0, 0.0, 0.0]
        _state.aocs_rates = [0.0, 0.0, 0.0]
        _state.aocs_sun_angle = 0.0
        _state.aocs_nadir_angle = 0.0

        _state.eps_chain = '0'
        _state.eps_net_power = 0
        _state.eps_sol_array = [Status.disabled, Status.disabled]
        _state.eps_battery_dod = 0.0
        _state.eps_temperature = 0.0
        _state.eps_acu = Status.disabled
        _state.eps_pdu = Status.disabled

        _state.dhs_chain = '0'
        _state.dhs_obsw_mode = Status.nominal
        _state.dhs_mem_dump_enabled = False
        _state.dhs_memory = 0.0
        _state.dhs_tm_counter = 0
        _state.dhs_tc_counter = 0

        _state.pl_gps_status = Status.off
        _state.pl_gps_pos = [0.0, 0.0, 0.0]
        _state.pl_camera_status = Status.off
        _state.pl_camera_config = ''
        _state.pl_sdr_status = Status.off
        _state.pl_sdr_config = ''

        return _state

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

        # spacecraft commanding for tc
        self.command = Command()

        # book-keeping
        self.triggered_safe_mode = False

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
            _state.frame_quality = gs_state.frame_quality
            _state.frame_checks = gs_state.frame_checks

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

        # FIXME
        if ov_state is not None and ov_state.no_tm is not None:
            _state.ov_no_tm = ov_state.no_tm
        else:
            _state.ov_no_tm = False

        # handle frame quality override
        if ov_state is not None and ov_state.frame_quality is not None:
            if 'frame_quality' not in self.prev_states:
                self.prev_states['frame_quality'] = _state.frame_quality
            _state.frame_quality = ov_state.frame_quality
        else:
            if 'frame_quality' in self.prev_states:
                _state.frame_quality = self.prev_states['frame_quality']
                del self.prev_states['frame_quality']

        # no TM if frame quality is not good
        if _state.status_dl == TTCState.FRAME_LOCK and _state.frame_quality != Quality.good:
            _state.ov_no_tm = True

        if _state.status_dl == TTCState.FRAME_LOCK and _state.frame_checks == Status.disabled:
            _state.ov_no_tm = True
        
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
            # if _state.ttc_snr_ul > 11.8:
            #     _state.ttc_state_ul = TTCState.FRAME_LOCK
            if _state.ttc_snr_ul > 8:
                _state.ttc_state_ul = TTCState.BIT_LOCK
            elif _state.ttc_snr_ul > -3:
                _state.ttc_state_ul = TTCState.PSK_LOCK
            elif _state.ttc_snr_ul > -4:
                _state.ttc_state_ul = TTCState.PLL_LOCK
        
        if(not _state.sweep_done):
            _state.ttc_state_ul = TTCState.NO_RF

        if int(_state.ttc_state_ul) < int(TTCState.PLL_LOCK) or int(_state.status_dl) < int(TTCState.PLL_LOCK):
            _state.ttc_coherent = Status.disabled

        return _state

    def _calculate_snr_ul(self, distance, ul_pwr):
        if distance and distance > 0:
            return -20 * log10(distance) + 28 + ul_pwr
        else:
            return 0

    # EPS
    def _update_eps(self, _state: SpacecraftState, ts: float) -> SpacecraftState:
        _state.eps_net_power = self._calc_net_power(_state)

        # update battery dod
        if _state.ts > 0:
            _state.eps_battery_dod = _state.eps_battery_dod - (_state.eps_net_power*(ts-_state.ts))

        # limit battery dod
        if _state.eps_battery_dod >= 100:
            _state.eps_battery_dod = 100
        if _state.eps_battery_dod <= 0:
            _state.eps_battery_dod = 0

        # trigger safe mode if running out of battery and not triggered before
        if _state.eps_battery_dod >= 95:
            if not self.triggered_safe_mode:
                _state, _ = self.command._execute_admin(_state, { 'control': 'trigger_safe_mode' })
                self.triggered_safe_mode = True
        else:
            self.triggered_safe_mode = False

        # update temperature
        equilibrium_temp = 10
        eclipse_temp = 20
        transmitter_on_temp = 10
        gps_on_temp = 10
        cam_on_temp = 10
        target_temp = equilibrium_temp + int(_state.ttc_tx_status==Status.on)*transmitter_on_temp + int(_state.is_sunlit)*eclipse_temp+\
            int(self.state.pl_gps_status==Status.on)*gps_on_temp + int(self.state.pl_camera_status==Status.on)*cam_on_temp

        _state.eps_temperature = self.state.eps_temperature - (_state.eps_temperature-target_temp)*self.scenario.time_step*0.005 + random.random()-0.5

        if _state.eps_temperature >= 60:
            _state, _ = self.command._execute_admin(_state, { 'control': 'trigger_safe_mode' })

        return _state

    def _calc_net_power(self, _state: SpacecraftState) -> float:
        _power = -2.0 # base comsumption

        if _state.eps_sol_array[0] == Status.nominal:
            _power += 5 * int(_state.is_sunlit)
        if _state.eps_sol_array[1] == Status.nominal:
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

    def _update_memory(self, _state: SpacecraftState, gs_state, ts: float):

        # reset memory dump when memory empty
        if _state.dhs_memory <= 0.0:
            _state.dhs_mem_dump_enabled = False

        # memory usage updates
        _use = 0.0001 # memory fills with basic TM
        if _state.pl_camera_status == Status.on:
            _use += 0.5 # memory fills with Camera data
        if _state.pl_gps_status == Status.on:
            _use += 0.0005 # memory fills with GPS data
        _state.dhs_memory += _use * (ts-_state.ts)

        # if memory dump enabled
        if _state.dhs_mem_dump_enabled:

            # updated modifier based on bit rate
            if _state.dhs_mem_dump_enabled is True:
                if _state.ttc_mode.name[-3:] == 'LBR':  # in a low bit rate mode
                    _mod = 0.6
                if _state.ttc_mode.name[-3:] == 'HBR':  # in a high bit rate mode
                    _mod = 1.2

            # update modifier based on S/X-band
            if _state.ttc_mode.name[0] == 'S':  # S-band
                _mod = _mod * 1
            if _state.ttc_mode.name[0] == 'X':  # X-band
                _mod = _mod * 3

            # update modifier based on carrier
            if _state.ttc_mode.name.split('_')[1] == 'Sup':  # supressed carrier
                _mod = _mod * 1/1
            if _state.ttc_mode.name.split('_')[1] == 'Res':  # residual carrier
                _mod = _mod * 1/4
            if _state.ttc_mode.name.split('_')[1] == 'Sub':  # subcarrier carrier
                _mod = _mod * 1/8

            _state.dhs_memory -= _mod * (ts-_state.ts)

        # bound value to percentage
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
        _state = self._update_eps(_state, ts)

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

    def set_state(self, state: SpacecraftState) -> None:
        self.lock.acquire()

        try:
            self.state = state
        except:
            # handle set state error
            print('set state error')
        finally:
            self.lock.release()

    def control(self, data, ov_state=None, admin=False):
        # default results
        _ok = { 'status': 'g:REL g:ACC g:OK' }
        _fail = { 'status': 'g:REL g:ACC r:FAIL' }
        _unk = { 'status': 'g:REL w:ACC w:UNK' }

        # handle admin commands
        if admin is True:
            _state, _result = self.command.execute(self.state, data, ov_state=ov_state, admin=True)
            self.set_state(_state)
            return _result

        # no tc override -> immediately return error
        if ov_state and ov_state.no_tc is True:
            return { 'status': 'g:REL w:ACC w:UNK' }

        # need at least ground station U/L carrier enabled and sweep done for spacon commanding
        if admin is False:
            if self.state.gs_carrier_ul is None or self.state.gs_carrier_ul == Status.off or self.state.sweep_done is False:
                return _fail

        # check if OBC error -> only high priority TC works
        if self.state.ttc_obc == Status.error:
            if data['command'] not in HPTC:
                return _unk

        # LBSC25 if in X-band + HGA antenna -> no TM + no TC + no spectrum
        if self.state.ttc_mode.name[0] == 'X' and self.state.ttc_x_antenna == TTCAntenna.HGA:
            return { 'status': 'g:REL w:UNK w:UNK' }

        # handle spacon commands
        _state, _result = self.command.execute(self.state, data, ov_state=ov_state, admin=False)
        self.set_state(_state)
        return _result

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


class Command:
    def __init__(self) -> None:
        # default results
        self.ok = { 'status': 'g:REL g:ACC g:OK' }
        self.fail = { 'status': 'g:REL g:ACC r:FAIL' }
        self.unk = { 'status': 'g:REL w:ACC w:UNK' }

    def execute(self, state: SpacecraftState, data, ov_state=None, admin=False) -> tuple[SpacecraftState, dict]:
        if admin:
            return self._execute_admin(state, data)
        else:
            return self._execute_tc(state, data, ov_state=ov_state)

    # handle the execution of commands from the admin
    def _execute_admin(self, state: SpacecraftState, data) -> tuple[SpacecraftState, dict]:
        result = self.ok

        # admin actions
        if data['control'] == 'trigger_safe_mode':
            state.aocs_valid = Status.unkown
            state.aocs_chain = 'B'
            state.aocs_mode = AOCSTarget.SUN
            state.ttc_chain = 'B'
            state.ttc_mode = TTCModes.S_Sup_LBR
            state.eps_chain = 'B'
            state.dhs_chain = 'B'
            state.dhs_obsw_mode = Status.safe
            state.pl_gps_status = Status.off
            state.pl_camera_status = Status.off
        if data['control'] == 'trigger_ttc_obc_error':
            state.ttc_obc = Status['error']

        # FIXME admin set status
        if data['control'] == 'aocs_mode':
            state.aocs_mode = AOCSTarget[data['value']]
        if data['control'] == 'aocs_valid':
            state.aocs_valid = Status[data['value']]
        if data['control'] == 'ttc_mode':
            state.ttc_mode = TTCModes[data['value']]
        if data['control'] == 'ttc_s_antenna':
            state.ttc_s_antenna = TTCAntenna[data['value']]
        if data['control'] == 'ttc_x_antenna':
            state.ttc_x_antenna = TTCAntenna[data['value']]
        if data['control'] == 'ttc_obc':
            state.ttc_obc = Status[data['value']]
        if data['control'] == 'dhs_obsw_mode':
            state.dhs_obsw_mode = Status[data['value']]

        return state, result

    # handle the execution of commands by the spacon
    def _execute_tc(self, state: SpacecraftState, data, ov_state=None) -> tuple[SpacecraftState, dict]:
        result = self.fail

        # defaul to unknown if no tm override
        if ov_state and ov_state.no_tm is True:
            _ok = { 'status': 'g:REL g:ACC w:UNK' }
            _fail = { 'status': 'g:REL g:ACC w:UNK' }
        else:
            _ok = self.ok
            _fail = self.fail

        # AOCS
        if data['control'] == 'aocs_mode':
            if data['value'] in ['SUN', 'TARGET', 'NADIR', 'RATEDAMPING', 'MONITORING']:
                state.aocs_mode = AOCSTarget[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'aocs_chain':
            if data['value'] in ['A', 'B']:
                state.aocs_chain = data['value']
                result = _ok
            else:
                result = _fail
        if data['control'] == 'aocs_valid':
            if data['value'] in ['valid', 'not_valid', 'unknown']:
                state.aocs_valid = Status[data['value']]
                result = _ok
            else:
                result = _fail

        # TTC
        if data['control'] == 'ttc_mode':
            if data['value'] in ['S_Sup_LBR', 'S_Sup_HBR', 'X_Sup_LBR', 'X_Sup_HBR', 'S_Res_LBR', 'X_Res_LBR', 'S_Sub_LBR', 'X_Sub_LBR']:
                state.ttc_mode = TTCModes[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_s_antenna':
            if data['value'] in ['LGA_RHC', 'LGA_LHC']:
                state.ttc_s_antenna = TTCAntenna[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_x_antenna':
            if data['value'] in ['MGA', 'HGA']:
                state.ttc_x_antenna = TTCAntenna[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_chain':
            if data['value'] in ['A', 'B']:
                state.ttc_chain = data['value']
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_obc_reboot':
            state.ttc_obc = Status['nominal']
            result = _ok
        if data['control'] == 'ttc_ping_ack':
            state.ttc_ping_ack = state.ttc_ping_ack + 1
            result = _ok
        if data['control'] == 'ttc_coherent':
            if data['value'] in ['enabled', 'disabled']:
                state.ttc_coherent = Status[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_tx_status':
            if data['value'] in ['on', 'off']:
                state.ttc_tx_status = Status[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'ttc_ranging':
            if data['value'] in ['enabled', 'disabled']:
                state.ttc_ranging = Status[data['value']]
                result = _ok
            else:
                result = _fail

        # EPS
        if data['control'] == 'eps_chain':
            if data['value'] in ['A', 'B']:
                # on chain swap -> OBSW to safe and ADCS to Sun pointing
                if state.eps_chain != data['value']:
                    state.dhs_obsw_mode = Status.safe
                    state.aocs_mode = AOCSTarget.SUN
                state.eps_chain = data['value']
                result = _ok
            else:
                result = _fail
        if data['control'] == 'eps_battery_dod':
            state.eps_battery_dod = float(data['value'])
            result = _ok
        if data['control'] == 'eps_sol_array__0' or data['control'] == 'eps_sol_array__1':
            if data['value'] in ['nominal', 'enabled', 'disabled']:
                _idx = int(data['control'].split('__')[-1])
                if _idx in [0, 1]:
                    state.eps_sol_array[_idx] = Status[data['value']]
                    result = _ok
            else:
                result = _fail

        # DHS
        if data['control'] == 'dhs_chain':
            if data['value'] in ['A', 'B']:
                # on chain swap -> OBSW to safe and ADCS to Sun pointing
                if state.dhs_chain != data['value']:
                    state.dhs_obsw_mode = Status.safe
                    state.aocs_mode = AOCSTarget.SUN
                state.dhs_chain = data['value']
                result = _ok
            else:
                result = _fail
        if data['control'] == 'dhs_obsw_mode':
            if data['value'] in ['safe', 'nominal']:
                state.dhs_obsw_mode = Status[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'dhs_mem_dump_enabled':
            if data['value'] in [True, False]:
                state.dhs_mem_dump_enabled = data['value']
                result = _ok
            else:
                result = self.fail
        if data['control'] == 'dhs_uploaded':
            if ov_state.no_uploads is not None and ov_state.no_uploads is True:
                result = _fail
            else:
                state.dhs_uploaded = state.dhs_uploaded + [data['value']]
                result = _ok

        # Payload
        if data['control'] == 'pl_gps_status':
            if state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    state.pl_gps_status = Status[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'pl_camera_status':
            if state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    state.pl_camera_status = Status[data['value']]
                result = _ok
            else:
                result = _fail
        if data['control'] == 'pl_sdr_status':
            if state.dhs_obsw_mode == Status.nominal:
                if data['value'] in ['on', 'off']:
                    state.pl_sdr_status = Status[data['value']]
                result = _ok
            else:
                result = _fail

        # return the updated state and result
        return state, result

class SpacePacketHandler:
    def __init__(self):
        self.fmt = 'I3B8f' + 'I4BfBBBIB' + 'If2B2f2B' + 'IB?f2I' + 'B3fBB'
        self.payload_keys = [
            'ts',
            'aocs_chain',
            'aocs_mode',
            'aocs_valid',
            'aocs_rotation_x',
            'aocs_rotation_y',
            'aocs_rotation_z',
            'aocs_rate_x',
            'aocs_rate_y',
            'aocs_rate_z',
            'aocs_sun_angle',
            'aocs_nadir_angle',
            'ttc_chain',
            'ttc_obc',
            'ttc_mode',
            'ttc_s_antenna',
            'ttc_x_antenna',
            'ttc_snr_ul',
            'ttc_state_ul',
            'ttc_coherent',
            'ttc_tx_status',
            'ttc_ping_ack',
            'ttc_ranging',
            'eps_chain',
            'eps_net_power',
            'eps_sol_array_1',
            'eps_sol_array_2',
            'eps_battery_dod',
            'eps_temperature',
            'eps_acu',
            'eps_pdu',
            'dhs_chain',
            'dhs_obsw_mode',
            'dhs_mem_dump_enabled',
            'dhs_memory',
            'dhs_tm_counter',
            'dhs_tc_counter',
            'pl_gps_status',
            'pl_gps_lat',
            'pl_gps_lon',
            'pl_gps_alt',
            'pl_camera_status',
            'pl_sdr_status'
        ]

    def as_byte_string(self, sc_state: SpacecraftState):
        return struct.pack(
            self.fmt,
            int(sc_state.ts),
            ord(sc_state.aocs_chain),
            sc_state.aocs_mode.value,
            sc_state.aocs_valid.value,
            sc_state.aocs_rotation[0], sc_state.aocs_rotation[1], sc_state.aocs_rotation[2],
            sc_state.aocs_rates[0], sc_state.aocs_rates[1], sc_state.aocs_rates[2],
            sc_state.aocs_sun_angle,
            sc_state.aocs_nadir_angle,
            ord(sc_state.ttc_chain),
            sc_state.ttc_obc.value,
            sc_state.ttc_mode.value,
            sc_state.ttc_s_antenna.value,
            sc_state.ttc_x_antenna.value,
            sc_state.ttc_snr_ul,
            sc_state.ttc_state_ul.value,
            sc_state.ttc_coherent,
            sc_state.ttc_tx_status,
            sc_state.ttc_ping_ack,
            sc_state.ttc_ranging,
            ord(sc_state.eps_chain),
            sc_state.eps_net_power,
            sc_state.eps_sol_array[0].value,
            sc_state.eps_sol_array[1].value,
            sc_state.eps_battery_dod,
            sc_state.eps_temperature,
            sc_state.eps_acu,
            sc_state.eps_pdu,
            ord(sc_state.dhs_chain),
            sc_state.dhs_obsw_mode.value,
            sc_state.dhs_mem_dump_enabled,
            sc_state.dhs_memory,
            sc_state.dhs_tm_counter,
            sc_state.dhs_tc_counter,
            sc_state.pl_gps_status.value,
            sc_state.pl_gps_pos[0],
            sc_state.pl_gps_pos[1],
            sc_state.pl_gps_pos[2],
            sc_state.pl_camera_status.value,
            sc_state.pl_sdr_status.value
        )

    def as_dict(self, packet: SpacePacket, post_proc: bool = True):
        values = struct.unpack(self.fmt, packet.data_field)

        data = {
            'primary_header': {
                 'version': '0b' + format(packet.version, '03b'),
                 'type': "TM" if packet.type == 0 else "TC",
                 'sec_hdr_flag': '0b' + format(packet.secondary_header_flag, '01b'),
                 'apid': packet.apid,
                 'sequence_flags': '0b' + format(packet.sequence_flags, '02b'),
                 'sequence_count': packet.sequence_count,
                 'data_length': packet.data_length
            },
            'sec_hdr': None,
            'payload': dict(zip(self.payload_keys, values))
        }

        if post_proc:
            data['payload']['aocs_chain'] = chr(data['payload']['aocs_chain'])
            data['payload']['aocs_mode'] = AOCSTarget(data['payload']['aocs_mode']).name.upper()
            data['payload']['aocs_valid'] = Status(data['payload']['aocs_valid']).name.upper()
            data['payload']['ttc_chain'] = chr(data['payload']['ttc_chain'])
            data['payload']['ttc_obc'] = Status(data['payload']['ttc_obc']).name.upper()
            data['payload']['ttc_mode'] = TTCModes(data['payload']['ttc_mode']).name.upper()
            data['payload']['ttc_s_antenna'] = TTCAntenna(data['payload']['ttc_s_antenna']).name.upper()
            data['payload']['ttc_x_antenna'] = TTCAntenna(data['payload']['ttc_x_antenna']).name.upper()
            data['payload']['ttc_state_ul'] = TTCState(data['payload']['ttc_state_ul']).name.upper()
            data['payload']['ttc_tx_status'] = Status(data['payload']['ttc_tx_status']).name.upper()
            data['payload']['ttc_coherent'] = Status(data['payload']['ttc_coherent']).name.upper()
            data['payload']['eps_chain'] = chr(data['payload']['eps_chain'])
            data['payload']['eps_sol_array_1'] = Status(data['payload']['eps_sol_array_1']).name.upper()
            data['payload']['eps_sol_array_2'] = Status(data['payload']['eps_sol_array_2']).name.upper()
            data['payload']['eps_acu'] = Status(data['payload']['eps_acu']).name.upper()
            data['payload']['eps_pdu'] = Status(data['payload']['eps_pdu']).name.upper()
            data['payload']['dhs_chain'] = chr(data['payload']['dhs_chain'])
            data['payload']['dhs_obsw_mode'] = Status(data['payload']['dhs_obsw_mode']).name.upper()
            data['payload']['pl_gps_status'] = Status(data['payload']['pl_gps_status']).name.upper()
            data['payload']['pl_camera_status'] = Status(data['payload']['pl_camera_status']).name.upper()
            data['payload']['pl_sdr_status'] = Status(data['payload']['pl_sdr_status']).name.upper()
        else:
            data['payload']['dhs_mem_dump_enabled'] = int(data['payload']['dhs_mem_dump_enabled'])

        return data

    def space_packet(self, sc_state: SpacecraftState):
        payload = self.as_byte_string(sc_state)

        packet = SpacePacket(apid=10, data_field=payload)

        return packet

    def from_bytestream(self, bytes):
        return SpacePacket.from_bytes(bytes)

