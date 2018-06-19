from mass_api_client import ConnectionManager
from mass_api_client.utils import get_or_create_analysis_system

from staged_analysis import AnalysisFrame, get_requests, report


async def example_stage_async(sockets):
    data = await sockets.receive()
    data.report['tags'] = ['one', 'two']
    await sockets.send(data, 'example_stage_sync')


def example_stage_sync(sockets):
    data = sockets.receive()
    data.report['json_report_objects'] = {'new_report': ('new_report', {'three': 'four'})}
    sockets.send(data, 'report')


if __name__ == '__main__':
    ConnectionManager().register_connection('default',
                                            'IjViMjgwNWVmNjEzYmM2MTViODllZWI1MSI.3tKl1aD90uoUfrhgS4Kwvka3DV4',
                                            'http://127.0.0.1:8000/api/', timeout=60)
    analysis_system_instance = get_or_create_analysis_system(identifier='example',
                                                             verbose_name='Example Analysis Client',
                                                             tag_filter_exp='sample-type:filesample',
                                                             )

    frame = AnalysisFrame(
        ["tcp://127.0.0.1:5559", "tcp://127.0.0.1:5560", "tcp://127.0.0.1:5561", "tcp://127.0.0.1:5562",
         "tcp://127.0.0.1:5563", "tcp://127.0.0.1:5564", "tcp://127.0.0.1:5565", "tcp://127.0.0.1:5566"])
    frame.add_stage(get_requests, 'requests', args=(analysis_system_instance, 'example_stage_async'))
    frame.add_stage(example_stage_async, 'example_stage_async', concurrency='async')
    frame.add_stage(example_stage_sync, 'example_stage_sync')
    frame.add_stage(report, 'report', replicas=3)
    frame.start_all_stages()
