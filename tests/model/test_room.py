from timebomb.model.room import Room


def test_room_init():
    room = Room("roomname")

    assert room.name == "roomname"
    assert room.game.status == "WAITING"
    assert len(room.players) == 0
    assert room.is_open


def test_room_add_player():
    room = Room("roomname")

    assert len(room.players) == 0
    assert room.is_open

    room.add_player(1)
    assert len(room.players) == 1
    assert room.players[0] == 1
    assert room.is_open

    for i in range(6):
        room.add_player(1)

    assert len(room.players) == 7
    assert room.is_open

    room.add_player(1)

    assert len(room.players) == 8
    assert not room.is_open


def test_room_is_open():
    room = Room("roomname")
    assert room.is_open

    room.players = range(8)
    assert not room.is_open

    room.players = []
    assert room.is_open

    room.game.status = "PLAYING"
    assert not room.is_open
