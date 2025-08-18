# Used by socketio_ex.py as a mock target
import socketio
from flask import Flask

# Create a Socket.IO server
sio = socketio.Server()
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)


# When a client connects
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")


# Join a room
@sio.event
def join_room(sid, data):
    room = data.get("room")
    sio.enter_room(sid, room)
    print(f"Client {sid} joined room {room}")
    # Optionally notify the room
    sio.emit("room_joined", f"{sid} joined {room}", room=room)
    return f"Joined room {room}"


# Leave a room
@sio.event
def leave_room(sid, data):
    room = data.get("room")
    sio.leave_room(sid, room)
    print(f"Client {sid} left room {room}")


# Broadcast message to a room
@sio.event
def send_message(sid, data):
    room = data.get("room")
    msg = data.get("message")
    print(f"Sent message ({msg} to room {room}")
    sio.emit("chat_message", msg, room=room)


# When a client disconnects
@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")


if __name__ == "__main__":
    import eventlet

    eventlet.wsgi.server(eventlet.listen(("localhost", 5001)), app)
