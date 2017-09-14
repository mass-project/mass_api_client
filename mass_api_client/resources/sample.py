import tempfile
from contextlib import contextmanager

from mass_api_client.connection_manager import ConnectionManager
from mass_api_client.resources.report import Report
from mass_api_client.schemas import DomainSampleSchema, IPSampleSchema, URISampleSchema, FileSampleSchema, ExecutableBinarySampleSchema
from .base_with_subclasses import BaseWithSubclasses


class Sample(BaseWithSubclasses):
    _endpoint = 'sample'
    _class_identifier = 'Sample'

    _filter_parameters = [
        'delivery_date__lte',
        'delivery_date__gte',
        'first_seen__lte',
        'first_seen__gte',
        'tags__all'
    ]

    def get_reports(self):
        """
        Retrieve all reports submitted for this Sample.

        :return: A list of :class:`.Report`
        """
        url = '{}reports/'.format(self.url)
        return Report._get_list_from_url(url, append_base_url=False)

    def get_relation_graph(self, depth=None):
        """
        Get all `SampleRelation`s in the relation graph of the sample.

        :param depth: max depth of the returned graph. None retrieves the complete graph.
        :return: An iterator over the relations
        """
        url = '{}relation_graph/'.format(self.url)
        if depth is not None:
            params = {'depth': depth}
        else:
            params = {}

        from .sample_relation import SampleRelation
        return SampleRelation._get_iter_from_url(url, params=params, append_base_url=False)

    def __repr__(self):
        return '[{}] {}'.format(str(self.__class__.__name__), str(self.id))

    def __str__(self):
        return self.__repr__()


class DomainSample(Sample):
    schema = DomainSampleSchema()
    _class_identifier = 'Sample.DomainSample'
    _creation_point = 'sample/submit_domain'
    _default_filters = {'_cls': _class_identifier}

    _filter_parameters = Sample._filter_parameters + [
        'domain',
        'domain__contains',
        'domain__startswith',
        'domain__endswith'
    ]

    @classmethod
    def create(cls, domain, tlp_level=0, tags=[]):
        """
        Create a new :class:`DomainSample` on the server.

        :param domain: The domain as a string.
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        return cls._create(domain=domain, tlp_level=tlp_level, tags=tags)


class URISample(Sample):
    schema = URISampleSchema()
    _class_identifier = 'Sample.URISample'
    _creation_point = 'sample/submit_uri'
    _default_filters = {'_cls': _class_identifier}

    _filter_parameters = Sample._filter_parameters + [
        'uri',
        'uri__contains',
        'uri__startswith',
        'uri__endswith'
    ]

    @classmethod
    def create(cls, uri, tlp_level=0, tags=[]):
        """
        Create a new :class:`URISample` on the server.

        :param uri: The uri as a string.
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        return cls._create(uri=uri, tlp_level=tlp_level, tags=tags)
      

class IPSample(Sample):
    schema = IPSampleSchema()
    _class_identifier = 'Sample.IPSample'
    _creation_point = 'sample/submit_ip'
    _default_filters = {'_cls': _class_identifier}

    _filter_parameters = Sample._filter_parameters + [
        'ip_address',
        'ip_address__startswith'
    ]

    @classmethod
    def create(cls, ip_address, tlp_level=0, tags=[]):
        """
        Create a new :class:`IPSample` on the server.

        :param ip_address: The ip address as a string
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        return cls._create(ip_address=ip_address, tlp_level=tlp_level, tags=tags)


class FileSample(Sample):
    schema = FileSampleSchema()
    _class_identifier = 'Sample.FileSample'
    _creation_point = 'sample/submit_file'
    _default_filters = {'_cls__startswith': _class_identifier}

    _filter_parameters = Sample._filter_parameters + [
        'md5sum',
        'sha1sum',
        'sha256sum',
        'sha512sum',
        'mime_type',
        'file_names',
        'file_size__lte',
        'file_size__gte',
        'shannon_entropy__lte',
        'shannon_entropy__gte'
    ]

    @classmethod
    def create(cls, filename, file, tlp_level=0, tags=[]):
        """
        Create a new :class:`FileSample` on the server.

        :param filename: The filename of the file
        :param file: A file-like object
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        return cls._create(additional_binary_files={'file': (filename, file)}, tlp_level=tlp_level, tags=tags)

    def download_to_file(self, file):
        """
        Download and store the file of the sample.

        :param file: A file-like object to store the file.
        """
        con = ConnectionManager().get_connection(self._connection_alias)
        return con.download_to_file(self.file, file, append_base_url=False)

    @contextmanager
    def temporary_file(self):
        """
        Contextmanager to get a temporary copy of the file of the sample.

        The file will automatically be closed and removed after use.

        :return: A file-like object.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            self.download_to_file(tmp)
            yield tmp


class ExecutableBinarySample(FileSample):
    schema = ExecutableBinarySampleSchema()
    _class_identifier = 'Sample.FileSample.ExecutableBinarySample'
    _default_filters = {'_cls': _class_identifier}
