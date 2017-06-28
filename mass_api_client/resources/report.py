from mass_api_client.connection_manager import ConnectionManager
from mass_api_client.schemas import ReportSchema
from .base import BaseResource
import datetime


class Report(BaseResource):
    REPORT_STATUS_CODE_OK = 0
    REPORT_STATUS_CODE_FAILURE = 1

    REPORT_STATUS_CODES = [REPORT_STATUS_CODE_OK, REPORT_STATUS_CODE_FAILURE]

    schema = ReportSchema()
    endpoint = 'report'
    creation_point = 'scheduled_analysis/{scheduled_analysis}/submit_report/'

    def __repr__(self):
        return '[Report] {} on {}'.format(self.sample, self.analysis_system)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create(cls, scheduled_analysis, tags=None, json_report_objects=None, raw_report_objects=None, additional_metadata=None, analysis_date=None):
        if tags is None:
            tags = []

        if additional_metadata is None:
            additional_metadata = {}

        if analysis_date is None:
            analysis_date = datetime.datetime.now()

        url = cls.creation_point.format(scheduled_analysis=scheduled_analysis.id)
        return cls._create(url=url, analysis_date=analysis_date, additional_json_files=json_report_objects,
                           additional_binary_files=raw_report_objects, tags=tags,
                           additional_metadata=additional_metadata, force_multipart=True)

    def get_json_report_object(self, key):
        cm = ConnectionManager()
        return cm.get_json(self.json_report_objects[key], append_base_url=False)

    def download_raw_report_object_to_file(self, key, file):
        cm = ConnectionManager()
        return cm.download_to_file(self.raw_report_objects[key], file, append_base_url=False)
