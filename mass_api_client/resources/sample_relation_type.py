from requests import HTTPError

from mass_api_client.resources import BaseResource
from mass_api_client.schemas import SampleRelationTypeSchema


class SampleRelationType(BaseResource):
    schema = SampleRelationTypeSchema()
    _endpoint = 'sample_relation_type'
    _creation_point = _endpoint

    filter_parameters = ['name']

    @classmethod
    def create(cls, name, directed):
        return cls._create(name=name, directed=directed)

    @classmethod
    def get_or_create(cls, name, directed):
        """
        Try to fetch the `SampleRelationType` from the server and create it if it does not exist.

        :param name: The unique name of the `SampleRelationType`
        :param directed: bool
        :return: The `SampleRelationType`
        :raises `ValueError` if the `SampleRelationType` already exists on the server, but the value of 'directed' does not match.
        """
        try:
            obj = cls.get(name)
        except HTTPError:
            obj = cls.create(name, directed)

        if obj.directed != directed:
            raise ValueError('The SampleRelationType exists on the server, but the value of "directed" does not match.')

        return obj

    def create_relation(self, sample, other, additional_metadata=None):
        from mass_api_client.resources import SampleRelation
        return SampleRelation.create(sample, other, self, additional_metadata)

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.name))

    def __str__(self):
        return self.__repr__()