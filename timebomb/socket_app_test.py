import multiprocessing

import socketio
import eventlet
from pytest import fixture

from timebomb.socket_app import MainNamespace


# @fixture(autouse=True)
def create_server():
    sioserver = socketio.Server(async_mode="eventlet")
    sioserver.register_namespace(MainNamespace("/"))
    app = socketio.WSGIApp(sioserver)

    def daemon_server():
        eventlet.wsgi.server(
            eventlet.listen(("localhost", 5000)), app, log_output=False
        )

    d = multiprocessing.Process(name="test-server", target=daemon_server)
    d.daemon = True
    d.start()
    return d


create_server()


def test_MainNamespace_login():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Invalid username."}

    client.emit("login", {}, callback=callback)

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert room["cards_left"] == room["cards_found"] == {}
        assert room["name"] and room["status"] == "WAITING" and room["cutter"] is None
        assert len(room["players"]) == 1 and room["players"][0]["name"] == "player1"
        assert set(room["players"][0].keys()) == {"name", "id"}

    client.emit("login", {"username": "player1"}, callback=callback)
    client.sleep(0.05)
    client.disconnect()


def test_MainNamespace_login_twice():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "SUCCESS"

    client.emit("login", {"username": "player1"}, callback=callback)

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Player already logged in."}

    client.emit("login", {"username": "player1"}, callback=callback)
    client.sleep(0.05)
    client.disconnect()


def test_MainNamespace_login_specific_room():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert room["name"] == "room1"
        assert len(room["players"]) == 1 and room["players"][0]["name"] == "player1"

    client.emit(
        "login", {"username": "player1", "roomname": "room1"}, callback=callback
    )
    client.sleep(0.05)

    client2 = socketio.Client()
    client2.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert room["name"] == "room1"
        assert (
            len(room["players"]) == 2
            and room["players"][0]["name"] == "player1"
            and room["players"][1]["name"] == "player2"
        )

    client2.emit(
        "login", {"username": "player2", "roomname": "room1"}, callback=callback
    )
    client2.sleep(0.05)

    client.disconnect()
    client2.disconnect()


def test_MainNamespace_login_random_fill_same_room():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert len(room["players"]) == 1 and room["players"][0]["name"] == "player1"

    client.emit("login", {"username": "player1"}, callback=callback)
    client.sleep(0.05)

    client2 = socketio.Client()
    client2.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert (
            len(room["players"]) == 2
            and room["players"][0]["name"] == "player1"
            and room["players"][1]["name"] == "player3"
        )

    client2.emit("login", {"username": "player3"}, callback=callback)
    client2.sleep(0.05)

    client.disconnect()
    client2.disconnect()


def test_MainNamespace_login_error_if_full_room():
    clients = [socketio.Client() for i in range(8)]

    for client in clients:
        client.connect("http://localhost:5000/", namespaces=["/"])
        client.emit("login", {"username": f"player", "roomname": "room1"})

    client2 = socketio.Client()
    client2.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Impossible to join this room."}

    client2.emit(
        "login", {"username": "player3", "roomname": "room1"}, callback=callback
    )

    client2.sleep(0.05)
    client2.disconnect()
    for client in clients:
        client.disconnect()


def test_MainNamespace_cut_errors():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Invalid target id."}

    client.emit("cut", {"target": "unknow_target"}, callback=callback)
    client.emit("login", {"username": "player1"})

    client2 = socketio.Client()
    client2.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Player not logged in."}

    client2.emit("cut", {"target": client.sid}, callback=callback)
    client2.emit("login", {"username": "player2"})

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Error while cutting."}

    client2.emit("cut", {"target": client2.sid}, callback=callback)

    client3 = socketio.Client()
    client3.connect("http://localhost:5000/", namespaces=["/"])
    client3.emit("login", {"username": "player1", "roomname": "other_room"})

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Can not cut player from other room."}

    client3.emit("cut", {"target": client2.sid}, callback=callback)

    client.sleep(0.05)
    client.disconnect()
    client2.disconnect()
    client3.disconnect()


def test_MainNamespace_cut():
    clients = [socketio.Client() for i in range(4)]

    for client in clients:
        client.connect("http://localhost:5000/", namespaces=["/"])
        client.emit("login", {"username": "player", "roomname": "room1"})
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "SUCCESS"
        assert res["data"]["cutter"]["id"] == clients[0].sid

    clients[0].emit("start", callback=callback)
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Error while cutting."}

    clients[3].emit("cut", {"target": clients[0].sid}, callback=callback)
    clients[3].sleep(0.05)

    def callback(res):
        assert res["status"] == "SUCCESS"
        assert res["data"]["cutter"]["id"] == clients[1].sid

    clients[0].emit("cut", {"target": clients[1].sid}, callback=callback)
    clients[0].sleep(0.05)

    for client in clients:
        client.disconnect()


def test_MainNamespace_cut():
    clients = [socketio.Client() for i in range(4)]

    for client in clients:
        client.connect("http://localhost:5000/", namespaces=["/"])
        client.emit("login", {"username": "player", "roomname": "room1"})
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "SUCCESS"
        assert res["data"]["cutter"]["id"] == clients[0].sid

    clients[0].emit("start", callback=callback)
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Error while cutting."}

    clients[3].emit("cut", {"target": clients[0].sid}, callback=callback)
    clients[3].sleep(0.05)

    def callback(res):
        assert res["status"] == "SUCCESS"
        assert res["data"]["cutter"]["id"] == clients[1].sid

    clients[0].emit("cut", {"target": clients[1].sid}, callback=callback)
    clients[0].sleep(0.05)

    for client in clients:
        client.disconnect()


def test_MainNamespace_start():
    clients = [socketio.Client() for i in range(4)]
    for client in clients:
        client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Player not logged in."}

    clients[0].emit("start", callback=callback)
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Can not start game in this room."}

    clients[0].emit("login", {"username": "player1", "roomname": "start_room"})
    clients[0].emit("start", callback=callback)
    clients[0].sleep(0.05)

    for client in clients[1:]:
        client.emit("login", {"username": "player", "roomname": "start_room"})
    clients[0].sleep(0.05)

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert (
            room["cutter"]["name"] == "player1"
            and room["cutter"]["id"] == clients[0].sid
        )
        assert room["status"] == "PLAYING"
        assert len(room["players"]) == 4
        assert (
            sum(room["cards_left"].values()) == 20
            and sum(room["cards_found"].values()) == 0
        )

    clients[0].emit("start", callback=callback)
    clients[0].sleep(0.05)

    for client in clients:
        client.disconnect()


def test_MainNamespace_chat():
    client = socketio.Client()
    client.connect("http://localhost:5000/", namespaces=["/"])

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Player not logged in."}

    client.emit("chat", {"message": "test-message"}, callback=callback)

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Invalid data."}

    client.emit("login", {"username": "playername"})
    client.emit("chat", {}, callback=callback)

    def callback(res):
        assert res["status"] == "SUCCESS"
        assert res["data"] == {"message": "test-message", "player": "playername"}

    client.emit("chat", {"message": "test-message"}, callback=callback)

    client.sleep(0.05)
    client.disconnect()
