from timebomb.model.player import Player


def test_player_init():
    player = Player("username", "sid")
    assert player.username == "username"
    assert player.sid == "sid"
