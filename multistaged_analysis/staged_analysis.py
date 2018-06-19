import asyncio
import pickle
import zlib
from multiprocessing import Process

import zmq.asyncio


class AsyncSockets:
    def __init__(self, shared_socket_list, context, in_address):
        self.shared_socket_list = shared_socket_list
        self.in_socket = context.socket(zmq.PULL)
        self.in_socket.connect(in_address)

    async def send(self, obj, stage, flags=0, protocol=-1):
        # force coroutine switch when sending because 'send' is blocking while queue isn't full
        await asyncio.sleep(0)
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return await self.shared_socket_list.out_sockets[stage].send(z, flags=flags)

    async def receive(self, flags=0):
        z = await self.in_socket.recv(flags)
        p = zlib.decompress(z)
        return pickle.loads(p)


class AsyncAnalysisModule:
    def __init__(self, context, method, args, in_address):
        self.in_address = in_address
        self.sockets = None
        self.context = context
        self.analysis_method = method
        self.args = args

    async def _bootstrap_stage(self):
        while True:
            await asyncio.ensure_future(self.analysis_method(self.sockets, *self.args))

    def bootstrap_stage(self, shared_sockets):
        self.sockets = AsyncSockets(shared_sockets, self.context, self.in_address)
        return self._bootstrap_stage()


class SyncSockets:
    def __init__(self, context, address_dict, name):
        self.out_sockets = {}
        for entry in address_dict:
            self.out_sockets[entry] = (context.socket(zmq.PUSH))
            self.out_sockets[entry].connect(address_dict[entry]['in'])
        self.in_socket = context.socket(zmq.PULL)
        self.in_socket.connect(address_dict[name]['out'])

    def send(self, obj, stage, flags=0, protocol=-1):
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return self.out_sockets[stage].send(z, flags=flags)

    def receive(self, flags=0):
        z = self.in_socket.recv(flags)
        p = zlib.decompress(z)
        return pickle.loads(p)


class SyncAnalysisModule:
    def __init__(self, context, method, name, args):
        self.address_dict = None
        self.name = name
        self.context = context
        self.analysis_method = method
        self.args = args

    def _bootstrap_stage(self, args):
        sockets = SyncSockets(self.context, self.address_dict, self.name)
        while True:
            self.analysis_method(sockets, *args)

    def bootstrap_stage(self, address_dict):
        self.address_dict = address_dict
        p = Process(target=self._bootstrap_stage, args=(self.args,))
        p.start()
        return p


class Streamer:
    def __init__(self, frontend_address, backend_address):
        self.frontend_address = frontend_address
        self.backend_address = backend_address

    def _streamer_process(self):
        context = zmq.Context(1)
        socket_pull = context.socket(zmq.PULL)
        socket_pull.bind(self.frontend_address)
        socket_push = context.socket(zmq.PUSH)
        socket_push.bind(self.backend_address)
        zmq.device(zmq.STREAMER, socket_pull, socket_push)

    def start_streamer(self):
        p = Process(target=self._streamer_process)
        p.start()


class AsyncSharedOutSockets:
    def __init__(self, context, address_dict):
        self.out_sockets = {}
        for entry in address_dict:
            self.out_sockets[entry] = (context.socket(zmq.PUSH))
            self.out_sockets[entry].connect(address_dict[entry]['in'])


class AnalysisFrame:
    def __init__(self, addresses):
        """

        :param addresses:
        """
        self.loop = asyncio.get_event_loop()
        self.async_context = zmq.asyncio.Context()
        self.context = zmq.Context()
        self.streamers = []
        self.addresses = addresses
        self.address_dict = {}
        self.stages = {}
        if len(addresses) % 2 != 0:
            print('WARNING: Number of addresses is uneven.')

        for i in range(len(addresses)):
            if i % 2 == 1:
                continue
            self.streamers.append(Streamer(addresses[i], addresses[i + 1]))
        self.start_streamer_workers()

    def add_stage(self, method, name, replicas=1, concurrency='process', args=()):
        """

        :param concurrency:
        :param method:
        :param name:
        :param replicas:
        :param args:
        """
        self.address_dict[name] = {}
        self.address_dict[name]['out'] = self.addresses.pop()
        self.address_dict[name]['in'] = self.addresses.pop()
        if name not in self.stages:
            self.stages[name] = []
        for _ in range(replicas):
            if concurrency == 'async':
                new_stage = AsyncAnalysisModule(self.async_context, method, args, self.address_dict[name]['out'])
            else:
                new_stage = SyncAnalysisModule(self.context, method, name, args)
            self.stages[name].append(new_stage)

    def start_all_stages(self):
        """

        """
        async_shared_sockets = AsyncSharedOutSockets(self.async_context, self.address_dict)
        coros = []
        processes = []
        for stage in self.stages:
            for module in self.stages[stage]:
                if type(module) is AsyncAnalysisModule:
                    coros.append(module.bootstrap_stage(async_shared_sockets))
                if type(module) is SyncAnalysisModule:
                    processes.append(module.bootstrap_stage(self.address_dict))
        self.loop.run_until_complete(asyncio.gather(*coros))
        for p in processes:
            p.join()

    def start_streamer_workers(self):
        for streamer in self.streamers:
            streamer.start_streamer()


class RequestObject:
    def __init__(self, request, sample, json_report_objects=None, raw_report_objects=None, additional_metadata=None,
                 tags=None, analysis_date=None, failed=False, error_message=None):
        self.sample = sample
        self.request = request
        self.report = {'json_report_objects': json_report_objects,
                       'raw_report_objects': raw_report_objects,
                       'additional_metadata': additional_metadata,
                       'tags': tags,
                       'analysis_date': analysis_date,
                       'failed': failed,
                       'error_message': error_message}


def get_requests(sockets, analysis_sys, next_stage):
    """

    :param sockets:
    :param analysis_sys:
    :param next_stage:
    :return:
    """

    def func(request, sample):
        request_obj = RequestObject(request, sample)
        sockets.send(request_obj, next_stage)
        return True

    analysis_sys.consume_requests(func)


def report(sockets):
    """

    :param sockets:
    """
    request_obj = sockets.receive()
    request_obj.request.create_report(json_report_objects=request_obj.report['json_report_objects'],
                                      raw_report_objects=request_obj.report['raw_report_objects'],
                                      additional_metadata=request_obj.report['additional_metadata'],
                                      tags=request_obj.report['tags'],
                                      analysis_date=request_obj.report['analysis_date'],
                                      failed=request_obj.report['failed'],
                                      error_message=request_obj.report['error_message'])
