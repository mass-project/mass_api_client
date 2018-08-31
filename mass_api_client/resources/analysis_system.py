from mass_api_client.schemas import AnalysisSystemSchema
from mass_api_client.queue import AnalysisRequestConsumer
from mass_api_client.connection_manager import ConnectionManager
from .base import BaseResource

from time import sleep


class AnalysisSystem(BaseResource):
    schema = AnalysisSystemSchema()
    _endpoint = 'analysis_system'
    _creation_point = _endpoint

    _filter_parameters = ['identifier_name', 'identifier_name__contains', 'verbose_name', 'verbose_name__contains']

    @classmethod
    def create(cls, identifier_name, verbose_name, tag_filter_expression='', time_schedule=None, number_retries=0,
               minutes_before_retry=0):
        """
        Create a new :class:`AnalysisSystem` on the server.

        :param identifier_name: Unique identifier string.
        :param verbose_name: A descriptive name of the AnalysisSystem.
        :param tag_filter_expression: Tag filters to automatically select samples for this AnalysisSystem.
        :param time_schedule: A list of integers. Each number represents the minutes after which a request will be scheduled.
        :param number_retries: The number of times a sample will be rescheduled after a failed analysis.
        :param minutes_before_retry: The amount of time to wait before rescheduling a sample after a failed analysis.
        :return: The created :class:`AnalysisSystem` object.
        """
        if time_schedule is None:
            time_schedule = [0]

        return cls._create(identifier_name=identifier_name, verbose_name=verbose_name,
                           tag_filter_expression=tag_filter_expression, time_schedule=time_schedule,
                           number_retries=number_retries, minutes_before_retry=minutes_before_retry)

    def create_request(self, sample, priority=0, parameters=None):
        """
        Create a new `AnalysisRequest` on the server.

        :param sample: A `Sample` object
        :param priority: The priority with which the request should be scheduled.
        :param parameters: Analysis system specific parameters.
        :return: The created `AnalysisRequest` object.
        """
        from .analysis_request import AnalysisRequest
        return AnalysisRequest.create(sample, self, priority, parameters)

    def consume_requests(self, callback, prefetch_count=1):
        """
        Process analysis requests for this analysis system.

        :param callback: A callable to process the analysis request.
        The callback should take the request and sample as parameters.
        :param prefetch_count: The number of requests to fetch from the queue at once.
        """
        con = ConnectionManager().get_connection(self._connection_alias)
        request_queue_id = '{}_analysis-requests'.format(self.identifier_name)
        consumer = AnalysisRequestConsumer(callback)
        con.get_queue_handler().consume(request_queue_id, consumer, prefetch_count)

        while True:
            sleep(1)

    def __repr__(self):
        return '[AnalysisSystem] {}'.format(self.identifier_name)

    def __str__(self):
        return self.__repr__()
