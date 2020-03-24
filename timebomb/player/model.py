from dataclasses import dataclass


@dataclass
class Player:
    name: str
    id: str
    roomid: str
    team: str = None
    hand: list = None
