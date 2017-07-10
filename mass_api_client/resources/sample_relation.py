from mass_api_client.schemas import DroppedBySampleRelationSchema, ResolvedBySampleRelationSchema, \
    RetrievedBySampleRelationSchema, ContactedBySampleRelationSchema, SsdeepSampleRelationSchema, SampleRelationTypeSchema
from .base_with_subclasses import BaseWithSubclasses, BaseResource
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


class SampleRelation(BaseWithSubclasses):
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


class DroppedBySampleRelation(SampleRelation):
    schema = DroppedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.DroppedBySampleRelation'
    creation_point = 'sample_relation/submit_dropped_by'


class ResolvedBySampleRelation(SampleRelation):
    schema = ResolvedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.ResolvedBySampleRelation'
    creation_point = 'sample_relation/submit_resolved_by'


class ContactedBySampleRelation(SampleRelation):
    schema = ContactedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.ContactedBySampleRelation'
    creation_point = 'sample_relation/submit_contacted_by'


class RetrievedBySampleRelation(SampleRelation):
    schema = RetrievedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.RetrievedBySampleRelation'
    creation_point = 'sample_relation/submit_retrieved_by'


class SsdeepSampleRelation(SampleRelation):
    schema = SsdeepSampleRelationSchema()
    _class_identifier = 'SampleRelation.SsdeepSampleRelation'
    creation_point = 'sample_relation/submit_ssdeep'
