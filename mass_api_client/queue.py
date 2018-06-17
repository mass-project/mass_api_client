import json
import stomp
from stomp.adapter import WebsocketConnection
from time import sleep


class QueueListener(stomp.ConnectionListener):
    def __init__(self, queue, callback, user, password):
        super(QueueListener, self).__init__()
        self.callback = callback
        self.queue_id = queue
        self.conn = WebsocketConnection()
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
    def on_message(self, headers, body):
        from mass_api_client.resources import AnalysisRequest, Sample
        data = json.loads(body)
        request = AnalysisRequest._get_detail_from_json(data['analysis_request'])
        sample = Sample._get_detail_from_json(data['sample'])

        result = self.callback(request, sample)

        if result:
            self.conn.ack(headers['message-id'], self.queue_id)
        else:
            self.conn.nack(headers['message-id'], self.queue_id)
