from pytest import fixture

from timebomb.player.model import Player
from timebomb.player.service import PlayerService, PLAYERS
from timebomb.player.interface import PlayerInterface


@fixture
def player_db():
    yield PLAYERS
    PLAYERS.clear()


def test_PlayerService_get_all(player_db: list):
    results: list = PlayerService.get_all()

    assert len(results) == 0

    player1: Player = Player(name="player1", id="player1id", roomid="roomid")
    player2: Player = Player(name="player2", id="player2id", roomid="roomid")

    player_db.append(player1)
    player_db.append(player2)

    results: list = PlayerService.get_all()

    assert len(results) == 2
    assert player1 in results and player2 in results


def test_PlayerService_get_by_id(player_db: list):
    player1: Player = Player(name="player1", id="player1id", roomid="roomid")

    player_db.append(player1)

    result: Player = PlayerService.get_by_id("player1id")

    assert result is player1


def test_PlayerService_update(player_db: list):
    player1: Player = Player(name="player1", id="player1id", roomid="roomid")

    player_db.append(player1)

    updates: PlayerInterface = {"name": "newname"}

    PlayerService.update(player1, updates)

    assert player_db[0].name == "newname"


def test_PlayerService_delete(player_db: list):
    player1: Player = Player(name="player1", id="player1id", roomid="roomid")
    player2: Player = Player(name="player2", id="player2id", roomid="roomid")

    player_db.append(player1)
    player_db.append(player2)

    result = PlayerService.delete(player1)

    assert result == "player1id"
    assert len(player_db) == 1
    assert player1 not in player_db and player2 in player_db


def test_PlayerService_create(player_db: list):
    infos: PlayerInterface = {"name": "username", "id": "userid", "roomid": "roomid"}
    result = PlayerService.create(infos)

    assert (
        result.name == "username"
        and result.id == "userid"
        and result.roomid == "roomid"
    )

    assert len(player_db) == 1
    assert result in player_db
