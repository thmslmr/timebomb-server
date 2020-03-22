from timebomb.model.player import Player


def test_player_init():
    player = Player("username", "sid")
    assert player.name == "username"
    assert player.sid == "sid"

    assert not player.role
    assert len(player.hand) == 0
    assert not player.is_cutting

    assert player.public_state == {
        "name": "username",
        "sid": "sid",
        "is_cutting": False,
    }
