import socketio

from timebomb.player.service import PlayerService
from timebomb.player.schema import PlayerSchema
from timebomb.player.model import Player


class PlayerEmitter:
    @staticmethod
    def error(message, sid, sio):
        sio.emit({"error": message}, room=sid)


class PlayerNamespace(socketio.Namespace):
    def on_create(self, sid, data):
        schema: PlayerSchema = PlayerSchema()
        player: Player = schema.load(data)
        PlayerService.create(player)

    def on_disconnect(self, sid):
        pass

    def on_state(self, sid, data):
        self.emit("my_response", data)


# sio.register_namespace(PlayerNamespace("/player"))
b
