from datetime import datetime

from mass_api_client.resources.base import BaseResource
from mass_api_client.schemas import AnalysisRequestSchema
from .analysis_system import AnalysisSystem
from .report import Report
from .sample import Sample


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    _endpoint = 'analysis_request'
    _creation_point = _endpoint

    _filter_parameters = ['analysis_requested__gte', 'analysis_requested__lte', 'analysis_system', 'priority',
                          'priority__gte', 'priority__lte', 'sample', 'schedule_after__gte', 'schedule_after__lte']

    @classmethod
    def create(cls, sample, analysis_system, schedule_after=None, priority=0, parameters=None):
        """
        Create a new :class:`.AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param analysis_system: The :class:`AnalysisSystem` that should be used for the analysis.
        :param schedule_after: The datetime after which the request should be scheduled. Uses now if None.
        :param priority: The priority with which the request should be scheduled.
        :param parameters: Analysis system specific parameters.
        :return: The created :class:`AnalysisRequest` object.
        """
        if not schedule_after:
            schedule_after = datetime.now()

        if not parameters:
            parameters = {}

        return cls._create(sample=sample.url, analysis_system=analysis_system.url, schedule_after=schedule_after,
                           priority=priority, parameters=parameters)

    def create_report(self, additional_metadata=None, json_report_objects=None, raw_report_objects=None, tags=None,
                      analysis_date=None, failed=False, error_message=None, report_queue=False):
        """
        Create a :class:`.Report` and remove the :class:`ScheduledAnalysis` from the server.

        :param additional_metadata: A dictionary of additional metadata.
        :param json_report_objects: A dictionary of JSON reports, where the key is the object name.
        :param raw_report_objects: A dictionary of binary file reports, where the key is the file name.
        :param tags: A list of strings.
        :param analysis_date: :py:mod:`datetime` object of the time the report was generated. Defaults to current time.
        :return: The created :class:`.Report` object.
        """
        return Report.create(self, json_report_objects=json_report_objects, raw_report_objects=raw_report_objects,
                             additional_metadata=additional_metadata, tags=tags, analysis_date=analysis_date,
                             failed=failed, error_message=error_message, use_queue=report_queue)

    def get_analysis_system(self):
        """
        Retrieve the corresponding :class:`AnaylsisSystem` object from the server.

        :return: The retrieved object.
        """
        return AnalysisSystem._get_detail_from_url(self.analysis_system, append_base_url=False)

    def get_sample(self):
        """
        Retrieve the scheduled :class:`.Sample`.

        :return: The corresponding :class:`.Sample` object.
        """
        sample_url = self.sample
        sample = Sample._get_detail_from_url(sample_url, append_base_url=False)
        return sample
