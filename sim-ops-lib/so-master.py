
import os, threading, time, json, logging, zmq, copy, glob
from datetime import datetime

from so.core import load_scenario, Backend, OverrideState, Status
from so.ground_station import GroundStationSim
from so.spacecraft import SpacecraftSim

logger = logging.getLogger(__name__)

# globals
SCENARIO, GS_SIM, SC_SIM, BACKEND, END_SIM = None, None, None, None, None
LAST_GS_STATE, LAST_SC_STATE = None, None
CONTROL_HIST = []
OV_STATE = OverrideState()

def sim_loop():
    logger.info('Starting sim loop')

    ts = datetime.fromisoformat(SCENARIO.begin).timestamp()
    while not END_SIM.is_set():
        start = time.time()
        logger.info(f"sim loop ping! ts: {ts} dt: {str(datetime.utcfromtimestamp(ts))}")

        gs_state = GS_SIM.ping(ts, sc_state=SC_SIM.state, ov_state=OV_STATE)
        if gs_state:
            BACKEND.publish('ground_station', gs_state.to_dict())

        sc_state = SC_SIM.ping(ts, gs_state=gs_state, ov_state=OV_STATE)
        if sc_state:
            BACKEND.publish('spacecraft', sc_state.to_dict())

        end = time.time()
        delta = SCENARIO.time_step - (end - start)

        ts += delta
        time.sleep(delta)

def start_sim(uid):
    logger.info(f"Starting sim { uid }")

    global SCENARIO, GS_SIM, SC_SIM, BACKEND, END_SIM, LAST_GS_STATE, LAST_SC_STATE
    END_SIM = threading.Event()

    SCENARIO = load_scenario(uid)
    GS_SIM = GroundStationSim(SCENARIO, initial_state=LAST_GS_STATE)
    SC_SIM = SpacecraftSim(SCENARIO, initial_state=LAST_SC_STATE)
    BACKEND = Backend(SCENARIO)

    t = threading.Thread(target=sim_loop)
    t.start()

def stop_sim():
    logger.info(f"Stopping sim")

    global END_SIM, GS_SIM, SC_SIM, LAST_GS_STATE, LAST_SC_STATE, CONTROL_HIST
    if END_SIM == None or SCENARIO == None or GS_SIM == None or SC_SIM == None:
        logger.info("No sim running")
        return
    END_SIM.set()

    logger.info('Storing current ground station and spacecraft state')
    LAST_GS_STATE = copy.deepcopy(GS_SIM.state) if GS_SIM else None
    LAST_SC_STATE = copy.deepcopy(SC_SIM.state) if SC_SIM else None

    # save control history to file and reset
    _path, _now = os.path.join('data', 'hist'), int(datetime.utcnow().timestamp())
    if not os.path.exists(_path):
        os.makedirs(_path)
    with open(os.path.join(_path, f"{ str(_now) }.json"), 'w') as fout:
        json.dump(CONTROL_HIST, fout)
    CONTROL_HIST = []

def _log_control(data, result, ts):
    global CONTROL_HIST

    data['result'] = result['status']
    data['ts'] = ts

    if 'admin' in data and data['admin'] is True:
        pass # FIXME log admin
    else:
        CONTROL_HIST.append(data)

def _get_history():
    _path = os.path.join('data', 'hist')

    if os.path.exists(_path):
        _filenames = sorted(glob.glob(os.path.join(_path, '*.json')), reverse=True)
    else:
        _filenames = []

    result = []
    for _filename in _filenames:
        with open(_filename, 'r') as fin:
            curr = json.load(fin)
            result.append([int(_filename.split('/')[-1].split('.')[0]), curr])

    return result

def _get_scenarios_data(scenarios):
    data = {}

    for scenario in scenarios:
        with open(os.path.join('data', 'scenarios', scenario, 'data.json'), 'r') as fin:
            data[scenario] = json.load(fin)

    return data

def control_loop():
    logger.info('Starting control loop')

    global GS_SIM, SC_SIM, OV_STATE

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:5555')

    while True:
        message = socket.recv_json()  # wait for next message

        data = json.loads(message)
        logger.info(f"Received control command: { data }")

        _ok, _fail = { 'status': 'OK' }, { 'status': 'FAIL'}
        _admin = False
        if 'admin' in data:
            _admin = data['admin']

        # handle spacecraft controls
        if 'system' in data and data['system'] == 'spacecraft':
            _fail = { 'status': 'r:REL r:ACC r:FAIL'}

            # need at least ground station U/L carrier enabled to send command
            if _admin is False and (GS_SIM is None or GS_SIM.state.carrier_ul is None or GS_SIM.state.carrier_ul == Status.off):
                result = { 'status': 'r:REL r:ACC r:FAIL'}
                _ts = GS_SIM.state.ts
            elif GS_SIM.state.power_ul < 50:
                result = { 'status': 'g:REL r:ACC r:FAIL'}
                _ts = GS_SIM.state.ts
            else:
                try:
                    if OV_STATE.no_tc is not True:
                        result = SC_SIM.control(data, ov_state=OV_STATE, admin=_admin)
                        SC_SIM.tc_history(data, result)
                        _ts = SC_SIM.state.ts
                    else:
                        # FIXME result for no TC override
                        result = { 'status': 'g:REL w:ACC w:UNK'}
                        _ts = SC_SIM.state.ts
                except:
                    logger.error(f"Failed spacecraft command: { data }")
                    result = _fail
            _log_control(data, result, _ts)

        # handle ground station control
        elif 'system' in data and data['system'] == 'ground_station':

            try:
                result = GS_SIM.control(data, sc_sim=SC_SIM)
                _ts = GS_SIM.state.ts
                _log_control(data, result, _ts)
            except:
                logger.error(f"Failed ground station command: { data }")
                result = _fail

        # handle admin control
        elif 'system' in data and data['system'] == 'admin':
            result = _ok

            match data['control']:
                case 'start':
                    start_sim(data['value'])
                case 'stop':
                    stop_sim()
                case 'status':
                    result['scenarios'] = sorted(os.listdir(os.path.join('data', 'scenarios')))
                    result['data'] = _get_scenarios_data(result['scenarios'])
                    result['running'] = not END_SIM.is_set() if END_SIM else False
                    result['name'] = SCENARIO.name if SCENARIO else ''
                    result['overrides'] = OV_STATE.current()
                case 'history':
                    result = _get_history()
                case other:
                    result = _fail

        # handle overrides
        elif 'system' in data and data['system'] == 'override':
            if data['value'] is None or len(data['value']) == 0:
                result = _fail
            else:
                if OV_STATE.update(data['control'], data['value']):
                    result = { 'status': 'OK' }
                else:
                    result = _fail
        else:
            result = _fail

        socket.send_json(result)

if __name__ == '__main__':

    # start control loop
    t = threading.Thread(target=control_loop)
    t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
