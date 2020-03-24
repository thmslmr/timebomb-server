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

        self.found = {"B": 0, "D": 0, "N": 0}
        self.left = {}
        self.players = []
        self.cutter = None

    @property
    def status(self) -> str:
        """Get current room status.

        Returns:
            str: Status name among (WAITING, READY and PLAYING).

        """
        if len(self.left) and (
            self.found["B"] > 0
            or self.found["D"] == len(self.players)
            or sum(self.left.values()) <= len(self.players)
        ):
            return "ENDED"
        if len(self.left):
            return "PLAYING"

        if len(self.players) < magics.MIN_PLAYERS:
            return "WAITING"

        if len(self.players) >= magics.MIN_PLAYERS and len(self.left) == 0:
            return "READY"

    @property
    def state(self) -> dict:
        """Get room state.

        Returns:
            dict: Dict containing all public room informations.

        """
        return {
            "name": self.name,
            "players": [player.public_state for player in self.players],
            "found": self.found,
            "left": self.left,
            "cutter": self.cutter.public_state if self.cutter else None,
            "status": self.status,
        }

    @property
    def is_open(self) -> bool:
        """Know if the room is open to new player.

        Returns:
            bool: If room is open.

        """
        return self.status != "PLAYING" and len(self.players) < magics.MAX_PLAYERS

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
            player.roomname = self.name
            return player

    def start(self):
        """Start the game."""
        if len(self.players) < magics.MIN_PLAYERS:
            return

        self.left = magics.NBPLAYER_TO_DECK[len(self.players)].copy()

        self.set_hands()
        self.set_roles()

        self.cutter = self.players[0]

    def cut_card(self, src_player: object, dst_player: object) -> str:
        """Cut a random card in player hands.

        Args:
            src_player (object): The player sid who cuts.
            dst_player (object): The player sid to be cut.

        Returns:
            str: The card cut.

        """
        if self.cutter.sid != src_player.sid:
            return

        if src_player.sid == dst_player.sid:
            return

        np.random.shuffle(dst_player.hand)
        card = dst_player.hand[0]
        dst_player.hand = np.delete(dst_player.hand, 0)

        self.found[card] += 1
        self.left[card] -= 1

        self.cutter = dst_player

        return card
