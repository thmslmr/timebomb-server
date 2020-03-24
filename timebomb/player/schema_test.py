from pytest import fixture

from timebomb.player.model import Player
from timebomb.player.schema import PlayerSchema
from timebomb.player.interface import PlayerInterface


def test_PlayerSchema_create():
    assert PlayerSchema()


def test_PlayerSchema_load():
    schema = PlayerSchema()
    params: PlayerInterface = schema.load(
        {"name": "username", "id": "userid", "roomId": "roomid"}
    )
    player = Player(**params)

    assert player.name == "username"
    assert player.id == "userid"
    assert player.roomid == "roomid"


def test_PlayerSchema_dump():
    schema = PlayerSchema()
    player = Player("username", "userid", "roomid")
    player_infos: PlayerInterface = schema.dump(player)

    assert player_infos == {
        "name": "username",
        "id": "userid",
        "roomId": "roomid",
        "hand": None,
        "team": None,
    }
