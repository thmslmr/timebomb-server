import random

from timebomb.model import magics
from timebomb.model.room import Room


class Arena:
    """Arena model."""

    def __init__(self):
        """Create empty rooms list."""
        self.rooms = []

    @property
    def open_rooms(self) -> list:
        """Get list of open rooms.

        Returns:
            list: List of open rooms in arena.

        """
        return [room for room in self.rooms if room.is_open]

    def create_random_room(self) -> Room:
        """Create a random room.

        Returns:
            Room: The newly created room.

        """
        noun = random.choice(magics.NOUNS)
        adjective = random.choice(magics.ADJECTIVES)
        roomhash = random.getrandbits(16)
        roomname = f"{adjective}-{noun}-{roomhash:x}"

        room = self.create_room(roomname)

        return room

    def create_room(self, roomname: str) -> Room:
        """Create specific room.

        Args:
            roomname (str): The room name.

        Returns:
            Room: The newly created room or None if room already exist.

        """
        if roomname in self.rooms:
            return

        room = Room(roomname)
        self.rooms.append(room)

        return room

    def get_room(self, roomname: str) -> Room:
        """Get a room by its name.

        Args:
            roomname (str): The room name.

        Returns:
            Room: The first found room with this name or None if not found.

        """
        for room in self.rooms:
            if room.name == roomname:
                return room

    def get_player(self, sid: str) -> object:
        """Get player object by its sid among all rooms.

        Args:
            sid (str): The player sid.

        Returns:
            object: Player object found if exists, else None.

        """
        for room in self.rooms:
            player = room.get_player(sid)
            if player:
                return player

    def join_room(self, player: object, roomname: str = None) -> Room:
        """Add player to a room.

        If no room name specify, create a new random one or join an existing open one.
        If room name, create of join is open.

        Args:
            player (object): The player to add.
            roomname (str): The name of the room to join.

        Returns:
            Room: The room entered or None if target room is not open.

        """
        if roomname:
            target_room = self.get_room(roomname)
            if not target_room:
                target_room = self.create_room(roomname)
        elif len(self.open_rooms) > 0:
            target_room = self.open_rooms[0]
        else:
            target_room = self.create_random_room()

        if target_room.is_open:
            target_room.add_player(player)

            return target_room
