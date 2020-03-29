from unittest.mock import patch, PropertyMock
from pytest import fixture

from timebomb.room.model import Room
from timebomb.player.model import Player
from timebomb.room.service import RoomService, ROOMS


def make_player(marker=None):
    return Player(name=f"user_{marker}", id=f"id_{marker}")


def make_room(marker=None):
    return Room(name=f"room_{marker}", id=f"id_{marker}")


@fixture
def room_db():
    yield ROOMS
    ROOMS.clear()


def test_RoomService_get_by_id(room_db: list):
    room1: Room = make_room(1)

    room_db.append(room1)

    result: Room = RoomService.get_by_id("id_1")

    assert result is room1


def test_RoomService_get_by_name(room_db: list):
    room1: Room = make_room(1)

    room_db.append(room1)

    result: Room = RoomService.get_by_name("room_1")

    assert result is room1


def test_RoomService_get_open_rooms(room_db: list):
    room1: Room = make_room(1)

    room_db.append(room1)

    result: list = RoomService.get_open_rooms()

    assert len(result) == 1 and room1 in result

    room1.players = [make_player(i) for i in range(8)]

    result: list = RoomService.get_open_rooms()

    assert result == []


def test_RoomService_update(room_db: list):
    room1: Room = make_room(1)

    room_db.append(room1)

    assert room_db[0].name == "room_1"

    updates = {"name": "newname"}
    RoomService.update(room1, updates)

    assert room_db[0].name == "newname"


def test_RoomService_delete(room_db: list):
    room1: Room = make_room(1)
    room2: Room = make_room(2)

    room_db.append(room1)
    room_db.append(room2)

    result = RoomService.delete(room1)

    assert result == "id_1"
    assert len(room_db) == 1
    assert room1 not in room_db and room2 in room_db


def test_RoomService_create(room_db: list):
    result: Room = RoomService.create("newroom")

    assert result.name == "newroom" and result.id

    assert len(room_db) == 1
    assert result in room_db


def test_RoomService_create_random(room_db: list):
    result: Room = RoomService.create_random()

    assert result.name and "-" in result.name and result.id

    assert len(room_db) == 1
    assert result in room_db


def test_RoomService_add_player(room_db: list):
    player1: Player = make_player(1)
    player2: Player = make_player(2)

    room1: Room = make_room(1)
    room2: Room = make_room(2)

    assert not room1.players
    assert not room2.players

    with patch.object(Room, "status", new_callable=PropertyMock) as status_prop:
        status_prop.return_value = "PLAYING"
        result: bool = RoomService.add_player(room1, player1)
        assert not result
        assert not room1.players

    result: bool = RoomService.add_player(room1, player1)

    assert result
    assert len(room1.players) == 1 and player1 in room1.players
    assert not room2.players

    result: bool = RoomService.add_player(room2, player2)

    assert result
    assert len(room1.players) == 1 and player1 in room1.players
    assert len(room2.players) == 1 and player2 in room2.players


def test_RoomService_cut_card(room_db: list):
    player1: Player = make_player(1)
    player2: Player = make_player(2)
    room: Room = make_room()

    player2.hand = ["D"]
    room.players = [player1, player2]
    room.cutter = player1
    room.cards_found = {"D": 0}
    room.cards_left = {"D": 1}

    assert room.status != "PLAYING"
    result: bool = RoomService.cut_card(room, player1, player2)
    assert not result

    with patch.object(Room, "status", new_callable=PropertyMock) as status_prop:
        status_prop.return_value = "PLAYING"
        assert room.status == "PLAYING"

        result: str = RoomService.cut_card(room, player2, player1)
        assert not result

        result: str = RoomService.cut_card(room, player1, player1)
        assert not result

        result: str = RoomService.cut_card(room, player1, player2)
        assert result == "D"
        assert room.cutter is player2
        assert room.cards_found == {"D": 1}
        assert room.cards_left == {"D": 0}
        assert player2.hand == []


def test_RoomService_distribute_cards(room_db: list):
    room: Room = make_room()

    with patch.object(Room, "status", new_callable=PropertyMock) as status_prop:
        status_prop.return_value = "PLAYING"

        room.players = [make_player(i) for i in range(3)]
        room.cards_left = {"D": 4}
        result: bool = RoomService.distribute_cards(room)
        assert not result

        room.players.append(make_player(3))
        room.cards_left = {"D": 3}
        result: bool = RoomService.distribute_cards(room)
        assert not result

        room.cards_left = {"D": 4}
        result: bool = RoomService.distribute_cards(room)

        assert result
        for player in room.players:
            assert player.hand == ["D"]

    result: bool = RoomService.distribute_cards(room)
    assert not result


def test_RoomService_distribute_cards(room_db: list):
    room: Room = make_room()
    assert room.status == "WAITING"

    result: bool = RoomService.start(room)
    assert not result

    room.players = [make_player(i) for i in range(4)]
    assert room.status == "READY"

    result: bool = RoomService.start(room)
    assert result
    assert room.status == "PLAYING"
    assert room.cutter is room.players[0]

    assert len(room.cards_found) == 3 and sum(room.cards_found.values()) == 0
    assert len(room.cards_left) == 3 and sum(room.cards_left.values()) == 20

    for player in room.players:
        assert player.team in ["Sherlock", "Moriarty"]
        assert len(player.hand) == 5
