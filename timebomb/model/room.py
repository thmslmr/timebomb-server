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


class Room:
    """Room model."""

    def __init__(self, name: str):
        self.name = name

        self.status = "WAITING"
        self.found = {"B": 0, "D": 0, "N": 0}
        self.left = {}
        self.players = []

    @property
    def cut_round(self) -> int:
        """Get current cut round.

        Returns:
            int: cut round given by card found and nb of players.

        """
        if self.status != "PLAYING":
            return

        return sum(self.found.values()) % len(self.players)

    @property
    def hand_round(self) -> int:
        """Get current hand round.

        Returns:
            int: cut round given by card left and nb of players.

        """
        if self.status != "PLAYING":
            return

        return 5 - (np.ceil(sum(self.left.values()) / len(self.players)) - 1)

    @property
    def cutter(self) -> object:
        """Get current cuting player.

        Returns:
            object: Player who is currently cutting.

        """
        if self.status != "PLAYING":
            return

        return [player for player in self.players if player.is_cutting][0]

    @property
    def state(self) -> dict:
        """Get room state.

        Returns:
            dict: Dict containing all public room informations.

        """
        cutter_name = self.cutter.name if self.cutter else ""
        return {
            "name": self.name,
            "players": [player.public_state for player in self.players],
            "found": self.found,
            "left": self.left,
            "cutter": cutter_name,
            "handround": self.hand_round,
            "cutround": self.cut_round,
        }

    @property
    def is_open(self) -> bool:
        """Know if the room is open to new player.

        Returns:
            bool: If room is open.

        """
        return self.status == "WAITING" and len(self.players) < magics.MAX_PLAYERS

    def get_player(self, sid: str) -> object:
        """Get player object by its sid.

        Args:
            sid (str): The player sid.

        Returns:
            object: Player object found if exists, else None.

        """
        for player in self.players:
            if player.sid == sid:
                return player

    def set_roles(self):
        """Set players new random role."""
        nb_player = len(self.players)
        roles = magics.NBPLAYER_TO_ROLES[nb_player].copy()
        roles_lst = count_to_list(roles)

        if len(roles_lst) > nb_player:
            np.random.shuffle(roles_lst)
            roles_lst = roles_lst[1:]

        assert len(roles_lst) == len(self.players)

        for i, role in enumerate(roles_lst):
            self.players[i].role = role

    def set_hands(self):
        """Set players new random hands."""
        left = count_to_list(self.left)
        np.random.shuffle(left)
        hands = np.split(left, len(self.players))

        assert len(hands) == len(self.players)

        for i, hand in enumerate(hands):
            self.players[i].hand = hand

    def add_player(self, player: object) -> object:
        """Add player to the room.

        Args:
            player (object): The player to add.

        Returns:
            object: The added player if open, else None.

        """
        if self.is_open:
            self.players.append(player)
            return player

    def start(self):
        """Start the game."""
        if len(self.players) < magics.MIN_PLAYERS:
            return

        self.status = "PLAYING"

        self.left = magics.NBPLAYER_TO_DECK[len(self.players)].copy()

        self.set_hands()
        self.set_roles()

        self.players[0].is_cutting = True

    def cut_card(self, src_sid: id, dst_sid: id) -> str:
        """Cut a random card in player hands.

        Args:
            src_sid (id): The player sid who cuts.
            dst_sid (id): The player sid to be cut.

        Returns:
            str: The card cut.

        """
        player_src = self.get_player(src_sid)

        if not player_src.is_cutting:
            return

        player_dst = self.get_player(dst_sid)

        np.random.shuffle(player_dst.hand)
        card = player_dst.hand[0]
        player_dst.hand = np.delete(player_dst.hand, 0)

        self.found[card] += 1
        self.left[card] -= 1

        player_src.is_cutting = False
        player_dst.is_cutting = True

        return card
