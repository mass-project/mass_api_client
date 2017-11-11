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
        Create a new :class:`AnalysisSystemInstance` on the server.

        For convenience
        :func:`~mass_api_client.resources.analysis_system.AnalysisSystem.create_analysis_system_instance`
        of class :class:`.AnalysisSystem` can be used instead.

        :param analysis_system: The corresponding :class:`.AnalysisSystem` object
        :return: The created :class:`AnalysisSystemInstance` object
        """
        return cls._create(analysis_system=analysis_system.url)

    def schedule_analysis(self, sample):
        """
        Schedule the given sample for this instance on the server.

        :param sample: The sample object to be scheduled.
        :return: The created :class:`.ScheduledAnalysis` object.
        """
        return ScheduledAnalysis.create(self, sample)

    def get_scheduled_analyses(self):
        """
        Retrieve all scheduled analyses for this instance.

        :return: A list of :class:`.ScheduledAnalysis` objects.
        """
        url = '{}scheduled_analyses/'.format(self.url)
        return ScheduledAnalysis._get_list_from_url(url, append_base_url=False)

    def get_analysis_system(self):
        """
        Retrieve the corresponding :class:`AnaylsisSystem` object from the server.

        :return: The retrieved object.
        """
        from .analysis_system import AnalysisSystem
        return AnalysisSystem._get_detail_from_url(self.analysis_system, append_base_url=False)

    def __repr__(self):
        return '[AnalysisSystemInstance] {}'.format(self.uuid)

    def __str__(self):
        return self.__repr__()
