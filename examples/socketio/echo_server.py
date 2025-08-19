# Used by socketio_ex.py as a mock target. Requires installing gevent-websocket
import gevent.monkey

gevent.monkey.patch_all()
import time

import socketio
from flask import Flask
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# Create a Socket.IO server
sio = socketio.Server(async_mode="gevent")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

DELAY = 0.01


# When a client connects
@sio.event
def connect(sid, environ):
    time.sleep(DELAY)
    print(f"Client connected: {sid}")


# Join a room
@sio.event
def join_room(sid, data):
    time.sleep(DELAY)
    room = data.get("room")
    sio.enter_room(sid, room)
    print(f"Client {sid} joined room {room}")
    # Optionally notify the room
    sio.emit("room_joined", f"{sid} joined {room}", room=room)
    return f"Joined room {room}"


# Leave a room
@sio.event
def leave_room(sid, data):
    time.sleep(DELAY)
    room = data.get("room")
    sio.leave_room(sid, room)
    print(f"Client {sid} left room {room}")


# Broadcast message to a room
@sio.event
def send_message(sid, data):
    time.sleep(DELAY)
    room = data.get("room")
    msg = data.get("message")
    print(f"Sent message ({msg} to room {room}")
    sio.emit("chat_message", msg, room=room)


# When a client disconnects
@sio.event
def disconnect(sid):
    time.sleep(DELAY)
    print(f"Client disconnected: {sid}")


server = pywsgi.WSGIServer(("0.0.0.0", 5001), app, handler_class=WebSocketHandler)
server.serve_forever()
