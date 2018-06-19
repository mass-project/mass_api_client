import json
import stomp
import logging
from stomp.adapter import WebsocketConnection
from time import sleep
from sys import exc_info
from traceback import format_exception, print_tb


logging.getLogger(__name__).addHandler(logging.NullHandler())


class QueueListener(stomp.ConnectionListener):
    def __init__(self, queue, callback, user, password, url):
        super(QueueListener, self).__init__()
        self.callback = callback
        self.queue_id = queue
        self.conn = WebsocketConnection(ws_uris=[url])
        self.conn.set_listener('', self)
        self.user = user
        self.password = password

    def run_forever(self):
        # TODO: find something more elegant for this workaround
        while True:
            self.conn.start()
            self.conn.connect(self.user, self.password, wait=True)
            self.conn.subscribe(destination='/queue/{}'.format(self.queue_id), id=self.queue_id,
                                ack='client')

            while self.conn.is_connected():
                sleep(1)

            self.conn.stop()


class AnalysisRequestListener(QueueListener):
    def __init__(self, queue, callback, user, password, url, catch_exceptions=True):
        super(AnalysisRequestListener, self).__init__(queue, callback, user, password, url)
        self.catch_exceptions = catch_exceptions

    def on_message(self, headers, body):
        from mass_api_client.resources import AnalysisRequest, Sample
        data = json.loads(body)
        request = AnalysisRequest._get_detail_from_json(data['analysis_request'])
        sample = Sample._get_detail_from_json(data['sample'])

        try:
            result = self.callback(request, sample)
        except Exception:
            if not self.catch_exceptions:
                raise
            self._handle_exception(request, exc_info())
            result = True

        if result:
            self.conn.ack(headers['message-id'], self.queue_id)
        else:
            self.conn.nack(headers['message-id'], self.queue_id)

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
                                           raw_report_objects={'traceback': ('traceback', exc_str)}, failed=True,
                                           error_message=exc_str)
        except Exception:
            logging.error('Could not create a report on the server.')
