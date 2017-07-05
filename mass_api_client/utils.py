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
import requests
from mass_api_client import resources
import logging
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_or_create_analysis_system_instance(instance_uuid='', identifier='', verbose_name='', tag_filter_exp='', uuid_file='uuid.txt'):
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
    :return: a analysis system instance
    """
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
        analysis_system = resources.AnalysisSystem.create(identifier, verbose_name, tag_filter_exp)
    analysis_system_instance = analysis_system.create_analysis_system_instance()
    with open(uuid_file, 'w') as uuid_fp:
        uuid_fp.write(analysis_system_instance.uuid)
    return analysis_system_instance


def process_analyses(analysis_system_instance, analysis_method, sleep_time):
    """Process all analyses which are scheduled for the analysis system instance.

    This function does not terminate on its own, give it a SIGINT or Ctrl+C to stop.

    :param analysis_system_instance: The analysis system instance for which the analyses are scheduled.
    :param analysis_method: A function or method which analyses a scheduled analysis. The function must not take further arguments.
    :param sleep_time: Time to wait between polls to the MASS server
    """
    try:
        while True:
            for analysis_request in analysis_system_instance.get_scheduled_analyses():
                analysis_method(analysis_request)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logging.debug('Shutting down.')
        return
