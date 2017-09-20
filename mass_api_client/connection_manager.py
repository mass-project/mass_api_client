import json
from contextlib import closing

import requests


class Connection:
    def __init__(self, api_key, base_url, timeout):
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._default_headers = {'content-type': 'application/json',
                                 'Authorization': 'APIKEY {}'.format(api_key)}

    def get_stream(self, url, append_base_url, params):
        if append_base_url:
            url = self._base_url + url

        r = requests.get(url, stream=True, headers=self._default_headers, params=params, timeout=self._timeout)
        r.raise_for_status()
        return r

    def download_to_file(self, url, file, append_base_url=True, params=None):
        if params is None:
            params = {}

        with closing(self.get_stream(url, append_base_url, params)) as r:
            for block in r.iter_content(1024):
                if not block:
                    break
                file.write(block)
            file.flush()

    def get_json(self, url, append_base_url=True, params=None):
        if params is None:
            params = {}

        if append_base_url:
            url = self._base_url + url

        r = requests.get(url, headers=self._default_headers, params=params, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    def post_json(self, url, data, append_base_url=True, params=None):
        if params is None:
            params = {}

        if append_base_url:
            url = self._base_url + url

        r = requests.post(url, json.dumps(data), headers=self._default_headers, params=params, timeout=self._timeout)
        r.raise_for_status()
        return r.json()

    def post_multipart(self, url, metadata, append_base_url=True, params=None, json_files=None, binary_files=None):
        if params is None:
            params = {}
        if binary_files is None:
            binary_files = {}
        if json_files is None:
            json_files = {}
        if append_base_url:
            url = self._base_url + url
        files = {}

        headers = self._default_headers.copy()
        headers.pop('content-type')
        json_files['metadata'] = (None, metadata)

        for key, value in json_files.items():
            files[key] = (value[0], json.dumps(value[1]), 'application/json')

        for key, value in binary_files.items():
            files[key] = (value[0], value[1], 'binary/octet-stream')

        r = requests.post(url, headers=headers, params=params, files=files, timeout=self._timeout)
        r.raise_for_status()
        if r.status_code == 204:
            return dict()
        return r.json()


class ConnectionManager:
    _connections = {}

    def get_connection(self, alias):
        if alias not in self._connections:
            raise RuntimeError("Connection '{}' is not defined. "
                               "Use ConnectionManager().register_connection(...) to do so.".format(alias))

        return self._connections[alias]

    def register_connection(self, alias, api_key, base_url, timeout=5):
        """
        Create and register a new connection.

        :param alias:   The alias of the connection. If not changed with `switch_connection`,
                        the connection with default 'alias' is used by the resources.
        :param api_key: The private api key.
        :param base_url: The api url including protocol, host, port (optional) and location.
        :param timeout: The time in seconds to wait for 'connect' and 'read' respectively.
                        Use a tuple to set these values separately or None to wait forever.
        :return:
        """
        if not base_url.endswith('/'):
            base_url += '/'

        self._connections[alias] = Connection(api_key, base_url, timeout)


