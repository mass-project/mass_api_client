from mass_api_client.schemas import ScheduledAnalysisSchema
from .base import BaseResource
from .report import Report
from .sample import Sample
import datetime


class ScheduledAnalysis(BaseResource):
    schema = ScheduledAnalysisSchema()
    endpoint = 'scheduled_analysis'
    creation_point = endpoint

    @classmethod
    def create(cls, analysis_system_instance, sample):
        """
        Create a new `ScheduledAnalysis` on the server.

        For convenience `AnalysisSystemInstance.schedule_analysis(sample)` can be used instead.

        :param analysis_system_instance: The `AnalysisSystemInstance` for which the sample should be scheduled.
        :param sample: The sample object to be scheduled.
        :return: The created `ScheduledAnalysis` object.
        """
        return cls._create(analysis_system_instance=analysis_system_instance.url, sample=sample.url)

    def create_report(self, analysis_date=datetime.datetime.now(), json_report_objects=None, raw_report_objects=None, tags=None):
        """
        Create a report and remove the ScheduledAnalysis from the server.

        :param json_report_objects: A dictionary of JSON reports, where the key is the object name.
        :param raw_report_objects: A dictionary of binary file reports, where the key is the file name.
        :param tags: A list of strings.
        :param analysis_date: datetime object of the time the report was generated. Defaults to current time.
        :return: The created report object.
        """
        return Report.create(self, json_report_objects=json_report_objects, raw_report_objects=raw_report_objects, tags=tags, analysis_date=analysis_date)

    def get_sample(self):
        """
        Retrieve the scheduled sample.

        :return: The corresponding `Sample` object.
        """
        sample_url = self.sample
        sample = Sample._get_detail_from_url(sample_url, append_base_url=False)
        return sample
