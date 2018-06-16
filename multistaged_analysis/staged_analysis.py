import asyncio
import pickle
import zlib
from multiprocessing import Process

import zmq.asyncio


class Sockets:
    def __init__(self, context, addresses, position):
        self.position = position
        self.out_sockets = []
        for i, address in enumerate(addresses):
            if i % 2 == 0:
                self.out_sockets.append(context.socket(zmq.PUSH))
                self.out_sockets[-1].connect(address)
        self.in_socket = context.socket(zmq.PULL)
        self.in_socket.connect(addresses[position * 2 + 1])

    async def send(self, obj, stage=None, flags=0, protocol=-1):
        # force coroutine switch when sending because 'send' is blocking while queue isn't full
        await asyncio.sleep(0)
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        if stage:
            return await self.out_sockets[stage].send(z, flags=flags)
        return await self.out_sockets[self.position + 1].send(z, flags=flags)

    async def receive(self, flags=0, protocol=-1):
        z = await self.in_socket.recv(flags)
        p = zlib.decompress(z)
        return pickle.loads(p)


class AnalysisModule:
    def __init__(self, context, addresses, method, position, loop):
        self.loop = loop
        self.position = position
        self.context = context
        self.analysis_method = method
        self.addresses = addresses

    async def bootstrap_stage(self):
        sockets = Sockets(self.context, self.addresses, self.position)

        while True:
            result = await asyncio.ensure_future(self.analysis_method(sockets), loop=self.loop)
            if result:
                await sockets.send(result)


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


class AnalysisFrame:
    def __init__(self, addresses):
        self.loop = asyncio.get_event_loop()
        self.async_context = zmq.asyncio.Context()
        self.context = zmq.Context()
        self.streamers = []
        self.addresses = addresses
        self.stages = {}
        if len(addresses) % 2 != 0:
            print('WARNING: Number of addresses is uneven.')

        for i in range(len(addresses)):
            if i % 2 == 1:
                continue
            self.streamers.append(Streamer(addresses[i], addresses[i + 1]))
        self.start_streamer_workers()

    def add_stage(self, method, position, replicas):
        if str(position) not in self.stages:
            self.stages[str(position)] = []
        for _ in range(replicas):
            new_stage = AnalysisModule(self.async_context, self.addresses, method, position, self.loop)
            self.stages[str(position)].append(new_stage)

    def start_all_stages(self):
        coros = []
        for stage in self.stages:
            for module in self.stages[stage]:
                coros.append(module.bootstrap_stage())
        self.loop.run_until_complete(asyncio.gather(*coros))

    def start_streamer_workers(self):
        for streamer in self.streamers:
            streamer.start_streamer()
