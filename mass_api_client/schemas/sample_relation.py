from marshmallow import fields

from .base import BaseSchema


class SampleRelationTypeSchema(BaseSchema):
    name = fields.String(required=True)
    directed = fields.Boolean(required=True)
    description = fields.String()


class SampleRelationSchema(BaseSchema):
    sample = fields.Url(required=True)
    other = fields.Url(required=True)
    relation_type = fields.Url(required=True)
    additional_metadata = fields.Dict()
    tags = fields.List(cls_or_instance=fields.Str)
