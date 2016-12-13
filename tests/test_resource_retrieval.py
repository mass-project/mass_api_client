import json

from httmock import urlmatch, HTTMock

from mass_api_client.resources import AnalysisRequest
from mass_api_client.resources import AnalysisSystem
from mass_api_client.resources import AnalysisSystemInstance
from mass_api_client.resources import Report
from mass_api_client.resources import ScheduledAnalysis
from mass_api_client.resources.sample import DomainSample, FileSample, IPSample, ExecutableBinarySample
from tests.httmock_test_case import HTTMockTestCase


class ReportRetrievalTestCase(HTTMockTestCase):
    def assertCorrectHTTPRetrieval(self, resource, identifier, path, data_path):
        with open(data_path) as data_file:
            data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_detail(url, request):
            self.assertAuthorized(request)
            return json.dumps(data)

        with HTTMock(mass_mock_detail):
            obj = resource.get(identifier)
            self.assertEqual(data, obj._to_json())

    def test_getting_analysis_system_detail(self):
        self.assertCorrectHTTPRetrieval(AnalysisSystem(), 'strings', r'/api/analysis_system/strings/',
                                        'tests/data/analysis_system.json')

    def test_getting_analysis_system_instance_detail(self):
        self.assertCorrectHTTPRetrieval(AnalysisSystemInstance(), '5a391093-f251-4c08-991d-26fc5e0e5793',
                                        r'/api/analysis_system_instance/5a391093-f251-4c08-991d-26fc5e0e5793',
                                        'tests/data/analysis_system_instance.json')

    def test_getting_analysis_request_detail(self):
        self.assertCorrectHTTPRetrieval(AnalysisRequest(), '58399e60a7a7f10cada00463',
                                        r'/api/analysis_request/58399e60a7a7f10cada00463/',
                                        'tests/data/analysis_request.json')

    def test_getting_report_detail(self):
        self.assertCorrectHTTPRetrieval(Report(), '58362185a7a7f10843133337', r'/api/report/58362185a7a7f10843133337/',
                                        'tests/data/report.json')

    def test_getting_ip_sample_detail(self):
        self.assertCorrectHTTPRetrieval(IPSample(), '580a1667a7a7f11628e905eb',
                                        r'/api/sample/580a1667a7a7f11628e905eb/',
                                        'tests/data/ip_sample.json')

    def test_getting_executable_binary_sample_detail(self):
        self.assertCorrectHTTPRetrieval(ExecutableBinarySample(), '5822057fa7a7f10cc420e3b7',
                                        r'/api/sample/5822057fa7a7f10cc420e3b7/',
                                        'tests/data/executable_binary_sample.json')

    def test_getting_domain_sample_detail(self):
        self.assertCorrectHTTPRetrieval(DomainSample(), '580a2413a7a7f126d0cc0d0a',
                                        r'/api/sample/580a2413a7a7f126d0cc0d0a/',
                                        'tests/data/domain_sample.json')

    def test_getting_file_sample_detail(self):
        self.assertCorrectHTTPRetrieval(FileSample(), '580a2429a7a7f126d0cc0d10',
                                        r'/api/sample/580a2429a7a7f126d0cc0d10/',
                                        'tests/data/file_sample.json')

    def test_getting_scheduled_analysis(self):
        self.assertCorrectHTTPRetrieval(ScheduledAnalysis(), '5836367da7a7f1084313338d',
                                        r'/api/scheduled_analysis/5836367da7a7f1084313338d/',
                                        'tests/data/scheduled_analysis.json')
