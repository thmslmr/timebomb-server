import socketio
from flask import Flask, request, jsonify

from timebomb.model.arena import Arena
from timebomb.model.player import Player

sio = socketio.Server(async_mode="eventlet")
app = Flask(__name__)

arena = Arena()


@app.route("/")
def index():
    return f"You've reach a time bomb server."


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    sid = request.form["sid"]

    new_player = Player(username, sid)
    roomname = request.form["roomname"]

    entered_room = arena.join_room(new_player, roomname)

    if entered_room:
        sio.enter_room(sid, entered_room.name)
        room_state_message(entered_room)

        return jsonify({"data": "wellconnected"})
    else:
        return jsonify({"data": "Room is busy"})


def room_state_message(room):
    sio.emit("room_stat", {"data": room.state}, room=room.name)


@sio.on("my_broadcast_event")
def test_broadcast_message(sid, message):
    print(f"New message from {sid}")
    sio.emit("my_response", {"data": message["data"]})


@sio.on("ping")
def ping_message(sid, message):
    sio.emit("my_response", {"data": sid})


app = socketio.WSGIApp(sio, app)
