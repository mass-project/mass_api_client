from unittest import mock

from httmock import HTTMock, urlmatch

from mass_api_client import utils
from tests.httmock_test_case import HTTMockTestCase


class UtilsTestCase(HTTMockTestCase):
    def test_create_analysis_system_with_uuid(self):
        @urlmatch()
        def mass_mock(url, req):
            return open('tests/data/analysis_system_instance.json').read()

        with HTTMock(mass_mock):
           analysis_system_instance = utils.get_or_create_analysis_system_instance("5a391093-f251-4c08-991d-26fc5e0e5793")
           self.assertEqual(analysis_system_instance.uuid, "5a391093-f251-4c08-991d-26fc5e0e5793")

    def test_create_analysis_system_without_uuid(self):
        @urlmatch()
        def mass_mock(url, req):
            if url.path.endswith('strings/'):
                return open('tests/data/analysis_system.json').read()
            else:
                return open('tests/data/analysis_system_instance.json').read()

        with HTTMock(mass_mock):
            analysis_system_instance = utils.get_or_create_analysis_system_instance(instance_uuid='', identifier='strings', verbose_name='Strings', tag_filter_exp='')
            self.assertEqual(analysis_system_instance.uuid, "5a391093-f251-4c08-991d-26fc5e0e5793")

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
                return open('tests/data/analysis_system_instance.json').read()

        with HTTMock(mass_mock):
            analysis_system_instance = utils.get_or_create_analysis_system_instance(instance_uuid='', identifier='strings', verbose_name='Strings', tag_filter_exp='')
            self.assertEqual(analysis_system_instance.uuid, '5a391093-f251-4c08-991d-26fc5e0e5793')

    @mock.patch("time.sleep", side_effect=InterruptedError)
    def test_process_analyses_without_scheduled_analyses(self, mocked_sleep):
        asi_mock = mock.Mock()
        asi_mock.get_scheduled_analyses.return_value = []
        analysis_method = mock.Mock()
        analysis_method.return_value = "some report"

        with self.assertRaises(InterruptedError):
            utils.process_analyses(asi_mock, analysis_method, 0)
        self.assertTrue(asi_mock.get_scheduled_analyses.called)
        self.assertFalse(analysis_method.called)

    @mock.patch("time.sleep", side_effect=InterruptedError)
    def test_process_analyses_with_scheduled_analyses(self, mocked_sleep):
        asi_mock = mock.Mock()
        asi_mock.get_scheduled_analyses.side_effect = ["some filesample", []]
        analysis_method = mock.Mock()
        analysis_method.return_value = "some report"

        with self.assertRaises(InterruptedError):
            utils.process_analyses(asi_mock, analysis_method, 0)
        self.assertTrue(asi_mock.get_scheduled_analyses.called)
        self.assertTrue(analysis_method.called)

