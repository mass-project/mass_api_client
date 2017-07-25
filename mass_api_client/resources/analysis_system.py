from mass_api_client.schemas import AnalysisSystemSchema
from .analysis_request import AnalysisRequest
from .analysis_system_instance import AnalysisSystemInstance
from .base import BaseResource


class AnalysisSystem(BaseResource):
    schema = AnalysisSystemSchema()
    _endpoint = 'analysis_system'
    _creation_point = _endpoint

    _filter_parameters = ['identifier_name', 'identifier_name__contains', 'verbose_name__contains', 'verbose_name']

    @classmethod
    def create(cls, identifier_name, verbose_name, tag_filter_expression=''):
        """
        Create a new :class:`AnalysisSystem` on the server.

        :param identifier_name: Unique identifier string.
        :param verbose_name: A descriptive name of the AnalysisSystem.
        :param tag_filter_expression: Tag filters to automatically select samples for this AnalysisSystem.
        :return: The created :class:`AnalysisSystem` object.
        """
        return cls._create(identifier_name=identifier_name, verbose_name=verbose_name, tag_filter_expression=tag_filter_expression)

    def create_request(self, sample, priority=0, parameters=None):
        """
        Create a new `AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param priority: The priority with which the request should be scheduled.
        :param parameters: Analysis system specific parameters.
        :return: The created `AnalysisRequest` object.
        """
        return AnalysisRequest.create(sample, self, priority, parameters)

    def create_analysis_system_instance(self):
        """
        Create an instance of this AnalysisSystem on the server.

        :return: The created :class:`AnalysisSystemInstance` object.
        """
        return AnalysisSystemInstance.create(analysis_system=self)

    def __repr__(self):
        return '[AnalysisSystem] {}'.format(self.identifier_name)

    def __str__(self):
        return self.__repr__()
