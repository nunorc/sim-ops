
import os, json, zmq
from dataclasses import dataclass, asdict
from enum import Enum
from scipy.spatial.transform import Rotation
from numpy import degrees, ndarray
from skyfield.toposlib import GeographicPosition
from skyfield.positionlib import Geocentric
from typing import Any

from .mqtt import MQTT

class Status(int, Enum):
    enabled = 1
    disabled = 2
    unkown = 3
    nominal = 4
    safe = 5
    on = 6
    off = 7
    not_valid = 8
    valid = 9

class TTCModes(int, Enum):
    # antenna configuration
    SLBR = 1
    SHBR = 2
    XLBR = 3
    XHBR = 4

class AOCSTarget(Enum):
    SUN = 1
    TARGET = 2
    NADIR = 3
    RATEDAMPING = 4
    MONITORING = 5

class TTCState(int, Enum):
    NO_RF = 1
    PLL_LOCK = 2
    PSK_LOCK = 3
    BIT_LOCK = 4
    FRAME_LOCK = 5

@dataclass
class GroundStation:
    name: str
    latitude: float
    longitude: float
    altitude: float

@dataclass
class Scenario:
    name: str = ''
    begin: str = ''
    end: str = ''
    tle: str = ''
    time_step: int = 5
    running: bool = False
    ground_station: GroundStation = None
    gs_initial_state: Any = None
    sc_initial_state: Any = None 

# load scenario from file
def load_scenario(uid):
    filename = os.path.join('data', 'scenarios', uid, 'data.json')

    if os.path.exists(filename):
        with open(filename, 'r') as fin:
            data = json.load(fin)

            gs_initial_state, sc_initial_state = None, None

            gs = GroundStation(**data['ground_station'])
            del data['ground_station']

            if 'gs_initial_state' in data:

                # handle Status enum
                if 'carrier_ul' in data['gs_initial_state']:
                    data['gs_initial_state']['carrier_ul'] = Status[data['gs_initial_state']['carrier_ul']]

                # handle TTCModes enum
                if 'mode' in data['gs_initial_state']:
                    data['gs_initial_state']['mode'] = TTCModes[data['gs_initial_state']['mode']]

                # FIXME: handle all other enums

            if 'sc_initial_state' in data:

                # handle Status enum
                for k in ['ttc_tx_status', 'pl_gps_status', 'pl_camera_status', 'dhs_obsw_mode', 'pts_sol_array']:
                    if k in data['sc_initial_state']:
                        if isinstance(data['sc_initial_state'][k], list):
                            data['sc_initial_state'][k] = [Status[x] for x in data['sc_initial_state'][k]]
                        else:
                            data['sc_initial_state'][k] = Status[data['sc_initial_state'][k]]

                # handle AOCSTarget enum
                if 'aocs_mode' in data['sc_initial_state']:
                    data['sc_initial_state']['aocs_mode'] = AOCSTarget[data['sc_initial_state']['aocs_mode']]

                # handle TTCMode
                if 'ttc_mode' in data['sc_initial_state']:
                    data['sc_initial_state']['ttc_mode'] = TTCModes[data['sc_initial_state']['ttc_mode']]

                # FIXME: handle all other enums

            scenario = Scenario(**data)
            scenario.ground_station = gs
            if gs_initial_state:
                scenario.gs_initial_state = gs_initial_state
            if sc_initial_state:
                scenario.sc_initial_state = sc_initial_state

            return scenario

class Backend:
    def __init__(self, scenario):
        self.scenario = scenario

        self.mqtt = MQTT()

    def publish(self, topic, data):

        self.mqtt.publish(topic, data)

        return True

# return enum types names instead of values (numbers)
def custom_dict_factory(kv_pairs):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, Rotation):
            return list(degrees(obj.as_rotvec()))
        elif isinstance(obj, GeographicPosition):
            return [obj.latitude.degrees, obj.longitude.degrees, obj.elevation.km]
        elif isinstance(obj, list):
            return [convert_value(x) for x in obj]
        elif isinstance(obj, Geocentric):
            return list(obj.position.km)
        elif isinstance(obj, ndarray):
            return list(obj)
        else:
            return obj

    return dict((k, convert_value(v)) for k, v in kv_pairs)

@dataclass
class OverrideState:
    max_status_dl: str = None
    max_snr_dl: float = None
    gps_status: Status = None
    camera_status: Status = None
    tx_status: Status = None
    carrier_ul: Status = None
    no_tm: bool = None
    no_tc: bool = None
    no_uploads: bool = None

    def has(self, attr):
        return hasattr(self, attr)

    def update(self, attr, value):
        if attr == '_unset':
            self.__setattr__(value, None)
            return True

        match attr:
            case 'max_status_dl':
                self.max_status_dl = TTCState[value]
                return True
            case 'max_snr_dl':
                self.max_snr_dl = float(value)
                return True
            case 'carrier_ul':
                self.carrier_ul = Status[value]
                return True
            case 'tx_status':
                self.tx_status = Status[value]
                return True
            case 'no_tm':
                self.no_tm = value.lower().strip() == 'enabled'
                return True
            case 'no_tc':
                self.no_tc = value.lower().strip() == 'enabled'
                return True
            case 'no_uploads':
                self.no_uploads = value.lower().strip() == 'enabled'
                return True
            case other:
                return False

    def current(self):
        return [(k, v) for (k,v)in asdict(self, dict_factory=custom_dict_factory).items() if v is not None]
