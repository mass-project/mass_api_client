import json
from httmock import HTTMock, urlmatch
from mass_api_client.utils import create_analysis_system_instance
from mass_api_client.utils import process_analyses
from tests.httmock_test_case import HTTMockTestCase
import subprocess

class UtilsTestCase(HTTMockTestCase):
    def test_create_analysis_system_with_uuid(self):
        @urlmatch()
        def mass_mock(url, req):
            return open('tests/data/analysis_system_instance.json').read()

        with HTTMock(mass_mock):
           analysis_system_instance = create_analysis_system_instance("5a391093-f251-4c08-991d-26fc5e0e5793")
           self.assertEqual(analysis_system_instance.uuid, "5a391093-f251-4c08-991d-26fc5e0e5793")

    def test_create_analysis_system_without_uuid(self):
        @urlmatch()
        def mass_mock(url, req):
            if url.path.endswith('strings/'):
                return open('tests/data/analysis_system.json').read()
            else:
                return open('tests/data/analysis_system_instance.json').read()

        with HTTMock(mass_mock):
           analysis_system_instance = create_analysis_system_instance(instance_uuid='', identifier='strings', verbose_name='Strings', tag_filter_exp='')
           self.assertEqual(analysis_system_instance.uuid, "5a391093-f251-4c08-991d-26fc5e0e5793")
