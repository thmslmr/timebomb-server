from pytest import fixture
from timebomb.room.model import Room
import timebomb.room.magics as magics


@fixture
def room() -> Room:
    return Room(name="roomname", id="rid")


def test_Room_create(room: Room):
    assert room
    assert room.name == "roomname"
    assert room.id == "rid"

    assert type(room.players) is list and not room.players
    assert room.cutter is None

    assert type(room.cards_found) is dict and not room.cards_found
    assert type(room.cards_left) is dict and not room.cards_left

    assert room.status == "WAITING"
    assert room.nb_players == 0
    assert room.is_open
    assert room.winning_team is None


def test_Room_status(room: Room):
    assert room.status == "WAITING"

    room.players = list(range(magics.MIN_PLAYERS - 1))
    assert room.status == "WAITING"

    room.players.append(4)
    assert room.status == "READY"

    room.cards_left = {"card_value": 10}
    assert room.status == "PLAYING"

    room.cards_left = {"card_value": 4}
    assert room.status == "ENDED"

    room.cards_left = {"card_value": 10}
    room.cards_found = {"B": 1}
    assert room.status == "ENDED"

    room.cards_found = {"D": 3}
    assert room.status == "PLAYING"

    room.cards_found = {"D": 4}
    assert room.status == "ENDED"
