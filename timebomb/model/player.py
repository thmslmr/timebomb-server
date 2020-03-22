class Player:
    """Player model."""

    __slots__ = ["name", "sid", "hand", "role", "roomname"]

    def __init__(self, name: str, sid: str):
        self.name = name
        self.sid = sid

        self.hand = []
        self.role = None
        self.roomname = None

    @property
    def public_state(self) -> dict:
        """Get infos seen by other players.

        Returns:
            dict: player public state.

        """
        return {"name": self.name, "sid": self.sid}
