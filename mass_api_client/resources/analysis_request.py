from mass_api_client.resources.base import BaseResource
from mass_api_client.schemas import AnalysisRequestSchema
from .analysis_system import AnalysisSystem


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    _endpoint = 'analysis_request'
    _creation_point = _endpoint

    _filter_parameters = ['analysis_requested__gte', 'analysis_requested__lte', 'analysis_system', 'priority',
                          'priority__gte', 'priority__lte', 'sample']

    @classmethod
    def create(cls, sample, analysis_system, priority=0, parameters=None):
        """
        Create a new :class:`.AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param analysis_system: The :class:`AnalysisSystem` that should be used for the analysis.
        :param priority: The priority with which the request should be scheduled.
        :param parameters: Analysis system specific parameters.
        :return: The created :class:`AnalysisRequest` object.
        """
        if not parameters:
            parameters = {}

        return cls._create(sample=sample.url, analysis_system=analysis_system.url, priority=priority,
                           parameters=parameters)

    def get_analysis_system(self):
        """
        Retrieve the corresponding :class:`AnaylsisSystem` object from the server.

        :return: The retrieved object.
        """
        return AnalysisSystem._get_detail_from_url(self.analysis_system, append_base_url=False)
