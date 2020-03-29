from marshmallow import fields, Schema

from timebomb.player.schema import PlayerSchema


class RoomSchema(Schema):
    """Room serialization schema."""

    name = fields.String(attribute="name")
    id = fields.String(attribute="id")

    players = fields.List(fields.Nested(PlayerSchema(only=("name", "id"))))
    cutter = fields.Nested(PlayerSchema(only=("name", "id")), allow_none=True)

    cards_found = fields.Dict(keys=fields.Str(), values=fields.Int())
    cards_left = fields.Dict(keys=fields.Str(), values=fields.Int())

    status = fields.String(attribute="status")


class EndedRoomSchema(Schema):
    """Ended Room serialization schema."""

    name = fields.String()
    id = fields.String()

    players = fields.List(fields.Nested(PlayerSchema(only=("name", "id", "team"))))

    winning_team = fields.List(fields.String())
