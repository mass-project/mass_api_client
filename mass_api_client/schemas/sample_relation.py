from marshmallow import fields, validate

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

class DroppedBySampleRelationSchema(SampleRelationSchema):
    _cls = fields.Str(validate=validate.Equal("SampleRelation.DroppedBySampleRelation"))


class ResolvedBySampleRelationSchema(SampleRelationSchema):
    _cls = fields.Str(validate=validate.Equal("SampleRelation.ResolvedBySampleRelation"))


class ContactedBySampleRelationSchema(SampleRelationSchema):
    _cls = fields.Str(validate=validate.Equal("SampleRelation.ContactedBySampleRelation"))


class RetrievedBySampleRelationSchema(SampleRelationSchema):
    _cls = fields.Str(validate=validate.Equal("SampleRelation.RetrievedBySampleRelation"))


class SsdeepSampleRelationSchema(SampleRelationSchema):
    _cls = fields.Str(validate=validate.Equal("SampleRelation.SsdeepSampleRelation"))
    match = fields.Float(validate=validate.Range(min=0, max=100), required=True)
