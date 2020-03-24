from timebomb.player.model import Player
from timebomb.player.interface import PlayerInterface

PLAYERS = []


class PlayerService:
    @staticmethod
    def get_all() -> list:
        return PLAYERS.copy()

    @staticmethod
    def get_by_id(player_id: str) -> Player:
        for player in PLAYERS:
            if player.id == player_id:
                return player

    @staticmethod
    def update(player: Player, changes: PlayerInterface) -> Player:
        player.__dict__.update(changes)
        return player

    @staticmethod
    def delete(player: Player) -> int:
        id = player.id
        PLAYERS.remove(player)
        return id

    @staticmethod
    def create(new_attrs: PlayerInterface) -> Player:
        new_player = Player(**new_attrs)
        PLAYERS.append(new_player)
        return new_player
