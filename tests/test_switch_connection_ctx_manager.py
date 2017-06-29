from httmock import all_requests, HTTMock

from mass_api_client import SwitchConnection
from mass_api_client.resources import Sample, Report
from tests.httmock_test_case import HTTMockTestCase


class SwitchConnectionTestCase(HTTMockTestCase):
    def test_retrieving_class_with_non_default_connection(self):
        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://notlocalhost/api/report/58362185a7a7f10843133337/', request.original.url)
            with open('tests/data/report.json') as fp:
                return fp.read()

        with SwitchConnection(Report, 'secondary') as ModifiedReport, HTTMock(mass_mock_result):
            report = ModifiedReport.get('58362185a7a7f10843133337')

        self.assertEqual(report.connection_alias, 'secondary')

    def test_retrieving_subclass_with_non_default_connection(self):
        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://notlocalhost/api/sample/580a2429a7a7f126d0cc0d10/', request.original.url)
            with open('tests/data/file_sample.json') as fp:
                return fp.read()

        with SwitchConnection(Sample, 'secondary') as Sample1, HTTMock(mass_mock_result):
            sample = Sample1.get('580a2429a7a7f126d0cc0d10')

        self.assertEqual(sample.connection_alias, 'secondary')

    def test_resetting_active_connection_after_switch(self):
        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://localhost/api/sample/580a2429a7a7f126d0cc0d10/', request.original.url)
            with open('tests/data/file_sample.json') as fp:
                return fp.read()

        with SwitchConnection(Sample, 'secondary') as Sample1:
            pass

        with HTTMock(mass_mock_result):
            Sample.get('580a2429a7a7f126d0cc0d10')
