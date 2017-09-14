from mass_api_client.schemas import DroppedBySampleRelationSchema, ResolvedBySampleRelationSchema, \
    RetrievedBySampleRelationSchema, ContactedBySampleRelationSchema, SsdeepSampleRelationSchema
from .base_with_subclasses import BaseWithSubclasses
from .sample import Sample


class SampleRelation(BaseWithSubclasses):
    _endpoint = 'sample_relation'
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

    def get_sample(self):
        """
        Retrieves the first :class:`Sample` object of the sample relation from the server.

        :return: The :class:`Sample` object.
        """
        return Sample._get_detail_from_url(self.sample, append_base_url=False)

    def get_other(self):
        """
        Retrieves the other :class:`Sample` object of the sample relation from the server.

        :return: The :class:`Sample` object.
        """
        return Sample._get_detail_from_url(self.other, append_base_url=False)


class DroppedBySampleRelation(SampleRelation):
    schema = DroppedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.DroppedBySampleRelation'
    _creation_point = 'sample_relation/submit_dropped_by'


class ResolvedBySampleRelation(SampleRelation):
    schema = ResolvedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.ResolvedBySampleRelation'
    _creation_point = 'sample_relation/submit_resolved_by'


class ContactedBySampleRelation(SampleRelation):
    schema = ContactedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.ContactedBySampleRelation'
    _creation_point = 'sample_relation/submit_contacted_by'


class RetrievedBySampleRelation(SampleRelation):
    schema = RetrievedBySampleRelationSchema()
    _class_identifier = 'SampleRelation.RetrievedBySampleRelation'
    _creation_point = 'sample_relation/submit_retrieved_by'


class SsdeepSampleRelation(SampleRelation):
    schema = SsdeepSampleRelationSchema()
    _class_identifier = 'SampleRelation.SsdeepSampleRelation'
    _creation_point = 'sample_relation/submit_ssdeep'
