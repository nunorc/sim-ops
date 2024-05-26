
import os, sys, json, zmq

CONTROL_TCP = os.getenv('SO_CONTROL_TCP', 'tcp://so-master:5555')
if not CONTROL_TCP:
    CONTROL_TCP = 'tcp://so-master:5555'

n = len(sys.argv)
if n == 4:
    system = sys.argv[-3]
    control = sys.argv[-2]
    value = sys.argv[-1]
    if value.lower().strip() == 'false':
        value = False
    elif value.lower().strip() == 'true':
        value = True
    else:
        pass

data = { 'system': system, 'control': control, 'value': value }

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(CONTROL_TCP)

if control:
    data = { 'system': system, 'control': control, 'value': value, 'admin': True }
    
    socket.send_json(json.dumps(data))
    message = socket.recv_json()

    print(message)

socket.close()
