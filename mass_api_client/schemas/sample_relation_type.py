from marshmallow import fields

from .base import BaseSchema


class SampleRelationTypeSchema(BaseSchema):
    name = fields.String(required=True)
    directed = fields.Boolean(required=True)
    description = fields.String()