from marshmallow import fields, Schema


class PlayerSchema(Schema):
    name = fields.String(attribute="name", required=True)
    id = fields.String(attribute="id", required=True)
    roomId = fields.String(attribute="roomid")
    team = fields.String(attribute="team")
    hand = fields.List(fields.String, attribute="hand")
