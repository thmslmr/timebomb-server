from collections import Counter

import numpy as np

from timebomb.model import magics
from timebomb.model.room import Room, count_to_list
from timebomb.model.player import Player


def test_count_to_list():
    map = {"A": 2, "B": 3}
    np.testing.assert_equal(count_to_list(map), ["A", "A", "B", "B", "B"])


def test_room_init():
    room = Room("testroom")
    assert room.status == "WAITING"
    assert room.name == "testroom"
    assert room.cutter is None

    assert type(room.found) is dict
    assert room.found == {"B": 0, "D": 0, "N": 0}

    assert type(room.left) is dict
    assert not room.left

    assert type(room.players) is list
    assert not room.players

    assert type(room.state) is dict
    assert room.state == {
        "found": {"B": 0, "D": 0, "N": 0},
        "left": {},
        "cutter": None,
        "name": "testroom",
        "status": "WAITING",
        "players": [],
    }


def test_room_start_4_players():
    room = Room("testroom")

    assert room.status == "WAITING"

    room.players = [Player(f"name_{i}", i) for i in range(4)]

    assert len(room.players) == 4
    assert room.status == "READY"
    assert not room.left
    assert room.found == {"B": 0, "D": 0, "N": 0}

    room.start()

    assert room.status == "PLAYING"
    assert room.left == {"B": 1, "D": 4, "N": 15}
    assert room.found == {"B": 0, "D": 0, "N": 0}
    assert room.cutter == room.players[0]

    all_roles = []
    all_hands = []

    for player in room.players:
        assert player.role in ["B", "R"]
        all_roles.append(player.role)

        assert len(player.hand) == 5
        all_hands.append(player.hand)

    all_roles = sorted(all_roles)
    assert all_roles == ["B", "B", "R", "R"] or all_roles == ["B", "B", "B", "R"]
    assert Counter(np.array(all_hands).reshape(-1).tolist()) == room.left


def test_room_round_with_4_players():
    room = Room("testroom")
    room.players = [Player(f"name_{i}", i) for i in range(4)]
    room.start()

    assert sum(room.found.values()) == 0
    assert room.cutter.sid == 0

    room.cut_card(room.players[1], room.players[2])

    assert sum(room.found.values()) == 0
    assert room.cutter.sid == 0

    room.cut_card(room.players[0], room.players[2])

    assert sum(room.found.values()) == 1
    assert room.cutter.sid == 2

    room.cut_card(room.players[2], room.players[1])
    assert room.cutter.sid == 1
    room.cut_card(room.players[1], room.players[3])

    assert sum(room.found.values()) == 3
    assert room.cutter.sid == 3

    room.cut_card(room.players[3], room.players[0])

    assert sum(room.found.values()) == 4
    assert room.cutter.sid == 0


def test_room_cut_card():
    room = Room("testroom")
    room.players = [Player(f"name_{i}", i) for i in range(4)]
    room.start()

    assert sum(room.left.values()) == 20
    assert sum(room.found.values()) == 0
    assert len(room.players[1].hand) == 5

    card = room.cut_card(room.players[0], room.players[1])

    assert card in ["D", "N", "B"]
    assert sum(room.left.values()) == 19
    assert sum(room.found.values()) == 1
    assert len(room.players[1].hand) == 4
    assert room.found[card] == 1


def test_room_get_player():
    room = Room("testroom")
    room.players = [Player(f"name_{i}", i) for i in range(4)]

    assert room.get_player(4) is None

    new_player = Player("name_4", 4)
    room.add_player(new_player)
    assert room.get_player(4) == new_player


def test_room_add_player():
    room = Room("testroom")
    player = Player("name", 0)

    assert room.players == []
    assert player.roomname is None

    room.add_player(player)

    assert len(room.players) == 1
    assert room.players[0] == player
    assert player.roomname == room.name


def test_room_state():
    room = Room("testroom")
    room.players = [Player(f"name_{i}", i) for i in range(4)]

    assert room.state == {
        "found": {"B": 0, "D": 0, "N": 0},
        "left": {},
        "cutter": None,
        "name": "testroom",
        "status": "READY",
        "players": [
            {"name": "name_0", "sid": 0},
            {"name": "name_1", "sid": 1},
            {"name": "name_2", "sid": 2},
            {"name": "name_3", "sid": 3},
        ],
    }

    room.start()

    assert room.state == {
        "found": {"B": 0, "D": 0, "N": 0},
        "left": {"B": 1, "D": 4, "N": 15},
        "cutter": {"name": "name_0", "sid": 0},
        "name": "testroom",
        "status": "PLAYING",
        "players": [
            {"name": "name_0", "sid": 0},
            {"name": "name_1", "sid": 1},
            {"name": "name_2", "sid": 2},
            {"name": "name_3", "sid": 3},
        ],
    }
