import json
from contextlib import closing

import requests


class Connection:
    def __init__(self, api_key, base_url):
        self._api_key = api_key
        self._base_url = base_url
        self._default_headers = {'content-type': 'application/json',
                                 'Authorization': 'APIKEY {}'.format(api_key)}

    def get_stream(self, url, append_base_url, params):
        if append_base_url:
            url = self._base_url + url

        r = requests.get(url, stream=True, headers=self._default_headers, params=params)
        r.raise_for_status()
        return r

    def download_to_file(self, url, file, append_base_url, params):
        with closing(self.get_stream(url, append_base_url, params)) as r:
            for block in r.iter_content(1024):
                if not block:
                    break
                file.write(block)

    def get_json(self, url, append_base_url, params):
        if append_base_url:
            url = self._base_url + url

        r = requests.get(url, headers=self._default_headers, params=params)
        r.raise_for_status()
        return r.json()

    def post_json(self, url, data, append_base_url, params):
        if append_base_url:
            url = self._base_url + url

        r = requests.post(url, json.dumps(data), headers=self._default_headers, params=params)
        r.raise_for_status()
        return r.json()

    def post_multipart(self, url, metadata, append_base_url, params, json_files=None, binary_files=None):
        if binary_files is None:
            binary_files = {}
        if json_files is None:
            json_files = {}
        if append_base_url:
            url = self._base_url + url
        files = {}

        headers = self._default_headers.copy()
        headers.pop('content-type')
        json_files['metadata'] = ('metadata', metadata)

        for key, value in json_files.items():
            files[key] = (value[0], json.dumps(value[1]), 'application/json')

        for key, value in binary_files.items():
            files[key] = (value[0], value[1], 'binary/octet-stream')

        r = requests.post(url, headers=headers, params=params, files=files)
        r.raise_for_status()
        return r.json()


class ConnectionManager:
    _connections = {}

    def register_connection(self, alias, api_key, base_url):
        self._connections[alias] = Connection(api_key, base_url)

    def download_to_file(self, url, file, append_base_url=True, params=None):
        if params is None:
            params = {}
        self._connections['default'].download_to_file(url, file, append_base_url, params)

    def get_json(self, url, append_base_url=True, params=None):
        if params is None:
            params = {}
        return self._connections['default'].get_json(url, append_base_url, params)

    def post_json(self, url, data, append_base_url=True, params=None):
        if params is None:
            params = {}
        return self._connections['default'].post_json(url, data, append_base_url, params)

    def post_multipart(self, url, metadata, append_base_url=True, params=None, json_files=None, binary_files=None):
        if binary_files is None:
            binary_files = {}
        if json_files is None:
            json_files = {}
        if params is None:
            params = {}
        return self._connections['default'].post_multipart(url, metadata, append_base_url, params, json_files, binary_files)
