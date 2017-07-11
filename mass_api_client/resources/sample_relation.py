from mass_api_client.schemas import SampleRelationTypeSchema, SampleRelationSchema
from .base_with_subclasses import BaseResource
from .sample import Sample


class SampleRelationType(BaseResource):
    schema = SampleRelationTypeSchema()
    endpoint = 'sample_relation_type'

    @classmethod
    def create(cls, name, directed, **kwargs):
        return cls._create(name=name, directed=directed)

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.name))

    def __str__(self):
        return self.__repr__()


class SampleRelation(BaseResource):
    schema = SampleRelationSchema()
    endpoint = 'sample_relation'
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
