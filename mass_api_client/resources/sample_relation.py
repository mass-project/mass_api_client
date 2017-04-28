from mass_api_client.schemas import DroppedBySampleRelationSchema, ResolvedBySampleRelationSchema, \
    RetrievedBySampleRelationSchema, ContactedBySampleRelationSchema, SsdeepSampleRelationSchema
from .base_with_subclasses import BaseWithSubclasses
from .sample import Sample


class SampleRelation(BaseWithSubclasses):
    endpoint = 'sample_relation'
    _class_identifier = 'SampleRelation'

    @classmethod
    def create(cls, sample, other, **kwargs):
        if not isinstance(sample, Sample) or not isinstance(other, Sample):
            raise ValueError('"sample" and "other" must be an instance of Sample')

        return cls._create(sample=sample.url, other=other.url, **kwargs)

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
