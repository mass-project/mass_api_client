"""Utility functions for writing an analysis client.

Example
-------

import os
from mass_api_client import ConnectionManager
from mass_api_client.utils import process_analyses, get_or_create_analysis_system_instance

def size_analysis(scheduled_analysis):
    sample = scheduled_analysis.get_sample()
    with sample.temporary_file() as f:
        sample_file_size = os.path.getsize(f.name)

    size_report = {'sample_file_size': sample_file_size}
    scheduled_analysis.create_report(
        json_report_objects={'size_report': ('size_report', size_report)},
        )

if __name__ == "__main__":
    ConnectionManager().register_connection('default', 'your api key', 'mass server url')

    analysis_system_instance = get_or_create_analysis_system_instance(identifier='size',
                                                                      verbose_name= 'Size Analysis Client',
                                                                      tag_filter_exp='sample-type:filesample',
                                                                      )
    process_analyses(analysis_system_instance, size_analysis, sleep_time=7)
"""
import logging
import signal
import time
from sys import exc_info
from traceback import format_exception, print_tb

import requests

from mass_api_client import resources

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_or_create_analysis_system_instance(instance_uuid='', identifier='', verbose_name='', tag_filter_exp='',
                                           time_schedule=None, uuid_file='uuid.txt'):
    """Get or create an analysis system instance for the analysis system with the respective identifier.

    This is a function for solving a common problem with implementations of MASS analysis clients.
    If the analysis system instance already exists, one has either a uuid or a file with the uuid as content.
    In this case one can retrieve the analysis system instance with the uuid.
    
    Otherwise one wants to create an instance for the analysis system with the given identifier.
    If the analysis system does not yet exists, it is also created.
    Then an analysis system instance for the analysis system is created and the uuid is saved to the uuid_file.

    :param instance_uuid: If not empty, directly gets the analysis system instance with the given uuid and tries nothing else.
    :param uuid_file: A filepath. If not empty, tries to read an uuid from the filepath. Otherwise the uuid is later saved to this file.
    :param identifier: Get an instance for an analysis system with the given identifier as string.
    :param verbose_name: The verbose name of the respective analysis system.
    :param tag_filter_exp: The tag filter expression as a string of the respective analysis system.
    :param time_schedule: A list of integers. Each number represents the minutes after which a request will be scheduled.
    :return: a analysis system instance
    """
    if time_schedule is None:
        time_schedule = [0]

    if instance_uuid:
        return resources.AnalysisSystemInstance.get(instance_uuid)

    try:
        with open(uuid_file, 'r') as uuid_fp:
            instance_uuid = uuid_fp.read().strip()
            return resources.AnalysisSystemInstance.get(instance_uuid)
    except IOError:
        logging.debug('UUID file does not exist.')

    try:
        analysis_system = resources.AnalysisSystem.get(identifier)
    except requests.HTTPError:
        analysis_system = resources.AnalysisSystem.create(identifier, verbose_name, tag_filter_exp, time_schedule)
    analysis_system_instance = analysis_system.create_analysis_system_instance()
    with open(uuid_file, 'w') as uuid_fp:
        uuid_fp.write(analysis_system_instance.uuid)
    return analysis_system_instance


def process_analyses(analysis_system_instance, analysis_method, sleep_time, delete_instance_on_exit=False, catch_exceptions=False):
    """Process all analyses which are scheduled for the analysis system instance.

    This function does not terminate on its own, give it a SIGINT or Ctrl+C to stop.

    :param analysis_system_instance: The analysis system instance for which the analyses are scheduled.
    :param analysis_method: A function or method which analyses a scheduled analysis. The function must not take further arguments.
    :param sleep_time: Time to wait between polls to the MASS server
    :param delete_instance_on_exit: If true remove the analysis_system_instance on the server before exit.
    :param catch_exceptions: Catch all exceptions during analysis and create a failure report on the server instead of termination.
    """

    def execute_analysis(scheduled_analysis):
        try:
            analysis_method(scheduled_analysis)
        except Exception:
            if not catch_exceptions:
                raise
            e = exc_info()
            exc_str = ''.join(format_exception(*e))
            print_tb(e[2])
            metadata = {
                'exception type': e[0].__name__
            }
            scheduled_analysis.create_report(additional_metadata=metadata,
                                             raw_report_objects={'traceback': ('traceback', exc_str)}, failed=True,
                                             error_message=exc_str)

    def exit_analysis_process(signum, frame):
        if delete_instance_on_exit:
            logging.debug('Deleting AnalysisSystemInstance...')
            analysis_system_instance.delete()
        logging.debug('Shutting down.')
        exit(0)

    signal.signal(signal.SIGINT, exit_analysis_process)
    signal.signal(signal.SIGTERM, exit_analysis_process)

    while True:
        analyses = analysis_system_instance.get_scheduled_analyses()
        for analysis in analyses:
            execute_analysis(analysis)

        if not analyses:
            time.sleep(sleep_time)

