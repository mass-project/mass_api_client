import asyncio
import time
import traceback

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from mass_api_client.resources import *

from .multistaged_analysis import RequestObject
from .modul_error_handling import error_handling_async_sentry


def create_sample_and_report(sockets, analysis_system):
    data = sockets.receive()
    s = Sample.create(uri=data.sample_uri, domain=data.sample_domain, port=data.sample_port, ipv4=data.sample_ipv4,
                      ipv6=data.sample_ipv6, filename=data.sample_filename, file=data.sample_filename,
                      tlp_level=data.sample_tlp_level, tags=data.sample_tags)
    Report.create_without_request(s, analysis_system, tags=data.report['tags'],
                                  json_report_objects=data.report['json_report_objects'],
                                  raw_report_objects=data.report['raw_report_objects'],
                                  additional_metadata=data.report['additional_metadata'],
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
    data.request.create_report(json_report_objects=data.report['json_report_objects'],
                               raw_report_objects=data.report['raw_report_objects'],
                               additional_metadata=data.report['additional_metadata'],
                               tags=data.report['tags'],
                               analysis_date=data.report['analysis_date'],
                               failed=data.report['failed'],
                               error_message=data.report['error_message'],
                               use_queue=True)


def _decode(byte_body, headers):
    ct = None
    if 'Content-Type' in headers:
        ct = 'Content-Type'
    elif 'content-type' in headers:
        ct = 'content-type'
    if ct:
        if 'iso-8859-1' in headers[ct].lower():
            return byte_body.decode('iso-8859-1', 'ignore')
        if 'iso-8859-2' in headers[ct].lower():
            return byte_body.decode('iso-8859-2', 'ignore')
        else:
            return byte_body.decode('utf-8', 'ignore')
    else:
        return byte_body.decode('utf-8', 'ignore')


async def get_http(sockets, error_handler=error_handling_async_sentry, parallel_requests=300, conn_timeout=60,
                   stream_timeout=300):
    async def fetch(url, args):
        async with sem:
            if args['client_headers']:
                await session.post(url, headers=args['client_headers'])
            async with session.get(url, allow_redirects=True) as response:
                raw_data = {}
                if args['text']:
                    if args['stream']:
                        start_time, byte_body = time.time(), b''
                        async for data in response.content.iter_chunked(1024):
                            if time.time() - start_time > stream_timeout:
                                raise ValueError('Timeout reached. Downloading the contents took too long.')
                            byte_body += data
                        raw_data['text'] = _decode(byte_body, dict(response.headers))
                    else:
                        byte_body = await response.read()
                        raw_data['text'] = _decode(byte_body, dict(response.headers))
                if args['headers']:
                    headers = response.headers
                    raw_data['headers'] = {}
                    for head in iter(headers):
                        if head not in raw_data['headers']:
                            raw_data['headers'][head] = headers[head]
                        elif isinstance(raw_data['headers'][head], str):
                            raw_data['headers'][head] = (raw_data['headers'][head], headers[head])
                        else:
                            raw_data['headers'][head] = raw_data['headers'][head] + (headers[head],)
                if args['cookies']:
                    raw_data['cookies'] = response.cookies
                if args['status']:
                    raw_data['status'] = response.status
                if args['redirects']:
                    raw_data['redirects'] = len(response.history)
                raw_data['url'] = url
                raw_data['error'] = False
                return raw_data

    async def req(args):
        tasks = []
        urls = args.pop('urls')
        for url in urls:
            tasks.append(asyncio.ensure_future(fetch(url, args), loop=sockets.loop))
        return await asyncio.gather(*tasks)

    async def run():
        while True:
            data = await sockets.receive()
            args = {'urls': data.get_instruction(sockets, 'url_list'),
                    'text': data.get_instruction(sockets, 'text'),
                    'cookies': data.get_instruction(sockets, 'cookies'),
                    'headers': data.get_instruction(sockets, 'headers'),
                    'status': data.get_instruction(sockets, 'status'),
                    'redirects': data.get_instruction(sockets, 'redirects'),
                    'client_headers': data.get_instruction(sockets, 'client_headers'),
                    'stream': data.get_instruction(sockets, 'stream')}

            try:
                future = await asyncio.ensure_future(req(args), loop=sockets.loop)

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