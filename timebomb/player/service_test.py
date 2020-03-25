from pytest import fixture

from timebomb.player.model import Player
from timebomb.player.service import PlayerService, PLAYERS


def make_player(marker=None):
    return Player(name=f"user_{marker}", id=f"id_{marker}")


@fixture
def player_db():
    yield PLAYERS
    PLAYERS.clear()


def test_PlayerService_get_by_id(player_db: list):
    player1: Player = make_player(1)

    player_db.append(player1)

    result: Player = PlayerService.get_by_id("id_1")

    assert result is player1


def test_PlayerService_update(player_db: list):
    player1: Player = make_player(1)

    player_db.append(player1)

    assert player_db[0].name == "user_1"

    updates = {"name": "newname"}
    PlayerService.update(player1, updates)

    assert player_db[0].name == "newname"


def test_PlayerService_delete(player_db: list):
    player1: Player = make_player(1)
    player2: Player = make_player(2)

    player_db.append(player1)
    player_db.append(player2)

    result = PlayerService.delete(player1)

    assert result == "id_1"
    assert len(player_db) == 1
    assert player1 not in player_db and player2 in player_db


def test_PlayerService_create(player_db: list):
    infos = {"name": "username", "id": "userid"}
    result = PlayerService.create(infos)

    assert result.name == "username" and result.id == "userid"

    assert len(player_db) == 1
    assert result in player_db
