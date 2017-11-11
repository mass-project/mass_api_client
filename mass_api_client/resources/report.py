import datetime

from mass_api_client.connection_manager import ConnectionManager
from mass_api_client.schemas import ReportSchema
from .base import BaseResource


class Report(BaseResource):
    REPORT_STATUS_CODE_OK = 0
    REPORT_STATUS_CODE_FAILURE = 1

    REPORT_STATUS_CODES = [REPORT_STATUS_CODE_OK, REPORT_STATUS_CODE_FAILURE]

    schema = ReportSchema()
    _endpoint = 'report'
    _creation_point = 'scheduled_analysis/{scheduled_analysis}/submit_report/'

    def __init__(self, connection_alias, **kwargs):
        super(Report, self).__init__(connection_alias, **kwargs)
        self._json_reports_cache = None

    def __repr__(self):
        return '[Report] {} on {}'.format(self.sample, self.analysis_system)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create(cls, scheduled_analysis, tags=None, json_report_objects=None, raw_report_objects=None, additional_metadata=None, analysis_date=None, failed=False, error_message=None):
        """
        Create a new report.

        For convenience :func:`~mass_api_client.resources.scheduled_analysis.ScheduledAnalysis.create_report`
        of class :class:`.ScheduledAnalysis` can be used instead.

        :param scheduled_analysis: The :class:`.ScheduledAnalysis` this report was created for
        :param tags: A list of strings
        :param json_report_objects: A dictionary of JSON reports, where the key is the object name.
        :param raw_report_objects: A dictionary of binary file reports, where the key is the file name.
        :param analysis_date: A datetime object of the time the report was generated. Defaults to current time.
        :return: The newly created report object
        """
        if tags is None:
            tags = []

        if additional_metadata is None:
            additional_metadata = {}

        if analysis_date is None:
            analysis_date = datetime.datetime.now()

        url = cls._creation_point.format(scheduled_analysis=scheduled_analysis.id)
        return cls._create(url=url, analysis_date=analysis_date, additional_json_files=json_report_objects,
                           additional_binary_files=raw_report_objects, tags=tags,
                           additional_metadata=additional_metadata, status=int(failed), error_message=error_message, force_multipart=True)

    @property
    def json_reports(self):
        if self._json_reports_cache:
            return self._json_reports_cache

        self._json_reports_cache = {}
        for key in self.json_report_objects.keys():
            self._json_reports_cache[key] = self.get_json_report_object(key)
        return self._json_reports_cache

    def get_json_report_object(self, key):
        """
        Retrieve a JSON report object of the report.

        :param key: The key of the report object
        :return: The deserialized JSON report object.
        """
        con = ConnectionManager().get_connection(self._connection_alias)
        return con.get_json(self.json_report_objects[key], append_base_url=False)

    def download_raw_report_object_to_file(self, key, file):
        """
        Download a raw report object and store it in a file.

        :param key: The key of the report object
        :param file: A file-like object to store the report object.
        """
        con = ConnectionManager().get_connection(self._connection_alias)
        return con.download_to_file(self.raw_report_objects[key], file, append_base_url=False)

    def get_analysis_system(self):
        """
        Retrieve the corresponding :class:`AnaylsisSystem` object from the server.

        :return: The retrieved object.
        """
        from .analysis_system import AnalysisSystem
        return AnalysisSystem._get_detail_from_url(self.analysis_system, append_base_url=False)
