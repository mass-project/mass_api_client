import json

from httmock import urlmatch, HTTMock

from mass_api_client.resources import *
from mass_api_client.resources.base import BaseResource
from tests.httmock_test_case import HTTMockTestCase


class ObjectCreationTestCase(HTTMockTestCase):
    def assertCorrectHTTPDetailCreation(self, resource, path, metadata, data_path):
        with open(data_path) as data_file:
            response_data = json.load(data_file)

        data = {}
        for key, value in metadata.items():
            if isinstance(value, BaseResource):
                data[key] = value.url
            else:
                data[key] = value

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_creation(url, request):
            print(request.body)
            self.assertAuthorized(request)
            self.assertEqual(json.loads(request.body), data)
            return json.dumps(response_data)

        with HTTMock(mass_mock_creation):
            obj = resource.create(**metadata)
            self.assertEqual(response_data, obj._to_json())

    def assertCorrectHTTPDetailCreationWithFile(self, resource, path, metadata, data_path, filename, file):
        with open(data_path) as data_file:
            response_data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_creation(url, request):
            self.assertAuthorized(request)
            self.assertHasFile(request, 'file', filename, file)
            self.assertHasForm(request, 'metadata', json.dumps(metadata), content_type='application/json')
            return json.dumps(response_data)

        with HTTMock(mass_mock_creation):
            obj = resource.create(filename=filename, file=file, **metadata)
            self.assertEqual(response_data, obj._to_json())

    def setUp(self):
        super(ObjectCreationTestCase, self).setUp()

        with open('tests/data/analysis_system.json') as f:
            data = AnalysisSystem._deserialize(json.load(f))
            self.analysis_system = AnalysisSystem._create_instance_from_data(data)

        with open('tests/data/analysis_system_instance.json') as f:
            data = AnalysisSystemInstance._deserialize(json.load(f))
            self.analysis_system_instance = AnalysisSystemInstance._create_instance_from_data(data)

        with open('tests/data/file_sample.json') as f:
            data = FileSample._deserialize(json.load(f))
            self.file_sample = FileSample._create_instance_from_data(data)

    def test_creating_analysis_system(self):
        data = {'identifier_name': 'identifier', 'verbose_name': 'Verbose name', 'tag_filter_expression': ''}
        self.assertCorrectHTTPDetailCreation(AnalysisSystem, r'/api/analysis_system/', data,
                                             'tests/data/analysis_system.json')

    def test_creating_analysis_system_instance(self):
        data = {'analysis_system': self.analysis_system}
        self.assertCorrectHTTPDetailCreation(AnalysisSystemInstance, r'/api/analysis_system_instance/', data,
                                             'tests/data/analysis_system_instance.json')

    def test_creating_scheduled_analysis(self):
        data = {
            'analysis_system_instance': self.analysis_system_instance,
            'sample': self.file_sample}
        self.assertCorrectHTTPDetailCreation(ScheduledAnalysis, r'/api/scheduled_analysis/', data,
                                             'tests/data/scheduled_analysis.json')

    def test_creating_domain_sample(self):
        data = {'domain': 'uni-bonn.de', 'tlp_level': 0}
        self.assertCorrectHTTPDetailCreation(DomainSample, r'/api/sample/submit_domain/', data,
                                             'tests/data/domain_sample.json')

    def test_creating_ip_sample(self):
        data = {'ip_address': '192.168.1.1', 'tlp_level': 0}
        self.assertCorrectHTTPDetailCreation(IPSample, r'/api/sample/submit_ip/', data,
                                             'tests/data/ip_sample.json')

    def test_creating_uri_sample(self):
        data = {'uri': 'http://uni-bonn.de/test', 'tlp_level': 0}
        self.assertCorrectHTTPDetailCreation(URISample, r'/api/sample/submit_uri/', data, 'tests/data/uri_sample.json')

    def test_creating_file_sample(self):
        with open('tests/data/test_data', 'rb') as file:
            data = {'tlp_level': 0}
            self.assertCorrectHTTPDetailCreationWithFile(FileSample, r'/api/sample/submit_file/', data,
                                                         'tests/data/file_sample.json', 'test_data', file)

    def test_creating_analysis_request(self):
        data = {
            'analysis_system': self.analysis_system,
            'sample': self.file_sample
            }

        @urlmatch()
        def mass_server(url, request):
            return open('tests/data/analysis_request.json', 'r').read()

        with HTTMock(mass_server):
            analysis_request = AnalysisRequest.create(self.file_sample, self.analysis_system)
            data = json.load(open('tests/data/analysis_request.json', 'r'))
            self.assertEqual(data, analysis_request._to_json())
