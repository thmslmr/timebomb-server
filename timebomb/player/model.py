from dataclasses import dataclass, field


@dataclass
class Player:
    """Player Model.

    Attributes:
        name (str): The player name.
        id (str): The player ID (socket ID).
        room_id (str): Locate in which room the player is.

        team (str): The player team. None before the game starts.
        hand (str): The player list of cards. None before the game starts.

    """

    name: str
    id: str
    room_id: str = None

    team: str = None
    hand: list = field(default_factory=list)
