from collections import Counter

import numpy as np

from timebomb.model import magics
from timebomb.model.game import Game, count_to_list, remove_random_element


def test_count_to_list():
    map = {"A": 2, "B": 3}
    np.testing.assert_equal(count_to_list(map), ["A", "A", "B", "B", "B"])


def test_remove_random_element():
    res = remove_random_element([1, 2, 3, 4, 5])
    assert len(res) == 4


def test_game_init():
    game = Game()
    assert game.status == "WAITING"
    assert game.cut_round is None
    assert game.hand_round is None


def test_game_start_4_players():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    assert game.status == "PLAYING"
    assert len(game.roles) == 4
    np.testing.assert_equal(list(game.roles.keys()), [1, 2, 3, 4])
    assert sorted(game.roles.values()) == ["B", "B", "R", "R"] or sorted(
        game.roles.values()
    ) == ["B", "B", "B", "R"]
    assert game.deck == {"B": 1, "D": 4, "N": 15}
    assert sum(game.deck.values()) % len(game.roles) == 0
    assert game.found == {"B": 0, "D": 0, "N": 0}
    assert game.cut == 1
    assert len(game.hands) == 4


def test_game_start_5_players():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4, 5])

    assert game.status == "PLAYING"
    assert len(game.roles) == 5
    np.testing.assert_equal(list(game.roles.keys()), [1, 2, 3, 4, 5])
    np.testing.assert_equal(sorted(game.roles.values()), ["B", "B", "B", "R", "R"])
    assert game.deck == {"B": 1, "D": 5, "N": 19}
    assert sum(game.deck.values()) % len(game.roles) == 0
    assert game.found == {"B": 0, "D": 0, "N": 0}
    assert game.cut == 1
    assert len(game.hands) == 5


def test_game_rounds_with_4_players():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    assert game.cut_round == 0
    assert game.hand_round == 1
    assert game.cut == 1

    game.cut_card(2)

    assert game.cut_round == 1
    assert game.hand_round == 1
    assert game.cut == 2

    for i in range(2):
        game.cut_card(1)

    assert game.cut_round == 3
    assert game.hand_round == 1
    assert game.cut == 1

    game.cut_card(3)

    assert game.cut_round == 0
    assert game.hand_round == 2
    assert game.cut == 3


def test_game_cut_card():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    assert sum(game.deck.values()) == 20
    assert sum(game.found.values()) == 0
    assert len(game.hands[1]) == 5

    card = game.cut_card(1)

    assert len(game.hands[1]) == 4
    assert sum(game.deck.values()) == 19
    assert sum(game.found.values()) == 1
    assert game.found[card] == 1


def test_game_distribute():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    hands = game.distribute()
    assert len(hands) == 4
    assert set([len(hand) for sid, hand in hands.items()]) == {5}

    for i in range(4):
        game.cut_card(1)

    assert sum(game.deck.values()) == 16
    assert sum(game.found.values()) == 4

    hands = game.distribute()

    assert len(hands) == 4
    hands_content = [el for sid, hand in hands.items() for el in hand]
    c = Counter(hands_content)

    if game.found["B"]:
        assert game.deck == {**c, "B": 0}
    else:
        assert game.deck == c


def test_game_state():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    assert game.state == {
        "found": game.found,
        "left": game.deck,
        "cut": game.cut,
        "handround": game.hand_round,
        "cutround": game.cut_round,
    }


def test_game_player_state():
    game = Game()
    game.start(player_ids=[1, 2, 3, 4])

    player_state = game.player_state(1)
    assert player_state == {"hand": game.hands[1], "role": game.roles[1]}
