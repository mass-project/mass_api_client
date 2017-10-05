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

    def download_to_file(self, file):
        """
        Download and store the file of the sample.

        :param file: A file-like object to store the file.
        """
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
    def create_with_file(cls, filename, file, tlp_level=0, tags=[]):
        """
        Create a new :class:`Sample` on the server.

        :param filename: The filename of the file
        :param file: A file-like object
        :param tlp_level: The TLP-Level
        :param tags: Tags to add to the sample.
        :return: The created sample.
        """
        return cls._create(additional_binary_files={'file': (filename, file)}, tlp_level=tlp_level, tags=tags)
