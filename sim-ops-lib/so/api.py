
import os, sys, json, zmq, subprocess
sys.path.insert(0, '')

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core import ObjectStore
from .spacecraft import SpacePacketHandler

CONTROL_TCP = os.getenv('SO_CONTROL_TCP', 'tcp://so-master:5555')
if not CONTROL_TCP:
    CONTROL_TCP = 'tcp://so-master:5555'
MCS_ADMIN_PW = os.getenv('SO_MCS_ADMIN_PASSWORD', 'admin')
if not MCS_ADMIN_PW:
    MCS_ADMIN_PW = 'admin'

OBJ_STORE = ObjectStore()
SPH = SpacePacketHandler()

app = FastAPI(title = 'so-api',  version = 'v0.0.1')
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

def _control(data):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 seconds timeout

    try:
        socket.connect(CONTROL_TCP)
        socket.send_json(json.dumps(data))
        result = socket.recv_json()
    except:
        result = { 'status': 'FAIL' }

    socket.close()

    return result

def _valid_auth(admin_pw):
    return MCS_ADMIN_PW == admin_pw

@app.get('/')
def _root():
    return { 'title': app.title, 'version': app.version }

@app.get('/admin/status', status_code=200)
def _get_admin_status(admin_pw: str):
    if _valid_auth(admin_pw):
        return _control({ 'system': 'admin', 'control': 'status', 'value': 'null' })
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth.')

@app.post('/admin', status_code=200)
async def _post_admin(admin_pw: str, request: Request):
    if _valid_auth(admin_pw):
        body = await request.json()
        return _control(body)
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth.')

@app.post('/control')
async def _post_control(request: Request):
    body = await request.json()
    result = _control(body)

    return result

@app.get('/admin/hist')
def _get_Admin_hist():
    result = _control({ 'system': 'admin', 'control': 'history', 'value': 'null' })

    return result

@app.get('/admin/trigger/{trigger}', status_code=200)
def _admin_trigger(trigger: str, admin_pw: str):
    if _valid_auth(admin_pw):
        filename = os.path.join('data', 'triggers', f'{trigger}.py')
        if os.path.exists(filename):
            subprocess.run([sys.executable, filename])
            return {'status': 'OK' }
        else:
            print('filename not found')
            return {'status': 'FAIL' }
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth.')

@app.get('/obj-store/tm')
def _os_get_tm():
    return OBJ_STORE.get_objects_tm()

@app.get('/obj-store/fd')
def _os_get_fd():
    return OBJ_STORE.get_objects_fd()

@app.get('/obj-store/set/{uid}/{key}/{value}', status_code=200)
def _os_set(uid: str, key: str, value: str):
    # FIXME coerce to correct types
    if key == 'status':
        value = int(value)

    data = OBJ_STORE.update_object('flight-dynamics', uid, key, value)

    return data

@app.get('/obj-store/sp/{bucket}/{object_name}')
def _os_tm_by_uid(bucket: str, object_name: str):
    bytes = OBJ_STORE.get(bucket, object_name)
    packet = SPH.from_bytestream(bytes)

    return SPH.as_dict(packet, post_proc=False)

