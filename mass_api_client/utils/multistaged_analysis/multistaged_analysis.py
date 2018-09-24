import asyncio
import os
import pickle
import random
import string
import sys
import traceback
import zlib
from multiprocessing import Process

import zmq.asyncio

if os.getenv('SENTRY_DSN', None):
    from raven import Client


class StageErrorHandlerStdout:
    """
    This error handler is meant as backup handler because the RequestObject gets lost.
    Instead use the Module Error Handlers for failed Reports.
    """

    def __init__(self):
        print('StageErrorHandlerStdout contructed')

    def handle(self, e):
        traceback.print_exc(file=sys.stdout)


class StageErrorHandlerSentry:
    """
    This error handler is meant as backup handler because the RequestObject gets lost.
    Instead use the Module Error Handlers for failed Reports.
    """

    def __init__(self):
        self.sentry_dsn = os.getenv('SENTRY_DSN', None)
        if self.sentry_dsn:
            self.client = Client(self.sentry_dsn)
        else:
            print('ERROR: SENTRY_DSN is not defined.')

    def handle(self, e):
        if self.sentry_dsn:
            try:
                self.client.captureException()
            except:
                print('ERROR: Cannot Capture Exception:')
                traceback.print_exc(file=sys.stdout)
        else:
            print('ERROR: Cannot capture because SENTRY_DSN is not defined. Using stdout instead:')
            traceback.print_exc(file=sys.stdout)


class AsyncSockets:
    """
    Each :class:`~mass_api_client.utils.multistaged_analysis.AsyncAnalysisModule`-instance has its own instance of
    :class:`~mass_api_client.utils.multistaged_analysis.AsyncSockets. They contain information like the name of the
    stage or a list of all sockets. With the instance of this class objects can be sent to other stages.
    """
    def __init__(self, shared_socket_list, context, in_address, loop, name, next_stage):
        self.name = name
        self.shared_socket_list = shared_socket_list
        self.in_socket = context.socket(zmq.PULL)
        self.in_socket.set_hwm(1)
        self.in_socket.connect(in_address)
        self.loop = loop
        self.next_stage = next_stage

    async def send(self, obj, stage=None, flags=0, protocol=-1):
        """
        Send an object to the stage with the name specified with the 'stage' parameter.
        :param obj: The object to be send.
        :param stage: The name of the stage to be send. If it is not specified the name of the stage passed with the 
                      'next_stage' parameter of the 
                      :func:`~mass_api_client.utils.multistaged_analysis.AnalysisFrame.add_stage` functionis used.
        :param flags: Flags through to the pickle module.
        :param protocol: The protocol passed through to the pickle module.
        :return: 
        """
        if stage is None:
            stage = self.next_stage
        # force coroutine switch when sending because 'send' is blocking while queue isn't full
        await asyncio.sleep(0)
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return await self.shared_socket_list.out_sockets[stage].send(z, flags=flags)

    async def send_with_instruction(self, obj, stage, report_name, report_data_for_called_stage, stage_instruction=None,
                                    flags=0,
                                    protocol=-1):
        await asyncio.sleep(0)

        obj.stage_report[stage] = report_data_for_called_stage
        obj.stage_report[stage]['report_name'] = report_name

        if stage_instruction:
            obj.stage_instruction = stage_instruction
        else:
            obj.stage_instruction = self.next_stage
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return await self.shared_socket_list.out_sockets[stage].send(z, flags=flags)

    async def send_instructed(self, obj, flags=0, protocol=-1):
        await asyncio.sleep(0)
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return await self.shared_socket_list.out_sockets[obj.stage_instruction].send(z, flags=flags)

    async def receive(self, flags=0):
        """
        Receive objects which are in the queue of the stage in wich this function is called.
        :param flags: Flags which are passed through to pickle.
        :return: Returns the received object.
        """
        z = await self.in_socket.recv(flags)
        p = zlib.decompress(z)
        return pickle.loads(p)


class AsyncAnalysisModule:
    def __init__(self, context, method, name, args, in_address, loop, next_stage, backup_error_handler):
        self.name = name
        self.in_address = in_address
        self.sockets = None
        self.context = context
        self.analysis_method = method
        self.args = args
        self.loop = loop
        self.next_stage = next_stage
        self.backup_error_hander = backup_error_handler

    async def _bootstrap_stage(self):
        while True:
            try:
                await asyncio.ensure_future(self.analysis_method(self.sockets, *self.args), loop=self.loop)
            except Exception as e:
                self.backup_error_hander.handle(e)
                #print(e, self.analysis_method)
                #traceback.print_exc(file=sys.stdout)

    def bootstrap_stage(self, shared_sockets):
        self.sockets = AsyncSockets(shared_sockets, self.context, self.in_address, self.loop, self.name,
                                    self.next_stage)
        return self._bootstrap_stage()


