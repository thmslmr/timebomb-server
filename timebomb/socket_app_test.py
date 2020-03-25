import socketio
import eventlet
import multiprocessing

from pytest import fixture
from timebomb.socket_app import MainNamespace


@fixture(autouse=True)
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
    yield app


@fixture
def client():
    sioclient = socketio.Client()
    sioclient.connect("http://localhost:5000/", namespaces=["/"])
    yield sioclient
    sioclient.disconnect()


def test_MainNamespace_login(client: socketio.Client):
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

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert room["cards_left"] == room["cards_found"] == {}
        assert (
            room["name"] == "room1"
            and room["status"] == "WAITING"
            and room["cutter"] is None
        )
        assert len(room["players"]) == 1 and room["players"][0]["name"] == "player2"
        assert set(room["players"][0].keys()) == {"name", "id"}

    client.emit(
        "login", {"username": "player2", "roomname": "room1"}, callback=callback
    )

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert (
            len(room["players"]) == 2
            and room["players"][0]["name"] == "player1"
            and room["players"][1]["name"] == "player3"
        )

    client.emit("login", {"username": "player3"}, callback=callback)

    def callback(res):
        assert res["status"] == "SUCCESS"
        room = res["data"]
        assert (
            len(room["players"]) == 2
            and room["players"][0]["name"] == "player1"
            and room["players"][1]["name"] == "player3"
        )

    for i in range(7):
        client.emit("login", {"username": f"player{i}", "roomname": "room1"})

    def callback(res):
        assert res["status"] == "ERROR"
        assert res["data"] == {"message": "Impossible to join this room."}

    client.emit(
        "login", {"username": "player3", "roomname": "room1"}, callback=callback
    )
    client.sleep(1)
