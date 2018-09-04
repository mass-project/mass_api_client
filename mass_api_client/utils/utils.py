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
from traceback import format_exception, print_tb

import requests

from mass_api_client import resources

logging.getLogger(__name__).addHandler(logging.NullHandler())


def handle_failed_analysis_request(analysis_request, e, use_queue=False):
    exc_str = ''.join(format_exception(*e))
    exc_type = e[0].__name__
    print_tb(e[2])
    metadata = {
        'exception type': exc_type
    }

    try:
        analysis_request.create_report(additional_metadata=metadata,
                                       tags=['failed_analysis', 'exception:{}'.format(exc_type)],
                                       raw_report_objects={'traceback': ('traceback', exc_str)}, failed=True,
                                       error_message=exc_str, use_queue=use_queue)
    except Exception:
        logging.error('Could not create a report on the server.')


def get_or_create_analysis_system(identifier='', verbose_name='', tag_filter_exp='',
                                  time_schedule=None, number_retries=0, minutes_before_retry=0):
    """Get or create an analysis system with the respective identifier.

    This is a function for solving a common problem with implementations of MASS analysis clients.
    If the analysis system already exists, one can retrieve the analysis system with the identifier.
    Otherwise one wants to create an analysis system with the given identifier.

    :param identifier: Get an instance for an analysis system with the given identifier as string.
    :param verbose_name: The verbose name of the respective analysis system.
    :param tag_filter_exp: The tag filter expression as a string of the respective analysis system.
    :param time_schedule: A list of integers. Each number represents the minutes after which a request will be scheduled.3
    :param number_retries: The number of times a sample will be rescheduled after a failed analysis.
    :param minutes_before_retry: The amount of time to wait before rescheduling a sample after a failed analysis.
    :return: a analysis system instance
    """
    if time_schedule is None:
        time_schedule = [0]

    try:
        analysis_system = resources.AnalysisSystem.get(identifier)
    except requests.HTTPError:
        analysis_system = resources.AnalysisSystem.create(identifier, verbose_name, tag_filter_exp, time_schedule, number_retries, minutes_before_retry)

    return analysis_system


