from timebomb.model.arena import Arena
from timebomb.model.player import Player


def test_arena_init():
    arena = Arena()

    assert arena.rooms == []
    assert not arena.open_rooms


def test_arena_create_room():
    arena = Arena()

    assert len(arena.rooms) == 0

    room = arena.create_room("roomname")

    assert room.name == "roomname"
    assert len(arena.rooms) == 1
    assert arena.rooms[0] == room


def test_arena_create_random_room():
    arena = Arena()

    assert len(arena.rooms) == 0

    room = arena.create_random_room()

    assert room.name
    assert len(arena.rooms) == 1
    assert arena.rooms[0] == room


def test_arena_open_rooms():
    arena = Arena()

    assert len(arena.rooms) == 0

    room = arena.create_random_room()

    assert len(arena.open_rooms) == 1

    room.players = range(8)

    assert len(arena.open_rooms) == 0


def test_arena_get_player():
    arena = Arena()

    assert arena.get_player(0) is None

    room = arena.create_random_room()

    assert arena.get_player(0) is None

    new_player = Player("username", 0)
    room.add_player(new_player)

    assert arena.get_player(0) == new_player


def test_arena_join_room():
    arena = Arena()
    player1 = Player("username", 0)

    assert len(arena.rooms) == 0
    assert player1.roomname is None

    random_room = arena.join_room(player1)

    assert len(arena.rooms) == 1
    assert len(arena.open_rooms) == 1
    assert arena.rooms[0] == random_room
    assert len(random_room.players) == 1
    assert random_room.players[0] == player1
    assert player1.roomname == random_room.name

    player2 = Player("username", 1)
    join_room = arena.join_room(player2)

    assert random_room == join_room
    assert len(arena.rooms) == 1
    assert len(arena.open_rooms) == 1
    assert len(join_room.players) == 2
    assert player2.roomname == player1.roomname

    player3 = Player("username", 2)
    custom_room = arena.join_room(player3, roomname="roomname")

    assert join_room != custom_room
    assert len(arena.rooms) == 2
    assert len(arena.open_rooms) == 2
    assert len(custom_room.players) == 1
    assert custom_room.players[0] == player3
    assert player3.roomname == "roomname"
    assert len(join_room.players) == 2

    player4 = Player("username", 3)
    custom_room_2 = arena.join_room(player4, roomname="roomname")
    assert custom_room_2 == custom_room
    assert len(arena.rooms) == 2
    assert len(custom_room_2.players) == 2
    assert len(join_room.players) == 2

    custom_room_2.players = [Player(f"name_{i}", i) for i in range(8)]
    join_room.players = [Player(f"name_{i}", i) for i in range(8, 16)]

    assert len(custom_room_2.players) == 8
    assert len(join_room.players) == 8
    assert len(arena.rooms) == 2
    assert len(arena.open_rooms) == 0

    player5 = Player("username", 4)
    custom_room_3 = arena.join_room(player5, roomname="roomname")
    assert not custom_room_3
    assert len(arena.rooms) == 2
    assert len(arena.open_rooms) == 0

    player6 = Player("username", 5)
    custom_room_3 = arena.join_room(player6)
    assert len(arena.rooms) == 3
    assert len(arena.open_rooms) == 1
    assert len(custom_room_2.players) == 8
    assert len(join_room.players) == 8
    assert len(custom_room_3.players) == 1
