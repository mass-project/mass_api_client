import tempfile
from contextlib import contextmanager

from mass_api_client.connection_manager import ConnectionManager
from mass_api_client.resources.report import Report
from mass_api_client.schemas import SampleSchema
from .base import BaseResource


class Sample(BaseResource):
    schema = SampleSchema()
    _endpoint = 'sample'
    _creation_point = _endpoint

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

    def contains_file(self):
        if 'file' in self.unique_features:
            return True
        else:
            return False

    def has_file(self):
        return 'file' in self.unique_features

    def has_ipv4(self):
        return 'ipv4' in self.unique_features

    def has_ipv6(self):
        return 'ipv6' in self.unique_features

    def has_port(self):
        return 'port' in self.unique_features

    def has_domain(self):
        return 'domain' in self.unique_features

    def has_uri(self):
        return 'uri' in self.unique_features

    def download_to_file(self, file):
        """
        Download and store the file of the sample.

        :param file: A file-like object to store the file.
        """
        if not self.contains_file():
            raise RuntimeError('The sample does not contain a file.')
        con = ConnectionManager().get_connection(self._connection_alias)
        return con.download_to_file(self.url + 'download/', file, append_base_url=False)

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

    @classmethod
    def create(cls, uri=None, domain=None, port=None, ipv4=None, ipv6=None, filename=None, file=None, tlp_level=0, tags=None):
        """
        Create a new :class:`Sample` on the server.

        :param uri: An URI
        :param domain: A domain name
        :param port: A port number
        :param ipv4: An IPv4 address
        :param ipv6: An IPv6 address
        :param filename: The filename of the file
        :param file: A file-like object
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        unique_features = {}
        if uri:
            unique_features['uri'] = uri
        if domain:
            unique_features['domain'] = domain
        if port:
            unique_features['port'] = port
        if ipv4:
            unique_features['ipv4'] = ipv4
        if ipv6:
            unique_features['ipv6'] = ipv6
        if not tags:
            tags = []
        if file and filename:
            return cls._create(additional_binary_files={'file': (filename, file)}, tlp_level=tlp_level, tags=tags, unique_features=unique_features)
        elif bool(file) != bool(filename):
            raise ValueError('Either file or filename is set, but not both.')
        else:
            return cls._create(tlp_level=tlp_level, tags=tags, unique_features=unique_features)

