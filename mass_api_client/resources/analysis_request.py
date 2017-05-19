from mass_api_client.resources.base import BaseResource
from mass_api_client.schemas import AnalysisRequestSchema


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    endpoint = 'analysis_request'
    creation_point = endpoint

    @classmethod
    def create(cls, sample, analysis_system):
        """
        Create a new `AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param analysis_system: The `AnalysisSystem` that should be used for the analysis.
        :return: The created `AnalysisRequest` object.
        """
        return cls._create(sample=sample.url, analysis_system=analysis_system.url)
