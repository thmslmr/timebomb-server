import socketio
from flask import Flask, request, jsonify
import sys

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

    print(f"Login with infos: {sid} - {username} - {roomname}")
    sys.stdout.flush()

    entered_room = arena.join_room(new_player, roomname)

    if entered_room:
        sio.enter_room(sid, entered_room.name)
        room_state_message(entered_room)

        print(f"Room state: {entered_room.state}")
        sys.stdout.flush()

        return jsonify(entered_room.state)
    else:
        return jsonify({"error": "Room is busy"})


@app.route("/cut", methods=["POST"])
def cut():
    src_sid = request.form["src"]
    dst_sid = request.form["dst"]

    src_player = arena.get_player(src_sid)
    dst_player = arena.get_player(dst_sid)

    if not (src_player and dst_player):
        return jsonify({"error": "Unknown player"})

    roomname = src_player.roomname
    room = arena.get_room(roomname)

    if not room:
        return jsonify({"error": "Unknown room"})

    card = room.cut_card(src_player, dst_player)

    if card:
        message = (
            f"{src_player.name} cut {dst_player.name}'s card and discover a {card}"
        )
        print(message)
        sys.stdout.flush()

        if sum(room.left.values()) % len(room.players) == 0:
            room.set_hands()
            for player in room.players:
                room_state_message(room)
                player_state_message(player)
        else:
            room_state_message(room)
            player_state_message(dst_player)

        bot = Player("", 0)
        chat_message(bot, message, room)

        return jsonify({"data": f"Cut card {card}"})
    else:
        return jsonify({"error": "Unable to cut a card"})


@app.route("/start", methods=["POST"])
def start():
    roomname = request.form["roomname"]
    room = arena.get_room(roomname)

    if room is None:
        return jsonify({"error": "Room does not exist."})

    if room.status != "READY":
        return jsonify({"error": "Game not ready to start."})

    room.start()
    sys.stdout.flush()

    room_state_message(room)

    for player in room.players:
        player_state_message(player)

    message = f"Game start ! The following role has been distribute."
    print(message)
    sys.stdout.flush()

    bot = Player("", 0)
    chat_message(bot, message, room)

    return jsonify({"data": "Game start."})


def room_state_message(room, **kwargs):
    sio.emit("room_state", room.state, room=room.name, **kwargs)


def chat_message(player, content, room):
    data = {"src": player.name, "content": content}
    sio.emit("chat_message", data, room=room.name)


def player_state_message(player):
    data = player.private_state
    print(f"Player state {data}")
    sys.stdout.flush()
    sio.emit("player_state", data, room=player.sid)


@sio.on("chat_message")
def chat_event(sid, data):
    for room in arena.rooms:

        player = room.get_player(sid)

        if player is not None:
            sys.stdout.flush()
            chat_message(player, data["content"], room)


@sio.event
def connect(sid, environ):
    print(f"Player connect : {sid}")
    sys.stdout.flush()

    data = {"sid": sid}
    sio.emit("connection", data, room=sid)


@sio.event
def disconnect(sid):
    print(f"Player disconnected : {sid}")
    sys.stdout.flush()

    for room in arena.rooms:
        player = room.get_player(sid)

        if player:
            sio.leave_room(sid, room.name)
            room.players.remove(player)

            if len(room.players) == 0:
                arena.rooms.remove(room)
            else:
                room_state_message(room)


app = socketio.WSGIApp(sio, app)
