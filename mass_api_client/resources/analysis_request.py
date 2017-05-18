from mass_api_client.schemas import AnalysisRequestSchema
from .sample import Sample
from mass_api_client.resources.base import BaseResource


class AnalysisRequest(BaseResource):
    schema = AnalysisRequestSchema()
    endpoint = 'analysis_request'
    creation_point = endpoint

    @classmethod
    def create(cls, sample, analysis_system):
        return cls._create(sample=sample.url, analysis_system=analysis_system.url)
