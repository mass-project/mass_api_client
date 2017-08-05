from mass_api_client.schemas import ScheduledAnalysisSchema
from .base import BaseResource
from .report import Report
from .sample import Sample


class ScheduledAnalysis(BaseResource):
    schema = ScheduledAnalysisSchema()
    _endpoint = 'scheduled_analysis'
    _creation_point = _endpoint

    @classmethod
    def create(cls, analysis_system_instance, sample):
        """
        Create a new :class:`ScheduledAnalysis` on the server.

        For convenience
        :func:`~mass_api_client.resources.analysis_system_instance.AnalysisSystemInstance.schedule_analysis`
        of class :class:`.AnalysisSystemInstance` can be used instead.

        :param analysis_system_instance: The :class:`.AnalysisSystemInstance` for which the sample should be scheduled.
        :param sample: The class:`.Sample` object to be scheduled.
        :return: The created :class:`ScheduledAnalysis` object.
        """
        return cls._create(analysis_system_instance=analysis_system_instance.url, sample=sample.url)

    def create_report(self, additional_metadata=None, json_report_objects=None, raw_report_objects=None, tags=None, analysis_date=None, failed=False, error_message=None):
        """
        Create a :class:`.Report` and remove the :class:`ScheduledAnalysis` from the server.

        :param additional_metadata: A dictionary of additional metadata.
        :param json_report_objects: A dictionary of JSON reports, where the key is the object name.
        :param raw_report_objects: A dictionary of binary file reports, where the key is the file name.
        :param tags: A list of strings.
        :param analysis_date: :py:mod:`datetime` object of the time the report was generated. Defaults to current time.
        :return: The created :class:`.Report` object.
        """
        return Report.create(self, json_report_objects=json_report_objects, raw_report_objects=raw_report_objects, additional_metadata=additional_metadata, tags=tags, analysis_date=analysis_date, failed=failed, error_message=error_message)

    def get_sample(self):
        """
        Retrieve the scheduled :class:`.Sample`.

        :return: The corresponding :class:`.Sample` object.
        """
        sample_url = self.sample
        sample = Sample._get_detail_from_url(sample_url, append_base_url=False)
        return sample
