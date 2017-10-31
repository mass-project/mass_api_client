from marshmallow import fields, Schema
from marshmallow.validate import Regexp, Range, Length

from .base import BaseSchema


class FileFeatureSchema(Schema):
    file_names = fields.List(cls_or_instance=fields.Str)
    file_size = fields.Integer(required=True)
    magic_string = fields.String(required=True)
    mime_type = fields.String(required=True)
    md5sum = fields.String(validate=Length(min=32, max=32), required=True)
    sha1sum = fields.String(validate=Length(min=40, max=40), required=True)
    sha256sum = fields.String(validate=Length(min=64, max=64), required=True)
    sha512sum = fields.String(validate=Length(min=128, max=128), required=True)
    ssdeep_hash = fields.String(validate=Length(max=200), required=True)
    shannon_entropy = fields.Float(validate=Range(min=0, max=8), required=True)


class UniqueSampleFeaturesSchema(Schema):
    file = fields.Nested(FileFeatureSchema)
    ipv4 = fields.String(validate=Regexp(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'))
    ipv6 = fields.String(validate=Regexp(r'([0-9a-f]{1,4}:{0,2}){1,8}'))
    port = fields.Integer(validate=Range(min=0, max=65535))
    domain = fields.String()
    uri = fields.String(validate=Regexp(r'\w+://.*'))
    custom_unique_feature = fields.String()


class SampleSchema(BaseSchema):
    delivery_dates = fields.List(cls_or_instance=fields.DateTime)
    first_seen = fields.DateTime()
    tags = fields.List(cls_or_instance=fields.Str)
    dispatched_to = fields.List(cls_or_instance=fields.Str)
    tlp_level = fields.Int(required=True)
    unique_features = fields.Nested(UniqueSampleFeaturesSchema)