class SyncSockets:
    """
        Each :class:`~mass_api_client.utils.multistaged_analysis.SyncAnalysisModule`-instance has its own instance of
        :class:`~mass_api_client.utils.multistaged_analysis.SyncSockets. They contain information like the name of the
        stage or a list of all sockets. With the instance of this class objects can be sent to other stages.
        """
    def __init__(self, context, address_dict, name, next_stage):
        self.out_sockets = {}
        for entry in address_dict:
            self.out_sockets[entry] = (context.socket(zmq.PUSH))
            self.out_sockets[entry].connect(address_dict[entry]['in'])
        self.in_socket = context.socket(zmq.PULL)
        self.in_socket.connect(address_dict[name]['out'])
        self.next_stage = next_stage
        self.name = name

    def send(self, obj, stage=None, flags=0, protocol=-1):
        """
        Send an object to the stage with the name specified with the 'stage' parameter.
        :param obj: The object to be send.
        :param stage: The name of the stage to be send. If it is not specified the name of the stage passed with the 
                      'next_stage' parameter of the 
                      :func:`~mass_api_client.utils.multistaged_analysis.AnalysisFrame.add_stage` functionis used.
        :param flags: Flags through to the pickle module.
        :param protocol: The protocol passed through to the pickle module.
        :return: 
        """
        if stage is None:
            stage = self.next_stage
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return self.out_sockets[stage].send(z, flags=flags)

    def send_with_instruction(self, obj, stage, report_name, report_data_for_called_stage, stage_instruction=None,
                              flags=0, protocol=-1):
        obj.stage_report[stage] = report_data_for_called_stage
        obj.stage_report[stage]['report_name'] = report_name

        if stage_instruction:
            obj.stage_instruction = stage_instruction
        else:
            obj.stage_instruction = self.next_stage
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return self.out_sockets[stage].send(z, flags=flags)

    def send_instructed(self, obj, flags=0, protocol=-1):
        p = pickle.dumps(obj, protocol)
        z = zlib.compress(p)
        return self.out_sockets[obj.stage_instruction].send(z, flags=flags)

    def receive(self, flags=0):
        """
        Receive objects which are in the queue of the stage in wich this function is called.
        :param flags: Flags which are passed through to pickle.
        :return: Returns the received object.
        """
        z = self.in_socket.recv(flags)
        p = zlib.decompress(z)
        return pickle.loads(p)


class SyncAnalysisModule:
    def __init__(self, context, method, name, args, next_stage, backup_error_handler):
        self.address_dict = None
        self.name = name
        self.context = context
        self.analysis_method = method
        self.args = args
        self.next_stage = next_stage
        self.backup_error_hander = backup_error_handler

    def _bootstrap_stage(self, args):
        sockets = SyncSockets(self.context, self.address_dict, self.name, self.next_stage)
        while True:
            try:
                self.analysis_method(sockets, *args)
            except Exception as e:
                self.backup_error_hander.handle(e)

    def bootstrap_stage(self, address_dict):
        self.address_dict = address_dict
        p = Process(target=self._bootstrap_stage, args=(self.args,))
        p.start()
        return p


class Streamer:
    """This class wraps the ZeroMQ Streamer Devices. Each device runs in its own Process."""
    def __init__(self, frontend_address, backend_address, queue_size):
        self.frontend_address = frontend_address
        self.backend_address = backend_address
        self.queue_size = queue_size

    def _streamer_process(self):
        context = zmq.Context(1)

        socket_pull = context.socket(zmq.PULL)
        socket_pull.set_hwm(self.queue_size)
        socket_pull.bind(self.frontend_address)

        socket_push = context.socket(zmq.PUSH)
        socket_push.set_hwm(1)
        socket_push.bind(self.backend_address)

        zmq.device(zmq.STREAMER, socket_pull, socket_push)

    def start_streamer(self):
        p = Process(target=self._streamer_process)
        p.start()


class AsyncSharedOutSockets:
    """
    Without the shared Sockets each stage would own its own outgoing Socket. To minimize this number, async Stages
    share their outgoing Socket. Incomming Sockets can not be shared because they hold the queue of each stage."""
    def __init__(self, context, address_dict):
        self.out_sockets = {}
        for entry in address_dict:
            self.out_sockets[entry] = (context.socket(zmq.PUSH))
            self.out_sockets[entry].set_hwm(1)
            self.out_sockets[entry].connect(address_dict[entry]['in'])


