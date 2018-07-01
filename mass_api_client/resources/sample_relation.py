from mass_api_client.schemas import SampleRelationSchema
from .base import BaseResource
from .sample import Sample
from .sample_relation_type import SampleRelationType


class SampleRelation(BaseResource):
    schema = SampleRelationSchema()
    _endpoint = 'sample_relation'
    _creation_point = _endpoint
    _creation_queue = 'sample_relations'
    _class_identifier = 'SampleRelation'

    @classmethod
    def create(cls, sample, other, relation_type, additional_metadata=None, use_queue=False):
        if not isinstance(sample, Sample) or not isinstance(other, Sample):
            raise ValueError('"sample" and "other" must be an instance of Sample')

        if additional_metadata is None:
            additional_metadata = {}

        return cls._create(sample=sample.url, other=other.url, relation_type=relation_type.url, additional_metadata=additional_metadata, use_queue=use_queue)

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

    def get_relation_type(self):
        """
        Retrieve the corresponding :class:`SampleRelationType` object from the server.

        :return: The retrieved object.
        """
        return SampleRelationType._get_detail_from_url(self.relation_type, append_base_url=False)

