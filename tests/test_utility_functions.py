from unittest import mock

from httmock import HTTMock, urlmatch

from mass_api_client import utils
from tests.httmock_test_case import HTTMockTestCase


class UtilsTestCase(HTTMockTestCase):
    def test_create_analysis_system(self):
        @urlmatch()
        def mass_mock(url, req):
            return open('tests/data/analysis_system.json').read()

        with HTTMock(mass_mock):
           analysis_system = utils.get_or_create_analysis_system("strings")
           self.assertEqual(analysis_system.identifier_name, "strings")

    def test_create_analysis_system_without_analysis_system(self):
        @urlmatch()
        def mass_mock(url, req):
            if url.path.endswith('strings/') and req.method == 'GET':
                print('Strings analysis system not yet available')
                return {'status_code': 404, 'content': ''}
            if req.method == 'POST' and url.path.endswith('analysis_system/'):
                print('Posted probably an analysis system')
                return open('tests/data/analysis_system.json').read()
            if req.method == 'POST' and url.path.endswith('analysis_system_instance/'):
                print('Posted probably an analysis system instance')
                return open('tests/data/analysis_system.json').read()

        with HTTMock(mass_mock):
            analysis_system = utils.get_or_create_analysis_system(identifier='strings', verbose_name='Strings', tag_filter_exp='')
            self.assertEqual(analysis_system.identifier_name, 'strings')
