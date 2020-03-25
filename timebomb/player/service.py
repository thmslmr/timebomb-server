from timebomb.player.model import Player

PLAYERS = []


class PlayerService:
    @staticmethod
    def get_by_id(id: str) -> Player:
        for player in PLAYERS:
            if player.id == id:
                return player

    @staticmethod
    def update(player: Player, changes: dict) -> Player:
        player.__dict__.update(changes)
        return player

    @staticmethod
    def delete(player: Player) -> int:
        id = player.id
        PLAYERS.remove(player)
        return id

    @staticmethod
    def create(new_attrs: dict) -> Player:
        new_player = Player(**new_attrs)
        PLAYERS.append(new_player)
        return new_player