class AnalysisFrame:
    """
     Instances of this class wrap ZeroMQ Streamer Devices and the analysis stages for an analysis pipeline.
     The workflow consists of three steps:

     1. Create frame
     2. Add stages
     3. Start stages
    """
    def __init__(self, ipc_path='/tmp/mass_pipeline/', loop=None):
        """Creates a new AnalysisFrame object.

        :param ipc_path: A list of Addresses for the ZeroMQ Queues. The length of the list should be even.
                         Each stage needs two addresses.
        :param loop: Define a custom loop for the asyncronous stages. If this parameter is not defined the function
                     :func:`~asyncio.get_event_loop` is called internally to get a event loop.

        """
        self.ipc_path = ipc_path + (''.join(random.choice(string.ascii_letters) for m in range(16))) + '/'
        while os.path.exists(self.ipc_path):
            self.ipc_path = ipc_path + (''.join(random.choice(string.ascii_letters) for m in range(16))) + '/'
        os.makedirs(self.ipc_path)
        self.ipc_name = 0
        self.async_context = zmq.asyncio.Context()
        self.context = zmq.Context()
        self.streamers = []
        self.address_dict = {}
        self.stages = {}
        if not loop:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    def add_stage(self, method, name, replicas=1, concurrency='process', args=(), next_stage=None, queue_size=100,
                  backup_error_handler=StageErrorHandlerSentry()):
        """

        :param method: A function which will be called with start_all_stages().
        :param name: Name of the Stage. It can be used to address communication between the stages.
        :param replicas: Number of the Replicas of this stage.
        :param concurrency: You can choose between 'process' and 'async'.
               'process': Starts the in 'method' defined function as process.
               'async': Starts the in 'method' defined function as a coroutine.
        :param args: A tuple of arguments which will be passed when the function is started.
        :param next_stage: Name of the default next stage. It is used for the
               :func:`~mass_api_client.utils.multistaged_analysis.SyncSockets.send` function of
               :class:`~mass_api_client.utils.multistaged_analysis.SyncSockets` or
               :class:`~mass_api_client.utils.multistaged_analysis.AsyncSockets` Objects. It defines the next stage if no
               'stage' parameter is defined.
        :param queue_size: The minimum queue Size for this stage. Note that the actual queue size might be much greater.
        :param backup_error_handler: A Error Handler Object which ensures thas the pipeline doesn't crash.
               Unsubmitted Reports get eventually lost, so it might be better to catch Exceptions inside the analysis module.
        """
        self.address_dict[name] = {}
        out_address = 'ipc://' + self.ipc_path + str(self.ipc_name)
        self.ipc_name += 1
        in_address = 'ipc://' + self.ipc_path + str(self.ipc_name)
        self.ipc_name += 1
        self.address_dict[name]['out'] = out_address
        self.address_dict[name]['in'] = in_address

        # add new streamer device
        self.streamers.append(Streamer(in_address, out_address, queue_size))

        if name not in self.stages:
            self.stages[name] = []
        for _ in range(replicas):
            if concurrency == 'async':
                new_stage = AsyncAnalysisModule(self.async_context, method, name, args, self.address_dict[name]['out'],
                                                self.loop, next_stage, backup_error_handler)
            else:
                new_stage = SyncAnalysisModule(self.context, method, name, args, next_stage, backup_error_handler)
            self.stages[name].append(new_stage)

    def start_all_stages(self):
        """Starts all stages added with the
        :func:`~mass_api_client.utils.multistaged_analysis.AnalysisFrame.add_stage` function.

        This function is blocking.
        """
        self._start_streamer_workers()
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

    def _start_streamer_workers(self):
        for streamer in self.streamers:
            streamer.start_streamer()


