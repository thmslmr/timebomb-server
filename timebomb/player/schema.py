from marshmallow import fields, Schema


class PlayerSchema(Schema):
    """Player serialization schema."""

    name = fields.String(attribute="name")
    id = fields.String(attribute="id")
    roomId = fields.String(attribute="room_id")
    team = fields.String(attribute="team")
    hand = fields.List(fields.String, attribute="hand")
