from mass_api_client.schemas import AnalysisSystemInstanceSchema
from .base import BaseResource
from .scheduled_analysis import ScheduledAnalysis


class AnalysisSystemInstance(BaseResource):
    schema = AnalysisSystemInstanceSchema()
    _endpoint = 'analysis_system_instance'
    _creation_point = _endpoint

    @classmethod
    def create(cls, analysis_system):
        """
        Create a new `AnalysisSystemInstance` on the server.

        For convenience `AnalysisSystem.create_analysis_system_instance()` can be used instead.

        :param analysis_system: The corresponding `AnalysisSystem` object
        :return: The created `AnalysisSystemInstance` object
        """
        return cls._create(analysis_system=analysis_system.url)

    def schedule_analysis(self, sample):
        """
        Schedule the given sample for this instance on the server.

        :param sample: The sample object to be scheduled.
        :return: The created `ScheduledAnalysis` object.
        """
        return ScheduledAnalysis.create(self, sample)

    def get_scheduled_analyses(self):
        """
        Retrieve all scheduled analyses for this instance.

        :return: A list of `AnalysisSystemInstance` objects.
        """
        url = '{}scheduled_analyses/'.format(self.url)
        return ScheduledAnalysis._get_list_from_url(url, append_base_url=False)

    def __repr__(self):
        return '[AnalysisSystemInstance] {}'.format(self.uuid)

    def __str__(self):
        return self.__repr__()
