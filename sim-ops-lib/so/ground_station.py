
import copy, threading, logging
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from skyfield.api import load, wgs84, EarthSatellite
from datetime import datetime
import numpy as np
from numpy import cos, pi, log10, sinc, sqrt
import pytz

from .core import Scenario, Status, TTCModes, TTCAntenna, TTCState, OverrideState, Quality, custom_dict_factory, DEFAULT_STATUS_DL_TRANSITIONS

logger = logging.getLogger(__name__)

@dataclass
class GroundStationState:
    ts: float = None
    carrier_ul: Status = Status.off
    spectrum_ul: list[float] = field(default_factory=list)
    spectrum_dl: list[float] = field(default_factory=list)
    frame_quality: Quality = Quality.unknown
    frame_checks: Status = Status.enabled
    status_dl: TTCState = TTCState.NO_RF
    status_dl_transitions: dict = field(default_factory=lambda: DEFAULT_STATUS_DL_TRANSITIONS)
    snr_dl: float = -128
    elevation: float = None
    azimuth: float = None
    distance: float = None
    interference: bool = False
    auto_track: bool = False
    program_track: bool = False
    doppler_enabled: bool = False
    doppler_velocity: float = None
    sweep_done: bool = False
    mode: TTCModes = TTCModes.S_Sub_LBR
    power_ul: float = 50.0
    position: list[float] = field(default_factory=list)

    # book-keeping
    auto_range: bool = False
    ul_state: TTCState = TTCState.NO_RF
    ul_snr: float = -128
    modes: list[str] = field(default_factory=lambda: [m.name for m in TTCModes])
    next_pass_start: str = ''
    next_pass_end: str = ''
    sweep_count: int = 0
    flight_dynamics: dict = field(default_factory=list)
    name: str = 'ESOC-1'

    def to_dict(self):
        return asdict(self, dict_factory=custom_dict_factory)

