import socketio

from timebomb.player.service import PlayerService
from timebomb.player.schema import PlayerSchema

from timebomb.room.service import RoomService
from timebomb.room.schema import RoomSchema, EndedRoomSchema


class MainNamespace(socketio.Namespace):
    def emit_room(self, room):
        schema = RoomSchema()
        json = schema.dump(room)
        self.emit("room", json, room=room.id)
        return json

    def emit_player(self, player):
        schema = PlayerSchema()
        json = schema.dump(player)
        self.emit("player", json, room=player.id)
        return json

    def emit_end(self, room):
        schema = EndedRoomSchema()
        json = schema.dump(room)
        self.emit("end", json, room=room.id)
        return json

    def emit_chat(self, room, data):
        self.emit("chat", data, room=room.id)
        return data

    def emit_notify(self, room, data):
        self.emit("notify", data, room=room.id)
        return data

    def on_login(self, sid: str, data: dict) -> dict:
        player = PlayerService.get_by_id(sid)

        if player:
            return {"status": "ERROR", "data": {"message": "Player already logged in."}}

        username = data.get("username")
        room_name = data.get("roomname")

        if not username:
            return {"status": "ERROR", "data": {"message": "Invalid username."}}

        player = PlayerService.create({"name": username[:11], "id": sid})

        if not room_name:
            open_rooms = RoomService.get_open_rooms()
            if not len(open_rooms):
                room = RoomService.create_random()
            else:
                room = open_rooms[0]
        else:
            room = RoomService.get_by_name(room_name)
            if not room:
                room = RoomService.create(room_name)

        player = RoomService.add_player(room, player)
        if not player:
            return {
                "status": "ERROR",
                "data": {"message": "Impossible to join this room."},
            }

        self.enter_room(sid, room.id)
        json = self.emit_room(room)
        return {"status": "SUCCESS", "data": json}

    def on_cut(self, sid: str, data: dict) -> dict:
        target_id = data.get("target")
        target_player = PlayerService.get_by_id(target_id)

        if not target_player:
            return {"status": "ERROR", "data": {"message": "Invalid target id."}}

        src_player = PlayerService.get_by_id(sid)
        if not src_player:
            return {"status": "ERROR", "data": {"message": "Player not logged in."}}

        if src_player.room_id != target_player.room_id:
            return {
                "status": "ERROR",
                "data": {"message": "Can not cut player from other room."},
            }

        room = RoomService.get_by_id(target_player.room_id)
        if not room:
            return {"status": "ERROR", "data": {"message": "Invalid room."}}

        card = RoomService.cut_card(room, src_player, target_player)
        if not card:
            return {"status": "ERROR", "data": {"message": "Error while cutting."}}

        if room.status == "ENDED":
            json = self.emit_end(room)
            return {"status": "SUCCESS", "data": json}

        res = RoomService.distribute_cards(room)
        if res:
            for player in room.players:
                self.emit_player(player)

        self.emit_notify(target_player, {"message": "Your turn to cut a card!"})
        self.emit_player(target_player)
        json = self.emit_room(room)
        return {"status": "SUCCESS", "data": json}

    def on_start(self, sid: str) -> dict:
        player = PlayerService.get_by_id(sid)

        if not player:
            return {"status": "ERROR", "data": {"message": "Player not logged in."}}

        room = RoomService.get_by_id(player.room_id)
        if not room:
            return {"status": "ERROR", "data": {"message": "Invalid room."}}

        res = RoomService.start(room)
        if not res:
            return {
                "status": "ERROR",
                "data": {"message": "Can not start game in this room."},
            }

        for player in room.players:
            self.emit_player(player)

        json = self.emit_room(room)
        return {"status": "SUCCESS", "data": json}

    def on_chat(self, sid: str, data: dict) -> dict:
        player = PlayerService.get_by_id(sid)

        if not player:
            return {"status": "ERROR", "data": {"message": "Player not logged in."}}

        room = RoomService.get_by_id(player.room_id)
        if not room:
            return {"status": "ERROR", "data": {"message": "Invalid room."}}

        message = data.get("message", "").strip()
        if not message:
            return {"status": "ERROR", "data": {"message": "Invalid data."}}

        data = {"player": player.name, "message": message}
        json = self.emit_chat(room, data)
        return {"status": "SUCCESS", "data": json}

    def on_disconnect(self, sid: str) -> dict:
        player = PlayerService.get_by_id(sid)

        if not player:
            return {"status": "SUCCESS", "data": {"message": "Player disconnect."}}

        room = RoomService.get_by_id(player.room_id)
        if not room:
            return {"status": "SUCCESS", "data": {"message": "Player disconnect."}}

        if room.status == "PLAYING":
            self.emit_end(room)
            self.emit_notify(room, {"message": f"{player.name} has left the game."})
            for r_player in room.players:
                self.leave_room(r_player.id, room.id)
                room.players.remove(r_player)
                PlayerService.delete(r_player)
            RoomService.delete(room)

        else:
            self.leave_room(player.id, room.id)
            room.players.remove(player)
            if not len(room.players):
                RoomService.delete(room)

            PlayerService.delete(player)

        return {"status": "SUCCESS", "data": {"message": "Player disconnect."}}
