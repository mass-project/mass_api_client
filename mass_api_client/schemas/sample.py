from marshmallow import fields, validate

from .base import BaseSchema


class SampleSchema(BaseSchema):
    delivery_date = fields.DateTime()
    first_seen = fields.DateTime()
    tags = fields.List(cls_or_instance=fields.Str)
    dispatched_to = fields.List(cls_or_instance=fields.Str)
    tlp_level = fields.Int(required=True)
    unique_features = fields.Dict()