class StageObject:
    def __init__(self, json_report_objects=None, raw_report_objects=None, additional_metadata=None, tags=None,
                 analysis_date=None, failed=False, error_message=None):
        self.stage_report = {}
        self.stage_instruction = None
        self.report = {'json_report_objects': json_report_objects,
                       'raw_report_objects': raw_report_objects,
                       'additional_metadata': additional_metadata,
                       'tags': tags,
                       'analysis_date': analysis_date,
                       'failed': failed,
                       'error_message': error_message}

    def get_instruction(self, sockets, sub_instruction):
        if sub_instruction in self.stage_report[sockets.name]:
            return self.stage_report[sockets.name].pop(sub_instruction)
        else:
            return None

    def get_stage_report(self, report_name):
        """
        Get a stage report of a specific stage.
        Stage reports are not to be confused with MASS reports.

        A stage report is a possibility to send data with the
        :class:`~mass_api_client.utils.multistaged_analysis.StageObject` between stages.

        :param report_name: The name of the stage report to get. If the stage report was created with
                            :func:`~mass_api_client.utils.multistaged_analysis.StageObject.make_stage_report`
                            it is the name of the stage which created the report.
        :return: Returns the stage report or 'None' if no report with this name exists.
        """
        if report_name in self.stage_report:
            return self.stage_report[report_name]
        else:
            return None

    def make_instructed_stage_report(self, sockets, stage_report):
        report_name = self.get_instruction(sockets, 'report_name')
        self.stage_report[report_name] = stage_report

    def make_stage_report(self, sockets, stage_report):
        """

        Get a stage report of a specific stage.

        A stage report is a possibility to send data with the
        :class:`~mass_api_client.utils.multistaged_analysis.StageObject` between stages.
        Stage reports are not to be confused with MASS reports.

        :param sockets: The :class:`~mass_api_client.utils.multistaged_analysis.SyncSockets` or
                        :class:`~mass_api_client.utils.multistaged_analysis.AsyncSockets`
                        object of this stage.
        :param stage_report: The stage report to be sent.
        """
        self.stage_report[sockets.name] = stage_report

    def report_json(self, sockets, report, report_name=None, subpress_stage_name=False):
        """
        This function can be used to create MASS-json-reports.

        :param sockets: The :class:`~mass_api_client.utils.multistaged_analysis.SyncSockets` or
                        :class:`~mass_api_client.utils.multistaged_analysis.AsyncSockets`
                        object of this stage.
        :param report: The report to be sent.
        :param report_name: specify the name of the report.
        :param subpress_stage_name: By default each json report is named by the name of the analysis stage.
                                    Multiple reports per stage can be created by naming this reports with the
                                    'report_name' parameter.
                                    When you pass 'True' to this parameter, reports are created independently
                                    from analysis stage name. You can specify the report name by the
                                    'report_name' parameter.
        """
        if not self.report['json_report_objects']:
            self.report['json_report_objects'] = {}
        if not subpress_stage_name:
            if sockets.name not in self.report['json_report_objects']:
                self.report['json_report_objects'][sockets.name] = {}
            if report_name:
                self.report['json_report_objects'][sockets.name][report_name] = report
            else:
                for key in report:
                    self.report['json_report_objects'][sockets.name][key] = report[key]
        else:
            if report_name:
                self.report['json_report_objects'][report_name] = report
            else:
                for key in report:
                    self.report['json_report_objects'][key] = report[key]

    def report_tag(self, tag_list):
        if not self.report['tags']:
            self.report['tags'] = []
        for tag in tag_list:
            self.report['tags'].append(tag)

    def report_failed(self, failed):
        self.report['failed'] = failed

    def report_raw_report_object(self, raw_report_objects):
        self.report['raw_report_objects'] = raw_report_objects

    def report_additional_metadata(self, additional_metadata):
        self.report['additional_metadata'] = additional_metadata

    def report_analysis_data(self, analysis_date):
        self.report['analysis_date'] = analysis_date

    def report_error_message(self, error_message):
        self.report['error_message'] = error_message


class RequestObject(StageObject):
    def __init__(self, request, sample, json_report_objects=None, raw_report_objects=None,
                 additional_metadata=None, tags=None, analysis_date=None, failed=False, error_message=None):
        StageObject.__init__(self, json_report_objects, raw_report_objects, additional_metadata, tags, analysis_date,
                             failed, error_message)
        self.sample = sample
        self.request = request


class CreateSampleAndReportObject(StageObject):
    def __init__(self, sample_uri=None, sample_domain=None, sample_port=None, sample_ipv4=None, sample_ipv6=None,
                 sample_filename=None, sample_file=None, sample_tlp_level=0, sample_tags=None,
                 report_json_report_objects=None, report_raw_report_objects=None,
                 report_additional_metadata=None, report_tags=None, report_analysis_date=None, report_failed=False,
                 report_error_message=None):
        StageObject.__init__(self, report_json_report_objects, report_raw_report_objects, report_additional_metadata,
                             report_tags, report_analysis_date,
                             report_failed, report_error_message)
        self.sample_uri = sample_uri
        self.sample_domain = sample_domain
        self.sample_port = sample_port
        self.sample_ipv4 = sample_ipv4
        self.sample_ipv6 = sample_ipv6
        self.sample_filename = sample_filename
        self.sample_file = sample_file
        self.sample_tlp_level = sample_tlp_level
        self.sample_tags = sample_tags
