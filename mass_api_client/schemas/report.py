from marshmallow import fields

from .base import BaseSchema


class ReportSchema(BaseSchema):
    analysis_system = fields.Url(required=True)
    sample = fields.Url(required=True)
    analysis_date = fields.DateTime(allow_none=True)
    upload_date = fields.DateTime(required=True)
    status = fields.Int()
    error_message = fields.Str(allow_none=True)
    tags = fields.List(cls_or_instance=fields.Str)
    additional_metadata = fields.Dict()
    json_report_objects = fields.Dict()
    raw_report_objects = fields.Dict()
