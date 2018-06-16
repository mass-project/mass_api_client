import json
import stomp


class QueueListener(stomp.ConnectionListener):
    def __init__(self, queue, callback, user, password):
        super(QueueListener, self).__init__()
        self.callback = callback
        self.queue_id = queue
        self.conn = stomp.Connection()
        self.conn.set_listener('', self)
        self.conn.start()
        self.conn.connect(user, password, wait=True)
        self.conn.subscribe(destination='/queue/{}'.format(queue), id=self.queue_id,
                            ack='client')


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
