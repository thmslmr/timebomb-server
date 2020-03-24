from flask import request, jsonify
from flask_restplus import Namespace, Resource
from flask.wrappers import Response

from timebomb.player.service import PlayerService
from timebomb.player.schema import PlayerSchema
from timebomb.player.model import Player
from timebomb.player.interface import PlayerInterface

PlayerAPI = Namespace("player")


@PlayerAPI.route("/")
class PlayerResource(Resource):
    """Player."""

    def get(self) -> list:
        """Get all players."""
        schema: PlayerSchema = PlayerSchema(many=True, only=("name", "id"))
        return schema.dump(PlayerService.get_all())

    def post(self) -> Player:
        """Create a new player."""
        schema: PlayerSchema = PlayerSchema()
        player: Player = schema.load(request.form)
        new_player: Player = PlayerService.create(player)
        return schema.dump(new_player)


@PlayerAPI.route("/<int:id>")
@PlayerAPI.param("id", "Player database ID")
class PlayerIdResource(Resource):
    def get(self, id: str) -> Player:
        """Get player by its ID"""
        player: Player = PlayerService.get_by_id(id)
        schema: PlayerSchema = PlayerSchema(only=("name", "id"))
        return schema.dump(player)

    def delete(self, id: str) -> Response:
        """Delete player by its ID"""
        id = PlayerService.delete(id)
        return jsonify({"id": id})

    def put(self, id: str) -> Player:
        """Update player by its ID"""
        changes: PlayerInterface = PlayerInterface(request.form)
        player: Player = PlayerService.get_by_id(id)
        new_player: Player = PlayerService.update(player, changes)
        schema: PlayerSchema = PlayerSchema(only=("name", "id"))
        return schema.dump(new_player)
