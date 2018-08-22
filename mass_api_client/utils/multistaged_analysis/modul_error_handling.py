import logging
import os
import traceback

sentry_dsn = os.getenv('SENTRY_DSN', None)
if sentry_dsn:
    from raven import Client
    client = Client(sentry_dsn)


def error_handling_sync_sentry(e, data, sockets):
    if sentry_dsn:
        client.captureException()
    else:
        print('ERROR: Cannot capture because SENTRY_DSN is not defined. Using stdout instead:')
        print(traceback.format_exc())
    data.report['failed'] = True
    data.report['error_message'] = str(e) + traceback.format_exc()
    data.report_tag(['failed'])
    print(traceback.format_exc())
    sockets.send(data, 'report')

async def error_handling_async_sentry(e, data, sockets):
    if sentry_dsn:
        client.captureException()
    else:
        print('ERROR: Cannot capture because SENTRY_DSN is not defined. Using stdout instead:')
        print(traceback.format_exc())
    data.report['failed'] = True
    data.report['error_message'] = str(e) + traceback.format_exc()
    data.report_tag(['failed'])
    await sockets.send(data, 'report')
    print(traceback.format_exc())


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

"""class ModuleErrorHandlerStdout:
    def __init__(self):
        print('StageErrorHandlerStdout contructed')
        handler = 

    def handle(self, e):
        traceback.print_exc(file=sys.stdout)


class ModuleErrorHandlerSentry:
    def __init__(self):
        self.sentry_dsn = os.getenv('SENTRY_DSN', None)
        if self.sentry_dsn:
            self.client = Client(self.sentry_dsn)
        else:
            print('ERROR: SENTRY_DSN is not defined.')

    def handle(self, e):
        if self.sentry_dsn:
            self.client.captureException()
        else:
            print('ERROR: Cannot capture because SENTRY_DSN is not defined.')"""
