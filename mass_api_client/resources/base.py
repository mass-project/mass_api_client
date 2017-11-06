from datetime import datetime

from mass_api_client.connection_manager import ConnectionManager


class Ref:
    def __init__(self, key):
        self.key = key

    def resolve(self, obj):
        return getattr(obj, self.key, None)


class BaseResource:
    schema = None
    _endpoint = None
    _creation_point = None
    _filter_parameters = []
    _default_filters = {}
    _connection_alias = 'default'

    def __init__(self, connection_alias, **kwargs):
        # Store current connection, in case the connection gets switched later on.
        self._connection_alias = connection_alias
        self.__dict__.update(kwargs)

    @classmethod
    @property
    def schema(cls):
        return Ref('schema').resolve(cls)

    @classmethod
    def _deserialize(cls, data, many=False):
        deserialized, errors = cls.schema.load(data, many=many)
        
        if errors:
            raise ValueError('An error occurred during object deserialization: {}'.format(errors))

        return deserialized

    @classmethod
    def _create_instance_from_data(cls, data):
        return cls(cls._connection_alias, **data)

    @classmethod
    def _get_detail_from_url(cls, url, append_base_url=True):
        con = ConnectionManager().get_connection(cls._connection_alias)

        deserialized = cls._deserialize(con.get_json(url, append_base_url=append_base_url))
        return cls._create_instance_from_data(deserialized)

    @classmethod
    def _get_iter_from_url(cls, url, params=None, append_base_url=True):
        if params is None:
            params = {}

        con = ConnectionManager().get_connection(cls._connection_alias)
        next_url = url

        while next_url is not None:
            res = con.get_json(next_url, params=params, append_base_url=append_base_url)
            deserialized = cls._deserialize(res['results'], many=True)
            for data in deserialized:
                yield cls._create_instance_from_data(data)
            try:
                next_url = res['next']
            except KeyError:
                raise StopIteration
            append_base_url = False

    @classmethod
    def _get_list_from_url(cls, url, params=None, append_base_url=True):
        if params is None:
            params = {}

        con = ConnectionManager().get_connection(cls._connection_alias)
        data = con.get_json(url, params=params, append_base_url=append_base_url)['results']
        deserialized = cls._deserialize(data, many=True)
        objects = [cls._create_instance_from_data(detail) for detail in deserialized]

        return objects

    @classmethod
    def _create(cls, additional_json_files=None, additional_binary_files=None, url=None, force_multipart=False, **kwargs):
        con = ConnectionManager().get_connection(cls._connection_alias)
        if not url:
            url = '{}/'.format(cls._creation_point)
        serialized, errors = cls.schema.dump(kwargs)

        if additional_binary_files or additional_json_files or force_multipart:
            response_data = con.post_multipart(url, serialized, json_files=additional_json_files, binary_files=additional_binary_files)
        else:
            response_data = con.post_json(url, serialized)

        deserialized = cls._deserialize(response_data)

        return cls._create_instance_from_data(deserialized)

    @classmethod
    def get(cls, identifier):
        """
        Fetch a single object.

        :param identifier: The unique identifier of the object
        :return: The retrieved object
        """
        return cls._get_detail_from_url('{}/{}/'.format(cls._endpoint, identifier))

    @classmethod
    def items(cls):
        """
        Get an iterator for all objects.

        :return: The iterator.
        """
        return cls._get_iter_from_url('{}/'.format(cls._endpoint), params=cls._default_filters)

    @classmethod
    def all(cls):
        """
        Download and return all objects.

        :return: The list of objects.
        """
        return [x for x in cls.items()]

    @classmethod
    def query(cls, **kwargs):
        """
        Query multiple objects.

        :param kwargs: The query parameters. The key is the filter parameter and the value is the value to search for.
        :return: The list of matching objects
        :raises: A `ValueError` if at least one of the supplied parameters is not in the list of allowed parameters.
        """
        params = cls._get_query_params(**kwargs)
        return cls._get_iter_from_url('{}/'.format(cls._endpoint), params=params)

    @classmethod
    def count(cls, **kwargs):
        """
        Get the number of objects matching the query parameters.
        The parameters are identical to those used in :func:`~mass_api_client.resources.base.query`.

        :param kwargs: The query parameters. The key is the filter parameter and the value is the value to search for.
        :return: The number of matching objects.
        :raises: A `ValueError` if at least one of the supplied parameters is not in the list of allowed parameters.
        """
        con = ConnectionManager().get_connection(cls._connection_alias)
        params = cls._get_query_params(**kwargs)
        params['count'] = ''

        return con.get_json('{}/'.format(cls._endpoint), params=params)['count']

    @classmethod
    def _get_query_params(cls, **kwargs):
        params = dict(cls._default_filters)

        for key, value in kwargs.items():
            if key in cls._filter_parameters:
                if isinstance(value, datetime):
                    params[key] = value.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                else:
                    params[key] = value
            else:
                raise ValueError('\'{}\' is not a filter parameter for class \'{}\''.format(key, cls.__name__))

        return params

    def delete(self):
        con = ConnectionManager().get_connection(self.connection_alias)
        con.delete(self.url, append_base_url=False)

    def _to_json(self):
        serialized, errors = self.schema.dump(self)

        if errors:
            raise ValueError('An error occurred during object serialization: {}'.format(errors))

        return serialized
