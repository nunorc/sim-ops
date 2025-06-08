
import os, json, zmq
from dataclasses import dataclass, asdict
from enum import Enum
from scipy.spatial.transform import Rotation
from numpy import degrees, ndarray
from skyfield.toposlib import GeographicPosition
from skyfield.positionlib import Geocentric
from typing import Any
from minio import Minio
from io import BytesIO

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
    error = 10

class Quality(int, Enum):
    good = 1
    bad = 2
    unknown = 3

class TTCModes(int, Enum):
    S_Sup_LBR = 1
    S_Sup_HBR = 2
    X_Sup_LBR = 3
    X_Sup_HBR = 4
    S_Res_LBR = 5
    X_Res_LBR = 6
    S_Sub_LBR = 7
    X_Sub_LBR = 8


class TTCAntenna(int, Enum):
    LGA_RHC = 1
    LGA_LHC = 2
    MGA = 3
    HGA = 4

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
    time_step: int = 1
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
                for k in ['ttc_tx_status', 'pl_gps_status', 'pl_camera_status', 'dhs_obsw_mode', 'eps_sol_array', 'obc_mode', 'ttc_obc']:
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

DEFAULT_STATUS_DL_TRANSITIONS = {
    'S_Sup_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 1.2, 'FRAME_LOCK': 1.7 },
    'S_Sup_HBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 1.2, 'FRAME_LOCK': 1.7 },
    'X_Sup_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 1.0, 'FRAME_LOCK': 1.5 },
    'X_Sup_HBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 1.0, 'FRAME_LOCK': 1.5 },
    'S_Res_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 0.7, 'FRAME_LOCK': 1.2 },
    'X_Res_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 0.7, 'FRAME_LOCK': 1.2 },
    'S_Sub_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 0.3, 'FRAME_LOCK': 0.8 },
    'X_Sub_LBR': { 'PLL_LOCK': -0.5, 'BIT_LOCK': 0.3, 'FRAME_LOCK': 0.8 }
}


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
    frame_quality: Quality = None

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
            case 'frame_quality':
                self.frame_quality = Quality[value]
                return True
            case other:
                return False

    def current(self):
        return [(k, v) for (k,v)in asdict(self, dict_factory=custom_dict_factory).items() if v is not None]

HPTC = ['TC_TTC_001', 'TC_TTC_002', 'TC_TTC_003', 'TC_TTC_004', 'TC_TTC_022', 'TC_TTC_023',
        'TC_TTC_031', 'TC_TTC_032', 'TC_TTC_041', 'TC_TTC_051', 'TC_TTC_052', 'TC_TTC_053', 'TC_TTC_061', 'TC_TTC_062']

SO_MINIO_ENDPOINT = os.getenv('SO_MINIO_ENDPOINT', 'so-minio:9000')
if not SO_MINIO_ENDPOINT:
    SO_MINIO_ENDPOINT = 'so-minio:9000'
SO_MINIO_ROOT_USER = os.getenv('SO_MINIO_ROOT_USER', 'myusername')
if not SO_MINIO_ROOT_USER:
    SO_MINIO_ROOT_USER = 'myusername'
SO_MINIO_ROOT_PASSWORD = os.getenv('SO_MINIO_ROOT_PASSWORD', 'mypassword')
if not SO_MINIO_ROOT_PASSWORD:
    SO_MINIO_ROOT_PASSWORD = 'mypassword'

class ObjectStore:
    def __init__(self, endpoint=SO_MINIO_ENDPOINT, access_key=SO_MINIO_ROOT_USER, secret_key=SO_MINIO_ROOT_PASSWORD):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

        self.client = Minio(self.endpoint, access_key=self.access_key, secret_key=self.secret_key, secure=False)

    # store space packet tm
    def store(self, bucket, packet_id, byte_stream):
        # create bucket if does not exist
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

        data = BytesIO(byte_stream)

        self.client.put_object(bucket_name=bucket, object_name=packet_id, data=data, length=len(byte_stream))

    def get_objects_tm(self):
        buckets = [x.name for x in self.client.list_buckets()]

        data = []
        for bucket in buckets:
            if bucket.startswith('sim-') and bucket.endswith('-tm'):
                objects = self.client.list_objects(bucket)
                data.append({ 'bucket': bucket, 'data': [x.object_name for x in objects] })

        return data

    # retrieve objects with flight dynamics products
    def get_objects_fd(self):
        if not self.client.bucket_exists('flight-dynamics'):
            return []

        objects = self.client.list_objects('flight-dynamics')

        data = []
        for object in objects:
            response = self.client.get_object('flight-dynamics', object.object_name)
            data.append(response.json())
        data.reverse()

        return data

    def get(self, bucket, object_name, is_json=False):
        response = self.client.get_object(bucket, object_name)

        if is_json:
            data = response.json()
        else:
            data = response.read()

        return data

    def update_object(self, bucket, object_name, key, value):
        response = self.client.get_object(bucket, object_name)
        data = response.json()
        if key in data:
            data[key] = value

        self.store(bucket, object_name, json.dumps(data).encode())

        return data

class Products:
    def __init__(self, object_store: ObjectStore = ObjectStore()):
        self.object_store = object_store

    def fd_start_sim(self):
        objects = self.object_store.get_objects_fd()

        for object in objects:
            if object['status'] == 1:
                if object['validity'] > 0:
                    self.object_store.update_object('flight-dynamics', object['id'], 'status', 2)
                else:
                    self.object_store.update_object('flight-dynamics', object['id'], 'status', -1)

    def fd_stop_sim(self, sim_uid, gs_state):
        _doppler = any([x[-2] for x in gs_state.flight_dynamics])
        _ranging = any([x[-1] for x in gs_state.flight_dynamics])

        if _doppler and _ranging:
            _validity = 2
        elif _doppler or _ranging:
            _validity = 1
        else:
            _validity = 0

        data = { 'id': sim_uid, 'status': 0, 'validity': _validity, 'data': gs_state.flight_dynamics }
        self.object_store.store('flight-dynamics', sim_uid, json.dumps(data).encode())

        return data
