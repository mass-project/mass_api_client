from mass_api_client.connection_manager import ConnectionManager
from mass_api_client.schemas import ReportSchema
from .base import BaseResource


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
    def create(cls, scheduled_analysis, tags=None, json_report_objects=None, raw_report_objects=None, additional_metadata=None):
        """
        Create a new report.

        For convenience `ScheduledAnalysis.create_report()` can be used instead.

        :param scheduled_analysis: The `ScheduledAnalysis` this report was created for
        :param tags: A list of strings
        :param json_report_objects: A dictionary of JSON reports, where the key is the object name.
        :param raw_report_objects: A dictionary of binary file reports, where the key is the file name.
        :return: The newly created report object
        """
        if tags is None:
            tags = []

        if additional_metadata is None:
            additional_metadata = {}

        url = cls.creation_point.format(scheduled_analysis=scheduled_analysis.id)
        return cls._create(url=url, additional_json_files=json_report_objects,
                           additional_binary_files=raw_report_objects, tags=tags,
                           additional_metadata=additional_metadata, force_multipart=True)

    def get_json_report_object(self, key):
        """
        Retrieve a JSON report object of the report.

        :param key: The key of the report object
        :return: The deserialized JSON report object.
        """
        cm = ConnectionManager()
        return cm.get_json(self.json_report_objects[key], append_base_url=False)

    def download_raw_report_object_to_file(self, key, file):
        """
        Download a raw report object and store it in a file.

        :param key: The key of the report object
        :param file: A `file` object to store the report object.
        """
        cm = ConnectionManager()
        cm.download_to_file(self.raw_report_objects[key], file, append_base_url=False)
