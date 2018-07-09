import asyncio
import traceback

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from mass_api_client.resources import *
from .multistaged_analysis import RequestObject


def error_handling_sync(e, data, sockets):
    data.report['failed'] = True
    data.report['error_message'] = str(e) + traceback.format_exc()
    data.report_tag(['failed'])
    sockets.send(data, 'report')
    print(traceback.format_exc())


async def error_handling_async(e, data, sockets):
    data.report['failed'] = True
    data.report['error_message'] = str(e) + traceback.format_exc()
    data.report_tag(['failed'])
    await sockets.send(data, 'report')
    print(traceback.format_exc())


def create_sample_and_report(sockets, analysis_sys):
    data = sockets.receive()

    s = Sample.create(uri=data.sample_uri, domain=data.sample_domain, port=data.sample_port, ipv4=data.sample_ipv4,
                      ipv6=data.sample_ipv6, filename=data.sample_filename, file=data.sample_file,
                      tlp_level=data.sample_tlp_level, tags=data.sample_tags)
    request = analysis_sys.create_request(s)
    request.create_report(json_report_objects=data.report['json_report_objects'],
                          raw_report_objects=data.report['raw_report_objects'],
                          additional_metadata=data.report['additional_metadata'],
                          tags=data.report['tags'],
                          analysis_date=data.report['analysis_date'],
                          failed=data.report['failed'],
                          error_message=data.report['error_message'])


def get_requests(sockets, analysis_sys):
    """Default Stage to get requests from the MASS Server.

    This function should be used as a parameter of the :func:`frame.add_stage` function.

    :param analysis_sys: Specify this parameter over the args parameter of add_stage
    """

    def func(request, sample):
        request_obj = RequestObject(request, sample)
        sockets.send(request_obj)
        return True

    analysis_sys.consume_requests(func)


def report(sockets):
    """Default stage to report analysis results to the MASS Server.

    This function should be used as a parameter of the :func:`frame.add_stage` function.
    It waits until it gets a RequestObject over the queue.

    """
    data = sockets.receive()
    print('report_stage', flush=True)
    data.request.create_report(json_report_objects=data.report['json_report_objects'],
                               raw_report_objects=data.report['raw_report_objects'],
                               additional_metadata=data.report['additional_metadata'],
                               tags=data.report['tags'],
                               analysis_date=data.report['analysis_date'],
                               failed=data.report['failed'],
                               error_message=data.report['error_message'],
                               use_queue=True)


async def get_http(sockets, error_handler=error_handling_async, parallel_requests=300, conn_timeout=60):
    async def fetch(url, text, cookies, headers, status, redirects):
        async with sem:
            async with session.get(url, allow_redirects=True) as response:
                raw_data = {}
                if text:
                    text = await response.read()
                    raw_data['text'] = text
                if headers:
                    raw_data['headers'] = dict(response.headers)
                if cookies:
                    raw_data['cookies'] = response.cookies
                if status:
                    raw_data['status'] = response.status
                if redirects:
                    raw_data['redirects'] = len(response.history)
                raw_data['url'] = url
                return raw_data

    async def req(urls, text, cookies, headers, status, redirects):
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(fetch(url, text, cookies, headers, status, redirects), loop=sockets.loop))
        return await asyncio.gather(*tasks)

    async def run():
        while True:
            data = await sockets.receive()
            urls = data.get_instruction(sockets, 'url_list')
            text = data.get_instruction(sockets, 'text')
            cookies = data.get_instruction(sockets, 'cookies')
            headers = data.get_instruction(sockets, 'headers')
            status = data.get_instruction(sockets, 'status')
            redirects = data.get_instruction(sockets, 'redirects')

            try:
                future = await asyncio.ensure_future(req(urls, text, cookies, headers, status, redirects), loop=sockets.loop)

            except Exception as e:
                await error_handler(e, data, sockets)
            else:
                if sockets.next_stage:
                    data.make_stage_report(sockets, future)
                    await sockets.send(data)
                else:
                    data.make_instructed_stage_report(sockets, future)
                    # if data.stage_instruction =
                    await sockets.send_instructed(data)

    sem = asyncio.Semaphore(parallel_requests)
    async with ClientSession(loop=sockets.loop, timeout=ClientTimeout(total=conn_timeout),
                             connector=TCPConnector(verify_ssl=False)) as session:
        await asyncio.gather(*[run() for _ in range(parallel_requests)])