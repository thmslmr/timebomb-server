from pytest import fixture

from timebomb.player.model import Player
from timebomb.player.interface import PlayerInterface


@fixture
def interface() -> PlayerInterface:
    return PlayerInterface(name="username", id="userid", roomid="roomid")


def test_PlayerInterface_create(interface: PlayerInterface):
    assert interface


def test_PlayerInterface_works(interface: PlayerInterface):
    player = Player(**interface)
    assert player
