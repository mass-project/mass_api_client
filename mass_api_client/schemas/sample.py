from marshmallow import fields

from .base import BaseSchema


class SampleSchema(BaseSchema):
    delivery_dates = fields.List(cls_or_instance=fields.DateTime)
    first_seen = fields.DateTime()
    tags = fields.List(cls_or_instance=fields.Str)
    dispatched_to = fields.List(cls_or_instance=fields.Str)
    tlp_level = fields.Int(required=True)
    unique_features = fields.Dict()

