from marshmallow import fields

from .base import BaseSchema


class ReportSchema(BaseSchema):
    analysis_system = fields.Url(required=True)
    sample = fields.Url(required=True)
    analysis_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S.%f+00:00')
    upload_date = fields.DateTime(required=True)
    # TODO: Check for correct status code: status = fields.Int(validate=validate.OneOf(Report.REPORT_STATUS_CODES))
    status = fields.Int()
    error_message = fields.Str(allow_none=True)
    tags = fields.List(cls_or_instance=fields.Str)
    additional_metadata = fields.Dict()
    json_report_objects = fields.Dict()
    raw_report_objects = fields.Dict()
