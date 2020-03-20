import numpy as np

from timebomb.model import magics


def count_to_list(dct):
    return np.repeat(list(dct.keys()), list(dct.values()))


def remove_random_element(lst):
    np.random.shuffle(lst)
    new_lst = lst[1:]
    return new_lst


class Game:
    def __init__(self):
        self.status = "WAITING"

    @property
    def cut_round(self):
        if self.status != "PLAYING":
            return
        return sum(self.found.values()) % len(self.roles)

    @property
    def hand_round(self):
        if self.status != "PLAYING":
            return
        return 5 - (np.ceil(sum(self.deck.values()) / len(self.roles)) - 1)

    def start(self, player_ids):
        self.status = "PLAYING"

        nb_player = len(player_ids)
        roles = magics.NBPLAYER_TO_ROLES[nb_player].copy()
        roles_lst = count_to_list(roles)

        if len(roles_lst) > nb_player:
            roles_lst = remove_random_element(roles_lst)

        deck = magics.NBPLAYER_TO_DECK[nb_player].copy()

        self.roles = dict(zip(player_ids, roles_lst))
        self.deck = deck
        self.found = {"B": 0, "D": 0, "N": 0}
        self.cut = player_ids[0]

        self.hands = self.distribute()

    def distribute(self):
        deck = count_to_list(self.deck)
        np.random.shuffle(deck)
        hands = np.split(deck, len(self.roles))
        return dict(zip(self.roles.keys(), hands))

    def cut_card(self, player_id):
        np.random.shuffle(self.hands[player_id])
        card = self.hands[player_id][0]
        self.hands[player_id] = np.delete(self.hands[player_id], 0)

        self.found[card] += 1
        self.deck[card] -= 1
        self.cut = player_id

        return card

    @property
    def state(self):
        return {
            "found": self.found,
            "left": self.deck,
            "cut": self.cut,
            "handround": self.hand_round,
            "cutround": self.cut_round,
        }

    def player_state(self, player_id):
        return {"hand": self.hands[player_id], "role": self.roles[player_id]}
