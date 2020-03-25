import socketio
from timebomb.socket import MainNamespace

sio = socketio.Server(async_mode="eventlet")

sio.register_namespace(MainNamespace("/"))

app = socketio.WSGIApp(sio)
