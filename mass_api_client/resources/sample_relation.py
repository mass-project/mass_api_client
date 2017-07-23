from requests.exceptions import HTTPError

from mass_api_client.schemas import SampleRelationTypeSchema, SampleRelationSchema
from .base_with_subclasses import BaseResource
from .sample import Sample


class SampleRelationType(BaseResource):
    schema = SampleRelationTypeSchema()
    endpoint = 'sample_relation_type'
    creation_point = endpoint

    filter_parameters = ['name']

    @classmethod
    def create(cls, name, directed, **kwargs):
        return cls._create(name=name, directed=directed)

    @classmethod
    def get_or_create(cls, name, directed, **kwargs):
        """
        Try to fetch the `SampleRelationType` from the server and create it if it does not exist.

        :param name: The unique name of the `SampleRelationType`
        :param directed: bool
        :param kwargs:
        :return: The `SampleRelationType`
        :raises `ValueError` if the `SampleRelationType` already exists on the server, but the value of 'directed' does not match.
        """
        try:
            obj = cls.get(name)
        except HTTPError:
            obj = cls.create(name, directed, **kwargs)

        if obj.directed != directed:
            raise ValueError('The SampleRelationType exists on the server, but the value of "directed" does not match.')

        return obj

    def create_relation(self, sample, other, **kwargs):
        return SampleRelation.create(sample, other, self, **kwargs)

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.name))

    def __str__(self):
        return self.__repr__()


class SampleRelation(BaseResource):
    schema = SampleRelationSchema()
    endpoint = 'sample_relation'
    creation_point = endpoint
    _class_identifier = 'SampleRelation'

    @classmethod
    def create(cls, sample, other, relation_type, **kwargs):
        if not isinstance(sample, Sample) or not isinstance(other, Sample):
            raise ValueError('"sample" and "other" must be an instance of Sample')

        return cls._create(sample=sample.url, other=other.url, relation_type=relation_type.url, **kwargs)

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.id))

    def __str__(self):
        return self.__repr__()
