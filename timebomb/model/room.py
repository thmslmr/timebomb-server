from timebomb.model.game import Game
from timebomb.model import magics


class Room:
    """Room model."""

    def __init__(self, name: str):
        """Create new game for the room.

        Args:
            name (str): The name of the room.

        """
        self.name = name
        self.game = Game()
        self.players = []

    @property
    def is_open(self) -> bool:
        """Know if the room is open to new player.

        Returns:
            bool: If room is open.

        """
        return self.game.status == "WAITING" and len(self.players) < magics.MAX_PLAYERS

    def add_player(self, player: object) -> bool:
        """Add player to the room.

        Args:
            player (object): The player to add.

        Returns:
            (bool): True if successfully added.

        """
        if self.is_open:
            self.players.append(player)
            return True

    @property
    def state(self) -> dict:
        """Get the room public state.

        Returns:
            dict: The name, list of players and if is open or not.

        """
        return {
            "name": self.name,
            "is_open": self.is_open,
            "players": [p.username for p in self.players],
        }
