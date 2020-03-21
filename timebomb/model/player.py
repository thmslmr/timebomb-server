class Player:
    """Player model."""

    __slots__ = ["username", "sid"]

    def __init__(self, username, sid):  # noqa
        self.username = username
        self.sid = sid
