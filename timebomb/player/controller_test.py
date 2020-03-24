from unittest.mock import patch

from flask import Flask
from flask_restplus import Api

from pytest import fixture

from timebomb.player.controller import PlayerAPI
from timebomb.player.service import PlayerService
from timebomb.player.model import Player


def make_player(marker=""):
    return Player(f"name_{marker}", f"id_{marker}", f"room_{marker}")


@fixture
def test_client():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    api = Api(app=app)
    api.add_namespace(PlayerAPI)

    return app.test_client()


@patch.object(PlayerService, "get_all", lambda: [make_player(1), make_player(2)])
def test_PlayerResource_get(test_client):
    results = test_client.get("/player/").get_json()

    assert len(results) == 2
    assert results[0] == {"name": "name_1", "id": "id_1"}
    assert results[1] == {"name": "name_2", "id": "id_2"}


@patch.object(PlayerService, "create", lambda player: player)
def test_PlayerResource_post(test_client):
    results = test_client.post(
        "/player/", data={"name": "username", "id": "userid", "roomId": "roomid"}
    ).get_json()

    assert results
    assert results == {"name": "username", "id": "userid", "roomId": "roomid"}


@patch.object(PlayerService, "get_by_id", lambda id: make_player(id))
def test_PlayerIdResource_get(test_client):
    results = test_client.get("/player/11").get_json()

    assert results
    assert results == {"name": "name_11", "id": "id_11"}


@patch.object(PlayerService, "delete", lambda id: f"id{id}")
def test_PlayerIdResource_delete(test_client):
    results = test_client.delete("/player/11").get_json()

    assert results
    assert results == {"id": "id11"}


@patch.object(PlayerService, "get_by_id", lambda id: make_player(id))
@patch.object(
    PlayerService, "update", lambda p, changes: Player(**{**p.__dict__, **changes})
)
def test_PlayerIdResource_put(test_client):
    results = test_client.put("/player/11", data={"name": "username"}).get_json()

    assert results
    assert results == {"id": "id_11", "name": "username"}
