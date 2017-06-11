from httmock import all_requests, HTTMock

from mass_api_client import switch_connection
from mass_api_client.resources import Sample
from tests.httmock_test_case import HTTMockTestCase


class SwitchConnectionTestCase(HTTMockTestCase):
    def test_retrieving_subclass_with_non_default_connection(self):
        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://notlocalhost/api/sample/580a2429a7a7f126d0cc0d10/', request.original.url)
            with open('tests/data/file_sample.json') as fp:
                return fp.read()

        with switch_connection(Sample, 'secondary'), HTTMock(mass_mock_result):
            Sample.get('580a2429a7a7f126d0cc0d10')

    def test_resetting_active_connection_after_switch(self):
        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://localhost/api/sample/580a2429a7a7f126d0cc0d10/', request.original.url)
            with open('tests/data/file_sample.json') as fp:
                return fp.read()

        with switch_connection(Sample, 'secondary'):
            pass

        with HTTMock(mass_mock_result):
            Sample.get('580a2429a7a7f126d0cc0d10')
