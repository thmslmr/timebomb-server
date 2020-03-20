import numpy as np

from timebomb.model import magics


def count_to_list(dct: dict) -> np.ndarray:
    """Transform counter in list.

    Args:
        dct (dict): The counter.

    Returns:
        np.ndarray: The list generated from the counter.

    """
    return np.repeat(list(dct.keys()), list(dct.values()))


def remove_random_element(lst: list) -> list:
    """Remove one random element from a list.

    Args:
        lst (list): The list.

    Returns:
        list: the new llist without the picked element.

    """
    np.random.shuffle(lst)
    new_lst = lst[1:]
    return new_lst


class Game:
    """Game model."""

    def __init__(self):
        """Set status to WAITING while game has not started."""
        self.status = "WAITING"

    @property
    def cut_round(self) -> int:
        """Get current cut round.

        Returns:
            int: cut round given by card found and nb of players.

        """
        if self.status == "WAITING":
            return
        return sum(self.found.values()) % len(self.roles)

    @property
    def hand_round(self) -> int:
        """Get current hand round.

        Returns:
            int: cut round given by card left and nb of players.

        """
        if self.status == "WAITING":
            return
        return 5 - (np.ceil(sum(self.deck.values()) / len(self.roles)) - 1)

    def start(self, player_ids: list):
        """Start the game.

        Args:
            player_ids (list): The list of player IDs in this game.

        """
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

    def distribute(self) -> dict:
        """Distribute the card left among the players.

        Returns:
            dict: A dictionnary of hands, where each key is a player id
                and the value is a list of card.

        """
        deck = count_to_list(self.deck)
        np.random.shuffle(deck)
        hands = np.split(deck, len(self.roles))
        return dict(zip(self.roles.keys(), hands))

    def cut_card(self, player_id: id) -> str:
        """Cut a random card in player hands.

        Args:
            player_id (id): The player to cut.

        Returns:
            str: The card cut.

        """
        np.random.shuffle(self.hands[player_id])
        card = self.hands[player_id][0]
        self.hands[player_id] = np.delete(self.hands[player_id], 0)

        self.found[card] += 1
        self.deck[card] -= 1
        self.cut = player_id

        return card

    @property
    def state(self) -> dict:
        """Get game state.

        Returns:
            dict: Dict containing all public game informations.

        """
        return {
            "found": self.found,
            "left": self.deck,
            "cut": self.cut,
            "handround": self.hand_round,
            "cutround": self.cut_round,
        }

    def player_state(self, player_id: id) -> dict:
        """Get player private game state.

        Args:
            player_id (id): The player id.

        Returns:
            dict: Dict containing player hand and role.

        """
        return {"hand": self.hands[player_id], "role": self.roles[player_id]}
