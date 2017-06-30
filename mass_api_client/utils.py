import requests
from mass_api_client import resources
import logging
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_analysis_system_instance(instance_uuid='', identifier='', verbose_name='', tag_filter_exp='', uuid_file='uuid.txt'):
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
    try:
        while True:
            for analysis_request in analysis_system_instance.get_scheduled_analyses():
                analysis_method(analysis_request)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logging.debug('Shutting down.')
        return
