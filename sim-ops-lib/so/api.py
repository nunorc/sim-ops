
import os, sys, json, zmq
sys.path.insert(0, '')

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

CONTROL_TCP = os.getenv('SO_CONTROL_TCP', 'tcp://so-master:5555')
if not CONTROL_TCP:
    CONTROL_TCP = 'tcp://so-master:5555'
MCS_ADMIN_PW = os.getenv('SO_MCS_ADMIN_PASSWORD', 'admin')
if not MCS_ADMIN_PW:
    MCS_ADMIN_PW = 'admin'

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
def _admin_status(admin_pw: str):
    if _valid_auth(admin_pw):
        return _control({ 'system': 'admin', 'control': 'status', 'value': 'null' })
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth:'+MCS_ADMIN_PW)

@app.post('/admin', status_code=200)
async def _admin(admin_pw: str, request: Request):
    if _valid_auth(admin_pw):
        body = await request.json()
        return _control(body)
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth.')

@app.post('/control', status_code=200)
async def _ground_stations_control(admin_pw: str, request: Request):
    if _valid_auth(admin_pw):
        body = await request.json()
        return _control(body)
    else:
        raise HTTPException(status_code=405, detail='Requires admin auth.')

@app.get('/admin/hist')
def _control_hist():
    result = _control({ 'system': 'admin', 'control': 'history', 'value': 'null' })

    return result
