import json
import logging
from uuid import uuid4
from sys import exc_info
from traceback import format_exception, print_tb

import stomp
from stomp.adapter.webstomp import WebsocketConnection

logging.getLogger(__name__).addHandler(logging.NullHandler())


class QueueHandler(stomp.ConnectionListener):
    def __init__(self, api_key, url):
        self.conn = WebsocketConnection(ws_uris=[url])
        #self.conn = stomp.Connection11()
        self.conn.set_listener('', self)
        #self.conn.set_listener('hearbeat', stomp.listener.HeartbeatListener)
        self.user = str(uuid4())
        self.password = api_key
        self.callbacks = {}
        self.destination_queue_ids = {}
        self._reconnect = True

    def _ensure_connection(self):
        if not self.conn.is_connected():
            self.conn.connect(self.user, self.password, headers={'heart-beat': '0,10000'}, wait=True)
            for queue_id in self.callbacks.keys():
                self.conn.subscribe(destination='/queue/{}'.format(queue_id), id=queue_id, ack='client')

    def consume(self, queue_id, callback):
        """

        :param queue_id: The name of the queue.
        :param callback: The callback receives conn, headers and data and should return True to ACK the message.
        :return:
        """
        destination = '/queue/{}'.format(queue_id)
        self._ensure_connection()
        self.callbacks[queue_id] = callback
        self.destination_queue_ids[destination] = queue_id
        self.conn.subscribe(destination=destination, id=queue_id, ack='client')

    def send(self, queue_id, data, headers=None):
        self._ensure_connection()
        self.conn.send(destination='/queue/{}'.format(queue_id), body=json.dumps(data), headers=headers)

    def on_connected(self, headers, body):
        logging.info('Queue connected. Subscribing to queues...')

    def on_receiver_loop_completed(self, headers, body):
        logging.info('Queue disconnected.')
        if self._reconnect:
            logging.info('Trying to reconnect...')
            self.conn.stop()
            self._ensure_connection()

    def on_error(self, headers, body):
        self._reconnect = False

    def on_message(self, headers, body):
        data = json.loads(body)
        queue_id = self.destination_queue_ids[headers['destination']]
        result = self.callbacks[queue_id](self.conn, headers, data)

        if result:
            self.conn.ack(headers['message-id'], queue_id)
        else:
            self.conn.nack(headers['message-id'], queue_id)


class AnalysisRequestConsumer:
    def __init__(self, callback, catch_exceptions=True):
        self.catch_exceptions = catch_exceptions
        self.callback = callback

    def __call__(self, conn, headers, data):
        from mass_api_client.resources import AnalysisRequest, Sample
        request = AnalysisRequest._get_detail_from_json(data['analysis_request'])
        sample = Sample._get_detail_from_json(data['sample'])

        try:
            return self.callback(request, sample)
        except Exception:
            if not self.catch_exceptions:
                raise
            self._handle_exception(request, exc_info())
            return True

    def _handle_exception(self, analysis_request, e):
        exc_str = ''.join(format_exception(*e))
        exc_type = e[0].__name__
        print_tb(e[2])
        metadata = {
            'exception type': exc_type
        }

        try:
            analysis_request.create_report(additional_metadata=metadata,
                                           tags=['failed_analysis', 'exception:{}'.format(exc_type)],
                                           raw_report_objects={'traceback': exc_str}, failed=True,
                                           error_message=exc_str, use_queue=True)
        except Exception:
            logging.error('Could not create a report on the server.', exc_info())
