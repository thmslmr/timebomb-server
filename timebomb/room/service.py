import random

import numpy as np

from timebomb.room.model import Room
import timebomb.room.magics as magics

ROOMS = []


class RoomService:
    @staticmethod
    def get_by_id(id: str) -> Room:
        for room in ROOMS:
            if room.id == id:
                return room

    @staticmethod
    def get_by_name(name: str) -> Room:
        for room in ROOMS:
            if room.name == name:
                return room

    @staticmethod
    def get_open_rooms() -> list:
        return [room for room in ROOMS if room.is_open]

    @staticmethod
    def update(room: Room, changes: dict) -> Room:
        room.__dict__.update(changes)
        return room

    @staticmethod
    def delete(room: Room) -> int:
        id = room.id
        ROOMS.remove(room)
        return id

    @staticmethod
    def create(name: str) -> Room:
        hash = random.getrandbits(128)
        room_id = f"{hash:032X}"

        new_room = Room(name=name, id=room_id)
        ROOMS.append(new_room)

        return new_room

    @staticmethod
    def create_random() -> Room:
        noun = random.choice(magics.NOUNS)
        adjective = random.choice(magics.ADJECTIVES)

        name = f"{adjective}-{noun}"
        new_room = RoomService.create(name)
        return new_room

    @staticmethod
    def start(room: Room) -> Room:
        if room.status != "READY":
            return

        cards_left = magics.NBPLAYER_TO_DECK[room.nb_players].copy()
        cards_found = {"B": 0, "D": 0, "N": 0}

        roles = magics.NBPLAYER_TO_ROLES[room.nb_players].copy()
        roles_lst = np.repeat(list(roles.keys()), list(roles.values()))
        np.random.shuffle(roles_lst)

        if len(roles_lst) > room.nb_players:
            roles_lst = roles_lst[1:]

        assert len(roles_lst) == len(room.players)

        RoomService.update(
            room,
            {
                "cards_left": cards_left,
                "cards_found": cards_found,
                "cutter": room.players[0],
            },
        )

        RoomService.distribute_cards(room)

        for i, role in enumerate(roles_lst):
            room.players[i].team = role

        return True

    @staticmethod
    def distribute_cards(room: Room) -> Room:
        if room.status not in ["PLAYING", "READY"]:
            return

        if sum(room.cards_left.values()) % room.nb_players != 0:
            return

        left_lst = np.repeat(
            list(room.cards_left.keys()), list(room.cards_left.values())
        )

        np.random.shuffle(left_lst)
        hands = np.split(left_lst, room.nb_players)

        for i, hand in enumerate(hands):
            room.players[i].hand = hand

        return True

    @staticmethod
    def cut_card(room: Room, from_player, to_player) -> Room:
        if room.status != "PLAYING":
            return

        if from_player is not room.cutter:
            return

        if from_player is to_player:
            return

        np.random.shuffle(to_player.hand)
        cutted = to_player.hand[0]
        to_player.hand = to_player.hand[1:]

        room.cards_found[cutted] += 1
        room.cards_left[cutted] -= 1

        room.cutter = to_player

        return cutted

    @staticmethod
    def add_player(room: Room, player) -> tuple:
        if not room.is_open:
            return

        if room.nb_players >= magics.MAX_PLAYERS:
            return

        room.players.append(player)
        player.room_id = room.id

        return True
