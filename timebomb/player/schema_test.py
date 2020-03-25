from timebomb.player.model import Player
from timebomb.player.schema import PlayerSchema


def test_PlayerSchema_create():
    assert PlayerSchema()


def test_PlayerSchema_load():
    schema = PlayerSchema()
    params = schema.load({"name": "username", "id": "userid"})
    player = Player(**params)

    assert player.name == "username"
    assert player.id == "userid"


def test_PlayerSchema_dump():
    player = Player("username", "userid")

    schema = PlayerSchema()
    player_json = schema.dump(player)

    assert player_json == {
        "name": "username",
        "id": "userid",
        "roomId": None,
        "hand": [],
        "team": None,
    }
