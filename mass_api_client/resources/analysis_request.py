from mass_api_client.resources.base import BaseResource
from mass_api_client.schemas import AnalysisRequestSchema


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    endpoint = 'analysis_request'
    creation_point = endpoint

    @classmethod
    def create(cls, sample, analysis_system, priority=0, parameters=None):
        """
        Create a new `AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param analysis_system: The `AnalysisSystem` that should be used for the analysis.
        :param priority: The priority with which the request should be scheduled.
        :param parameters: Analysis system specific parameters.
        :return: The created `AnalysisRequest` object.
        """
        return cls._create(sample=sample.url, analysis_system=analysis_system.url, priority=priority, parameters=parameters)
