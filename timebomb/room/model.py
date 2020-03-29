from dataclasses import dataclass, field
import timebomb.room.magics as magics


@dataclass
class Room:
    """Room Model.

    Attributes:
        name (str): The room name.
        id (str): The room ID.

        players (list): List of Player in this room.
        cutter (Player): Current cutter player.

        cards_found (dict): Counter dict of card found.
        cards_left (dict): Counter dict of card left.

    """

    name: str
    id: str

    players: list = field(default_factory=list)
    cutter = None

    cards_found: dict = field(default_factory=dict)
    cards_left: dict = field(default_factory=dict)

    @property
    def nb_players(self) -> int:
        return len(self.players)

    @property
    def is_open(self) -> bool:
        return (
            self.status in ["WAITING", "READY"] and self.nb_players < magics.MAX_PLAYERS
        )

    @property
    def winning_team(self) -> str:
        if self.cards_found.get("B", 0) > 0:
            return "Moriarty", "The bomb has been triggered."

        if self.nb_players and self.cards_found.get("D", 0) == self.nb_players:
            return "Sherlock", "The bomb has been fully defused."

        if self.cards_left and sum(self.cards_left.values()) <= self.nb_players:
            return "Moriarty", "The bomb has not been defused in time."

    @property
    def status(self) -> str:
        if self.nb_players < magics.MIN_PLAYERS:
            return "WAITING"

        if self.nb_players >= magics.MIN_PLAYERS and not self.cards_left:
            return "READY"

        if self.winning_team:
            return "ENDED"

        if self.cards_left:
            return "PLAYING"