# ground station simulator
class GroundStationSim:
    def __init__(self, scenario : Scenario, initial_state : GroundStationState = None) -> None:
        self.scenario = scenario

        self.dt_i = datetime.fromisoformat(self.scenario.begin)
        self.dt_f = datetime.fromisoformat(self.scenario.end)

        self.location = wgs84.latlon(scenario.ground_station.latitude,
                                     scenario.ground_station.longitude,
                                     elevation_m=scenario.ground_station.altitude)
        lines = [x.strip() for x in self.scenario.tle.split("\n") if len(x) > 0]
        self.satellite = EarthSatellite(lines[1], lines[2], lines[0])
        self.time_scale = load.timescale()

        # calculate passes for current day
        self.t_i = self.time_scale.utc(self.dt_i.year, self.dt_i.month, self.dt_i.day, 0, 0, 0)
        self.t_f = self.time_scale.utc(self.dt_f.year, self.dt_f.month, self.dt_f.day, 23, 59, 59)
        t, events = self.satellite.find_events(self.location, self.t_i, self.t_f, altitude_degrees=0.0)

        # store previous values for after removing overrides
        self.prev_states = {}

        self.spectrum_gen = SpectrumGenerator()

        self.passes, _curr = [], []
        for ti, event in zip(t, events):
            if event == 0:
                _curr.append(ti.utc_datetime().timestamp())
            if event == 2:
                _curr.append(ti.utc_datetime().timestamp())
                self.passes.append(_curr)
                _curr = []

        # start with the initial state argument if available
        if initial_state:
            self.state = initial_state
        # otherwise start with new state
        else:
            self.state = GroundStationState(ts=datetime.fromisoformat(self.scenario.begin).timestamp())

        # update initial state with params defined in the scenario
        if scenario.gs_initial_state:
            for k, v in scenario.gs_initial_state.items():
                self.state.__setattr__(k, v)

        self.lock = threading.Lock()

    def _updates_from_sc_state(self, _state: GroundStationState, sc_state) -> GroundStationState:

        if sc_state: # SNR and state updates on spacecraft side based on GS 
            _state.ul_state = sc_state.ttc_state_ul
            _state.ul_snr = sc_state.ttc_snr_ul
        else:
            _state.ul_state = TTCState.NO_RF
            _state.ul_snr = -128

        return _state

    def _handle_overrides(self, _state: GroundStationState, ov_state: OverrideState) -> GroundStationState:

        if ov_state is not None and ov_state.carrier_ul is not None:
            if 'carrier_ul' not in self.prev_states:
                self.prev_states['carrier_ul'] = _state.carrier_ul
            _state.carrier_ul = ov_state.carrier_ul
        else:
            if 'carrier_ul' in self.prev_states:
                _state.carrier_ul = self.prev_states['carrier_ul']
                del self.prev_states['carrier_ul']

        # handle frame quality
        if ov_state is not None and ov_state.frame_quality is not None:
            if 'frame_quality' not in self.prev_states:
                self.prev_states['frame_quality'] = _state.frame_quality
            _state.frame_quality = ov_state.frame_quality
        else:
            if 'frame_quality' in self.prev_states:
                _state.frame_quality = self.prev_states['frame_quality']
                del self.prev_states['frame_quality']

        return _state

    def _update_tracking(self, _state: GroundStationState, ts: float, sc_state) -> GroundStationState:
        _state.elevation, _state.azimuth, _state.distance, _state.doppler_velocity = None, None, None, None

        if self.state.program_track is True:
            for i in self.passes:
                if i[0] <= ts <= i[1]:
                    difference = self.satellite - self.location
                    dt = datetime.fromtimestamp(ts, tz=pytz.UTC)
                    t = self.time_scale.from_datetime(dt)
                    topocentric = difference.at(t)
                    _state.position = topocentric.position.km
                    alt, az, dist = topocentric.altaz()
                    _, _, _, _, _, velocity = topocentric.frame_latlon_and_rates(self.location)

                    _state.elevation = alt.degrees
                    _state.azimuth = az.degrees
                    _state.distance = dist.km
                    _state.doppler_velocity = velocity.km_per_s * -1.0

                    # update flight dynamics data every 10s
                    if len(_state.position) > 0 and int(ts) % 10 == 0:
                        _reading = _state.position.tolist()
                        if _state.auto_range is True and sc_state.ttc_ranging == Status.enabled:
                            _reading.append(_state.distance)
                        else:
                            _reading.append(0.0)
                        if _state.doppler_enabled is True and sc_state.ttc_coherent == Status.enabled:
                            _reading.append(_state.doppler_velocity)
                        else:
                            _reading.append(0.0)
                        _state.flight_dynamics.append(_reading)

        return _state

    def _next_pass_window(self, _state: GroundStationState, ts: float) -> GroundStationState:
        _state.next_pass_start, _state.next_pass_end = None, None

        for i in self.passes:
            if ts <= i[1]:
                _state.next_pass_start = i[0]
                _state.next_pass_end = i[1]
                break

        return _state

    # calculate D/L snr
    def _calc_snr_dl(self, _state: GroundStationState, sc_state, ov_state: OverrideState) -> GroundStationState:
        _snr_dl = -128

        # handle no_tm override
        #if ov_state and ov_state.no_tm is True:
        #    _snr_dl = -128
        # if spacecraft transmitter is off
        if sc_state.ttc_tx_status == Status.off:
            _snr_dl = -128
        # if spacecraft is below horizon
        elif _state.elevation is None or _state.elevation < 0.0 or _state.distance is None or _state.distance < 0.0:
            _snr_dl = -128
        # no spectrum if bands in s/c and g/s are different
        elif _state.mode.name[0] != sc_state.ttc_mode.name[0]:
            _snr_dl = -128
        # else calculate D/L snr
        else:
            _snr_dl =  -20 * log10(_state.distance) + 68   #+ 3*(TTCModes.SHBR - sc_state.ttc_mode)
            # _snr_dl = -20 * log10(_state.distance) + 68

        # LBSC25 if in X-band + HGA antenna -> no TM + no TC + no spectrum
        if sc_state.ttc_mode.name[0] == 'X' and sc_state.ttc_x_antenna == TTCAntenna.HGA:
            _snr_dl = -128

        # handle max_snr_dl override
        if ov_state and ov_state.max_snr_dl:
            if _snr_dl > ov_state.max_snr_dl is not None:
                _snr_dl = ov_state.max_snr_dl

        _state.snr_dl = _snr_dl

        return _state

    # update D/L status
    def _update_status_dl(self, _state: GroundStationState, sc_state, ov_state : OverrideState) -> GroundStationState:

        # if mode is wrong, status is affected but spectrum isnt
        if _state.mode != sc_state.ttc_mode:
            _state.snr_dl = -128

        _status_dl = TTCState.NO_RF
        # _state.sweep_done = sc_state.sweep_done

        if _state.snr_dl > _state.status_dl_transitions[_state.mode.name]['FRAME_LOCK']:
            _status_dl = TTCState.FRAME_LOCK
        elif _state.snr_dl > _state.status_dl_transitions[_state.mode.name]['BIT_LOCK']:
            _status_dl = TTCState.BIT_LOCK
        elif _state.snr_dl > _state.status_dl_transitions[_state.mode.name]['PLL_LOCK']:
            _status_dl = TTCState.PLL_LOCK

        # handle max_status_dl override
        if ov_state and ov_state.max_status_dl:
            if _status_dl.value > ov_state.max_status_dl.value:
                _status_dl = ov_state.max_status_dl

        # set frame quality to good by default if no override
        if ov_state and ov_state.frame_quality is None:
            if _status_dl == TTCState.FRAME_LOCK:
                _state.frame_quality = Quality.good
            else:
                _state.frame_quality = Quality.unknown

        _state.status_dl = _status_dl

        return _state

    def _update_spectrums(self, _state: GroundStationState, sc_state) -> GroundStationState:

        if _state.carrier_ul == Status.on:
            _freqs, _totals = self.spectrum_gen.uplink_spectrum(_state.mode, power=_state.power_ul)
        else:
            _freqs, _totals = self.spectrum_gen.uplink_spectrum(_state.mode, power=0)
        _ul_f = list(_freqs[np.isfinite(_totals)])
        _ul_p = list(_totals[np.isfinite(_totals)])
        _ul = list(zip(_ul_f, _ul_p))

        _freqs, _totals = self.spectrum_gen.downlink_spectrum(sc_state.ttc_mode, SNR=_state.snr_dl, v_doppler=_state.doppler_velocity, coherent=sc_state.ttc_coherent)
        _dl_f = list(_freqs[np.isfinite(_totals)])
        _dl_p = list(_totals[np.isfinite(_totals)])
        _dl = list(zip(_dl_f, _dl_p))

        _state.spectrum_ul = _ul
        _state.spectrum_dl = _dl

        return _state

    def _update_wrap_up(self, _state : GroundStationState) -> GroundStationState:

        # auto disconnect u/l carrier below 5 elevation
        if _state.carrier_ul == Status.on and _state.elevation and _state.elevation <= 5.0:
            _state.carrier_ul = Status.off

        # reset U/L status
        if _state.elevation is None or _state.elevation <= 0.0:
            _state.ul_state = TTCState.NO_RF
            _state.frame_quality = Quality.unknown

        # reset doppler requires two way PLL
        if int(_state.ul_state) < int(TTCState.PLL_LOCK) or int(_state.status_dl) < int(TTCState.PLL_LOCK):
            _state.doppler_enabled = False

        # reset auto range requires BIT_LOCK
        if int(_state.ul_state) < int(TTCState.BIT_LOCK) or int(_state.status_dl) < int(TTCState.BIT_LOCK):
             _state.auto_range = False

        # reset sweep done
        if _state.ul_snr < -4:
            _state.sweep_done = False

        return _state

    def ping(self, ts : float, sc_state = None, ov_state : OverrideState = None) -> GroundStationState:

        # start the next state from the current state
        _state = copy.deepcopy(self.state)
        _state.ts = ts

        # updates from spacecraft state
        _state = self._updates_from_sc_state(_state, sc_state)

        # handle overrides
        _state = self._handle_overrides(_state, ov_state)

        # update tracking: calculate elevation, azimuth, range (distance) and doppler velocity
        _state = self._update_tracking(_state, ts, sc_state)

        # update next pass window
        _state = self._next_pass_window(_state, ts)

        # calculate D/L snr
        _state = self._calc_snr_dl(_state, sc_state, ov_state)

        # build spectrums
        _state = self._update_spectrums(_state, sc_state)

        # update D/L state
        _state = self._update_status_dl(_state, sc_state, ov_state)

        # updates wrap up
        _state = self._update_wrap_up(_state)

        # update current state
        self.lock.acquire()
        try:
            self.state = _state
        finally:
            self.lock.release()

        # pong
        return self.state

    def _set_state(self, settings):
        self.lock.acquire()
        try:
            for attr, value in settings:
                setattr(self.state, attr, value)
        finally:
            self.lock.release()

    def control(self, data, sc_sim=None):
        _ok = { 'status': 'OK' }
        _fail = { 'status': 'FAIL' }

        if data['control'] == 'carrier_ul':
            if data['value'] in ['on', 'off'] and self.state.elevation >= 5.0:
                self._set_state([('carrier_ul', Status[data['value']])])
                return _ok
            else:
                return _fail

        if data['control'] == 'sweep':
            if self.state.carrier_ul == Status.on and data['value'] is True:
                self._set_state([('sweep_done', True), ('sweep_count', self.state.sweep_count+1 )])
                return _ok
            else:
                return _fail

        if data['control'] == 'power_ul':
            self._set_state([('power_ul', float(data['value']))])
            return _ok

        if data['control'] == 'mode':
            if data['value'] in ['S_Sup_LBR', 'S_Sup_HBR', 'X_Sup_LBR', 'X_Sup_HBR', 'S_Res_LBR', 'X_Res_LBR', 'S_Sub_LBR', 'X_Sub_LBR']:
                sets = [('mode', TTCModes[data['value']])]
                if self.state.mode.name[0] != data['value'][0]:
                    sets.append(('sweep_done', False))
                self._set_state(sets)
                return _ok
            else:
                return _fail
        
        if data['control'] == 'auto_track':
            if isinstance(data['value'], bool):
                self._set_state([('auto_track', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'program_track':
            if isinstance(data['value'], bool):
                self._set_state([('program_track', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'auto_range':
            if isinstance(data['value'], bool):
                self._set_state([('auto_range', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'doppler_enabled':
            if isinstance(data['value'], bool):
                self._set_state([('doppler_enabled', data['value'])])
                return _ok
            else:
                return _fail

        if data['control'] == 'frame_checks':
            if data['value'] == 'enabled':
                self._set_state([('frame_checks', Status[data['value']])])
                return _ok
            elif data['value'] == 'disabled':
                self._set_state([('frame_checks', Status[data['value']])])
                return _ok
            else:
                return _fail

        return _fail


# spectrums generator
class SpectrumGenerator:
    def __init__(self, SPECTRUMSIZE : int = 200, BW : int = 20) -> None:
        self.SPECTRUMSIZE = SPECTRUMSIZE
        self.BW = BW

        self.turnaroundRatios = {
            #UL/DL
            "SS" : 240/221,
            "SX" : 880/221,
            "XS" : 240/749,
            "XX" : 880/749,
            "XKa" : 3344/749,
            "KaX" : 880/3599,
            "KaKa" : 3360/3599
        }

        self.modeParameters = {
            TTCModes.S_Sup_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 1e6,
                "band" : "SS",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.S_Sup_HBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 2e6,
                "band" : "SS",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.X_Sup_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 3e6,
                "band" : "SX",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.X_Sup_HBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 4e6,
                "band" : "SX",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.S_Res_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 1e6,
                "band" : "SS",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.X_Res_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 3e6,
                "band" : "SX",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.S_Sub_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 1e6,
                "band" : "SS",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            },
            TTCModes.X_Sub_LBR:{
                "ul_bw" : 256e3,
                "dl_bw" : 3e6,
                "band" : "SX",
                "up_freq": 2053.136,
                "ul_mod_idx": 0.5
            }
        }

    def _RC_filter(self, f, roll_off, bw):
        return 0.5*(1+cos(pi/bw/roll_off*(abs(f)-(1-roll_off)*bw/2)))

    def _lin2db(self, x):
        return 10*log10(x)

    def _db2lin(self, x):
        return 10**(x/10)
    
    def _NRZ_PM(self, mode: str, bw, frequencies, cf, mod_idx = 0.7):
        if mode == 'Sub': #NRZ/PSK/PM, subcarrier
            bw = bw/16
            P = lambda x: sinc(x/bw)/bw
            S = lambda x: bw/4*(P(x+4*bw)**2+P(x-4*bw)**2)
        elif mode == 'Res': #SP-L/PM
            bw = bw/4
            P = lambda x: sinc(x/bw)/bw
            S = lambda x: bw/4*(P(x+bw)**2+P(x-bw)**2)
        else: #NRZ-L/PM
            bw = bw/2
            P = lambda x: sinc(x/bw)/bw
            S = lambda x: bw/4*(P(x)**2)

        carrier_idx = min(range(len(frequencies)), key=lambda i: abs(frequencies[i]-cf))
        carrier = 1e-12*np.ones(self.SPECTRUMSIZE)
        carrier[carrier_idx] = 10*np.cos(mod_idx)**2 # 10 is just a factor, should be ref_bw/freq_step

        signal = np.array([S(f-cf) for f in frequencies])
        signal = np.sin(mod_idx)**2*signal + carrier
        return signal

    
    def _PSK(self, bw, frequencies, cf, roll_off = 0.4):
        spectrum_low = cf - self.BW/2
        spectrum_high = cf + self.BW/2
        #maybe make this constant until mode changes
        freq = [spectrum_low,-bw/2*(1+roll_off)+cf, -bw/2*(1-roll_off)+cf, bw/2*(1-roll_off)+cf, bw/2*(1+roll_off)+cf, spectrum_high]
        signal = np.piecewise(frequencies, [frequencies<freq[1], (frequencies>=freq[1]) & (frequencies<freq[2]), (frequencies>=freq[2]) & (frequencies<freq[3]), (frequencies>=freq[3]) & (frequencies<freq[4]), frequencies>=freq[4] ], 
                                        [0, lambda x: self._RC_filter(x-cf, roll_off, bw), 1, lambda x: self._RC_filter(x-cf, roll_off, bw), 0])
        return signal

    def downlink_spectrum(self, mode : TTCModes, v_doppler = 0, SNR = 5, _interference = False, coherent = False):
        #Frequency span of Spectrum
        zoom = 4
        spectrum_center = self.modeParameters[mode]["up_freq"]*self.turnaroundRatios[self.modeParameters[mode]["band"]]
        spectrum_low = spectrum_center - self.BW/2/zoom
        spectrum_high = spectrum_center + self.BW/2/zoom
        frequencies = np.linspace(spectrum_low, spectrum_high, self.SPECTRUMSIZE)

        # FIXME
        if v_doppler is None:
            v_doppler = 0

        #values that go to deep to explain
        noise_level = -110
        #fixed by mode
        c = 3e8

        doppler = 1+v_doppler*1000/c
        bw = self.modeParameters[mode]["dl_bw"]/1e6
        cf = self.modeParameters[mode]["up_freq"]*self.turnaroundRatios[self.modeParameters[mode]["band"]] * doppler
        if coherent:
            cf = cf *doppler
        modename = mode.name[2:5]
        if modename == 'Sup':
            signal = self._db2lin(SNR)*self._PSK(bw, frequencies, cf)
        else:
            signal = self._db2lin(SNR)*self._NRZ_PM(modename, bw, frequencies, cf)

        noise = abs(np.random.normal(1, 0.2, self.SPECTRUMSIZE))
        interference = np.piecewise(frequencies, [frequencies<cf*1.01, frequencies<cf*1.02, frequencies<spectrum_high], [0, 1, 0]) if _interference else 0

        total = self._lin2db(signal+noise+interference) + noise_level

        return [frequencies, total]

    def uplink_spectrum(self, mode : TTCModes, power = 53, SNR = 20, noisefloor = 10):
        #Frequency span of Spectrum
        zoom = 16
        bw = self.modeParameters[mode]["ul_bw"]/1e6
        spectrum_center = self.modeParameters[mode]["up_freq"] # center frequency of the spectrum analyzer
        spectrum_low = spectrum_center - self.BW/2/zoom
        spectrum_high = spectrum_center + self.BW/2/zoom
        frequencies = np.linspace(spectrum_low, spectrum_high, self.SPECTRUMSIZE)


        mod_idx = self.modeParameters[mode]["ul_mod_idx"]
        cf = self.modeParameters[mode]["up_freq"] # center frequency of the signal
        noise = self._db2lin(-SNR)*abs(np.random.normal(0, 0.5, self.SPECTRUMSIZE)) + self._db2lin(noisefloor-power)*abs(np.random.normal(0, 0.2, self.SPECTRUMSIZE))
        signal = self._NRZ_PM('Res', bw, frequencies, cf, mod_idx)
        total = power + self._lin2db( noise + signal)

        return [frequencies, total]
