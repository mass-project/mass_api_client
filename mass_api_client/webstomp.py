from stomp.connect import BaseConnection
from stomp.protocol import Protocol11
from stomp.transport import Transport
from stomp.exception import ConnectFailedException

from hashlib import sha1
from base64 import b64encode

import re
import os
import logging

log = logging.getLogger('stomp.py')

# As specified in :rfc:`6455`.
WS_KEY = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebsocketTransport(Transport):
    def __init__(self,
                 url,
                 try_loopback_connect=True,
                 reconnect_sleep_initial=0.1,
                 reconnect_sleep_increase=0.5,
                 reconnect_sleep_jitter=0.1,
                 reconnect_sleep_max=60.0,
                 reconnect_attempts_max=3,
                 ssl_key_file=None,
                 ssl_cert_file=None,
                 ssl_ca_certs=None,
                 ssl_cert_validator=None,
                 ssl_version=None,
                 timeout=None,
                 keepalive=None,
                 vhost=None,
                 auto_decode=True,
                 encoding='utf-8',
                 recv_bytes=1024
                 ):
        self.ws_nonce = None
        host, port, self.resource, use_ssl = self._parse_url(url)
        super(WebsocketTransport, self).__init__(host_and_ports=[(host, port)],
                                                 prefer_localhost=False,
                                                 try_loopback_connect=try_loopback_connect,
                                                 reconnect_sleep_initial=reconnect_sleep_initial,
                                                 reconnect_sleep_increase=reconnect_sleep_increase,
                                                 reconnect_sleep_jitter=reconnect_sleep_jitter,
                                                 reconnect_sleep_max=reconnect_sleep_max,
                                                 reconnect_attempts_max=reconnect_attempts_max,
                                                 use_ssl=use_ssl,
                                                 ssl_key_file=ssl_key_file,
                                                 ssl_cert_file=ssl_cert_file,
                                                 ssl_ca_certs=ssl_ca_certs,
                                                 ssl_cert_validator=ssl_cert_validator,
                                                 ssl_version=ssl_version,
                                                 timeout=timeout,
                                                 keepalive=keepalive,
                                                 vhost=vhost,
                                                 auto_decode=auto_decode,
                                                 encoding=encoding,
                                                 recv_bytes=recv_bytes)

    def attempt_connection(self):
        super(WebsocketTransport, self).attempt_connection()

        # Initiate WS connection
        self.ws_nonce = b64encode(os.urandom(16))
        self.send(self._handshake_request)

        # Read handshake headers from server
        response = b''
        while True:
            b = self.receive()
            if not b:
                break
            response += b
            if b'\r\n\r\n' in response:
                break

        # Validate response from server
        try:
            self._validate_response(response)
        except ConnectFailedException:
            self.disconnect_socket()
            raise

    @staticmethod
    def _parse_url(url):
        """
        Parses an URL to extract the host, port, path and whether SSL should be used.

        :param str url: An URL of the form ws://host[:port][path] or wss://host[:port][path]
        :return (str,int,str,bool): The tuple of host, port, path and the use of SSL
        """
        m = re.search(r'^(?P<proto>ws|wss)://(?P<host>[^:]+)(:(?P<port>\d+))?(?P<path>/.*)', url)
        return m.group('host'), int(m.group('port')), m.group('path'), m.group('proto') == 'wss'

    @property
    def _handshake_request(self):
        """
        The WS-handshake request of the client.
        Adapted from: https://github.com/Lawouach/WebSocket-for-Python/blob/master/ws4py/client/__init__.py
        """
        headers = [
            ('Host', '%s:%s' % (self.current_host_and_port[0], self.current_host_and_port[1])),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', self.ws_nonce.decode('utf-8')),
            ('Sec-WebSocket-Version', '13')
        ]

        request = [("GET %s HTTP/1.1" % self.resource).encode('utf-8')]
        for header, value in headers:
            request.append(("%s: %s" % (header, value)).encode('utf-8'))
        request.append(b'\r\n')

        return b'\r\n'.join(request)

    def _validate_response(self, response):
        """
        Validate if the response of the server complies with :rfc:`6455` and raise an exception if it does not.

        :param bytes response: The response from the server
        :return:
        """
        headers, _, body = response.partition(b'\r\n\r\n')

        # The body should be empty, as the STOMP protocol should be initiated by the client
        if body:
            raise ConnectFailedException('Invalid response from WS server.')

        # Check for the right status code
        response_line, _, headers = headers.partition(b'\r\n')
        protocol, code, status = response_line.split(b' ', 2)
        if code != b'101':
            raise ConnectFailedException('Invalid WS response status: %s %s' % (code, status))

        # Parse the headers
        header_dict = {}
        for header_line in headers.split(b'\r\n'):
            k, v = header_line.decode().split(':', 1)
            header_dict[k.strip().lower()] = v.strip().lower()

        # Check if the received headers are valid
        if 'upgrade' not in header_dict or header_dict['upgrade'] != 'websocket':
            raise ConnectFailedException('Server did not upgrade connection to websocket.')

        if 'connection' not in header_dict or header_dict['connection'] != 'upgrade':
            raise ConnectFailedException('WS server did not upgrade connection.')

        sec_token = b64encode(sha1(self.ws_nonce + WS_KEY).digest()).decode().lower()
        if 'sec-websocket-accept' not in header_dict or header_dict['sec-websocket-accept'] != sec_token:
            raise ConnectFailedException('Wrong WS accept key.')


class WebstompConnection(BaseConnection, Protocol11):
    def __init__(self, url, reconnect_sleep_initial=0.1,
                 reconnect_sleep_increase=0.5, reconnect_sleep_jitter=0.1, reconnect_sleep_max=60.0,
                 reconnect_attempts_max=3, timeout=None, heartbeats=(0, 0), keepalive=None,
                 vhost=None, auto_decode=True, auto_content_length=True, heart_beat_receive_scale=1.5):
        transport = WebsocketTransport(url,
                                       reconnect_sleep_initial=reconnect_sleep_initial,
                                       reconnect_sleep_increase=reconnect_sleep_increase,
                                       reconnect_sleep_jitter=reconnect_sleep_jitter,
                                       reconnect_sleep_max=reconnect_sleep_max,
                                       reconnect_attempts_max=reconnect_attempts_max,
                                       timeout=timeout,
                                       keepalive=keepalive,
                                       vhost=vhost,
                                       auto_decode=auto_decode)
        BaseConnection.__init__(self, transport)
        Protocol11.__init__(self, transport)

    def connect(self, *args, **kwargs):
        self.transport.start()
        Protocol11.connect(self, *args, **kwargs)
