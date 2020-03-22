class Player:
    """Player model."""

    __slots__ = ["name", "sid", "hand", "role", "is_cutting"]

    def __init__(self, name: str, sid: str):
        self.name = name
        self.sid = sid

        self.hand = []
        self.role = None
        self.is_cutting = False

    @property
    def public_state(self) -> dict:
        """Get infos seen by other players.

        Returns:
            dict: player public state.

        """
        return {"name": self.name, "sid": self.sid, "is_cutting": self.is_cutting}
