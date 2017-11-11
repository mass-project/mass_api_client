from mass_api_client.resources.base import BaseResource
from mass_api_client.schemas import AnalysisRequestSchema
from .analysis_system import AnalysisSystem


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    _endpoint = 'analysis_request'
    _creation_point = _endpoint

    @classmethod
    def create(cls, sample, analysis_system):
        """
        Create a new :class:`.AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param analysis_system: The :class:`AnalysisSystem` that should be used for the analysis.
        :return: The created :class:`AnalysisRequest` object.
        """
        return cls._create(sample=sample.url, analysis_system=analysis_system.url)

    def get_analysis_system(self):
        """
        Retrieve the corresponding :class:`AnaylsisSystem` object from the server.

        :return: The retrieved object.
        """
        return AnalysisSystem._get_detail_from_url(self.analysis_system, append_base_url=False)
