from pytest import fixture

from timebomb.player.model import Player


@fixture
def default_player() -> Player:
    return Player(name="username", id="playerid", roomid="roomid")


@fixture
def player() -> Player:
    return Player(name="username", id="playerid", roomid="roomid", team="B", hand=[])


def test_Player_create_default(default_player: Player):
    assert default_player


def test_Player_create(player: Player):
    assert player
