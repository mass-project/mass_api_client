import json

from httmock import urlmatch, HTTMock

from mass_api_client.resources import *
from mass_api_client.resources.base import BaseResource
from tests.httmock_test_case import HTTMockTestCase


class ObjectCreationTestCase(HTTMockTestCase):
    def assertCorrectHTTPDetailCreation(self, resource, path, metadata, data_path, unique_features=None):
        with open(data_path) as data_file:
            response_data = json.load(data_file)

        if unique_features:
            data = {'unique_features': unique_features}
        else:
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
            parameters = dict(metadata)
            if unique_features:
                parameters.update(unique_features)
            obj = resource.create(**parameters)
            self.assertEqual(response_data, obj._to_json())

    def assertCorrectHTTPDetailCreationWithFile(self, resource, path, metadata, data_path, filename, file, unique_features=None):
        with open(data_path) as data_file:
            response_data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_creation(url, request):
            data = dict(metadata)
            if isinstance(unique_features, dict):
                data['unique_features'] = unique_features
            self.assertAuthorized(request)
            self.assertHasFile(request, 'file', filename, file)
            self.assertHasForm(request, 'metadata', json.dumps(data), content_type='application/json')
            return json.dumps(response_data)

        with HTTMock(mass_mock_creation):
            parameters = dict(metadata)
            if unique_features:
                parameters.update(unique_features)
            obj = resource.create(filename=filename, file=file, **parameters)
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
            data = Sample._deserialize(json.load(f))
            self.file_sample = Sample._create_instance_from_data(data)

        with open('tests/data/sample_relation_type.json') as f:
            data = SampleRelationType._deserialize(json.load(f))
            self.relation_type = SampleRelationType._create_instance_from_data(data)

        with open('tests/data/scheduled_analysis.json') as f:
            data = ScheduledAnalysis._deserialize(json.load(f))
            self.scheduled_analysis = ScheduledAnalysis._create_instance_from_data(data)

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
        data = {'tlp_level': 0, 'tags': []}
        unique_features = {'domain': 'uni-bonn.de'}
        self.assertCorrectHTTPDetailCreation(Sample, r'/api/sample/', data,
                                             'tests/data/domain_sample.json', unique_features)

    def test_creating_ip_sample(self):
        data = {'tlp_level': 0, 'tags': []}
        unique_features = {'ipv4': '192.168.1.1'}
        self.assertCorrectHTTPDetailCreation(Sample, r'/api/sample/', data,
                                             'tests/data/ip_sample.json', unique_features)

    def test_creating_uri_sample(self):
        data = {'tlp_level': 0, 'tags': []}
        unique_features = {'uri': 'http://uni-bonn.de/test'}
        self.assertCorrectHTTPDetailCreation(Sample, r'/api/sample/', data,
                                             'tests/data/uri_sample.json', unique_features)

    def test_creating_file_sample(self):
        with open('tests/data/test_data', 'rb') as file:
            data = {'tlp_level': 0, 'tags': []}
            self.assertCorrectHTTPDetailCreationWithFile(Sample, r'/api/sample/', data,
                                                         'tests/data/file_sample.json', 'test_data', file, {})

    def test_creating_sample_relation_type(self):
        data = {'name': 'Example Relation Type', 'directed': True}
        self.assertCorrectHTTPDetailCreation(SampleRelationType, r'/api/sample_relation_type/', data, 'tests/data/sample_relation_type.json')

    def test_creating_sample_relation(self):
        data = {'sample': self.file_sample, 'other': self.file_sample, 'relation_type': self.relation_type, 'additional_metadata': {'match': 100}}
        self.assertCorrectHTTPDetailCreation(SampleRelation, r'/api/sample_relation/', data, 'tests/data/sample_relation.json')

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
