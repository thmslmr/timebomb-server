from pytest import fixture

from timebomb.room.model import Room
from timebomb.room.schema import RoomSchema, EndedRoomSchema
from timebomb.player.model import Player


def test_RoomSchema_create():
    assert RoomSchema()


def test_RoomSchema_load():
    schema = RoomSchema()
    params = schema.load({"name": "roomname", "id": "roomid"})
    room = Room(**params)

    assert room.name == "roomname"
    assert room.id == "roomid"


def test_RoomSchema_dump():
    room = Room("name", "id")

    schema = RoomSchema()
    room_json = schema.dump(room)

    assert room_json == {
        "name": "name",
        "id": "id",
        "players": [],
        "cutter": None,
        "cards_found": {},
        "cards_left": {},
        "status": "WAITING",
    }


def test_RoomSchema_dump_with_player():
    room = Room("name", "id")
    player = Player("username", "id", room.name)

    room.players.append(player)
    room.cutter = player

    schema = RoomSchema()
    room_json = schema.dump(room)

    assert room_json == {
        "name": "name",
        "id": "id",
        "players": [{"name": "username", "id": "id"}],
        "cutter": {"name": "username", "id": "id"},
        "cards_found": {},
        "cards_left": {},
        "status": "WAITING",
    }


def test_EndedRoomSchema_dump_with_player():
    room = Room("name", "id")
    player = Player("username", "id", room.name)

    player.team = "team1"
    room.players.append(player)
    room.cutter = player

    schema = EndedRoomSchema()
    room_json = schema.dump(room)

    assert room_json == {
        "name": "name",
        "id": "id",
        "players": [{"name": "username", "id": "id", "team": "team1"}],
    }
