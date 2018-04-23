import json
import tempfile

from httmock import all_requests, urlmatch, HTTMock

from mass_api_client.resources import AnalysisRequest
from mass_api_client.resources import AnalysisSystem
from mass_api_client.resources import AnalysisSystemInstance
from mass_api_client.resources import Report
from mass_api_client.resources import ScheduledAnalysis
from mass_api_client.resources.sample import Sample
from tests.httmock_test_case import HTTMockTestCase


class ReportRetrievalTestCase(HTTMockTestCase):
    def assertCorrectHTTPDetailRetrieval(self, resource, identifier, path, data_path):
        with open(data_path) as data_file:
            data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_detail(url, request):
            self.assertAuthorized(request)
            return json.dumps(data)

        with HTTMock(mass_mock_detail):
            obj = resource.get(identifier)._to_json()
            self.assertEqual(data, obj)

    def assertCorrectHTTPListRetrieval(self, resource, path, data_path):
        with open(data_path) as data_file:
            data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_list(url, request):
            self.assertAuthorized(request)
            return json.dumps(data)

        with HTTMock(mass_mock_list):
            obj_list = resource.all()

        for data_obj, py_obj in zip(data['results'], obj_list):
            self.assertEqual(data_obj, py_obj._to_json())

    def assertCorrectHTTPIterRetrieval(self, resource, path, data_paths):

        @urlmatch(netloc=r'localhost', path=path)
        def mass_mock_list(url, request):
            data_file = data_paths[0] if url.query == 'per_page=100' else data_paths[1]
            with open(data_file) as data_file:
                data = json.load(data_file)

            self.assertAuthorized(request)
            return json.dumps(data)

        with HTTMock(mass_mock_list):
            obj_list = list(resource.items())

        self.assertEqual(len(obj_list), 4)

    def test_querying_samples(self):
        with open('tests/data/file_sample_list.json') as data_file:
            data = json.load(data_file)

        params = {'tags__contains': 'extension:bin'}

        @all_requests
        def mass_mock_result(url, request):
            self.assertAuthorized(request)
            self.assertEqual('http://localhost/api/sample/', request.original.url)
            self.assertEqual(params, request.original.params)
            return json.dumps(data)

        with HTTMock(mass_mock_result):
            obj_list = Sample.query(tags__contains=params['tags__contains'])
            for data_obj, py_obj in zip(data['results'], obj_list):
                self.assertEqual(data_obj, py_obj._to_json())

    def test_downloading_sample_file(self):
        test_file_path = 'tests/data/test_data'

        @urlmatch(netloc=r'localhost', path=r'/api/sample/59f7908215b77f2a3b562840/download/')
        def mass_mock_file(url, request):
            self.assertAuthorized(request)
            with open(test_file_path, 'rb') as data_file:
                content = data_file.read()
            return content

        with open('tests/data/file_sample.json') as f:
            data = Sample._deserialize(json.load(f))
            file_sample = Sample._create_instance_from_data(data)

        with HTTMock(mass_mock_file), tempfile.TemporaryFile() as tmpfile, open(test_file_path, 'rb') as data_file:
            file_sample.download_to_file(tmpfile)
            tmpfile.seek(0)
            self.assertEqual(data_file.read(), tmpfile.read())

    def test_retrieving_json_report_object(self):
        with open('tests/data/file_sample.json') as data_file:
            json_data = json.load(data_file)

        @urlmatch(netloc=r'localhost', path=r'/api/report/58362185a7a7f10843133337/json_report_object/found_strings/')
        def mass_mock_report_object(url, request):
            self.assertAuthorized(request)
            return json.dumps(json_data)

        with open('tests/data/report.json') as f:
            data = Report._deserialize(json.load(f))
            report = Report._create_instance_from_data(data)

        with HTTMock(mass_mock_report_object):
            retrieved_data = report.get_json_report_object('found_strings')

        self.assertEqual(json_data, retrieved_data)

    def test_retrieving_raw_report_object(self):
        test_file_path = 'tests/data/test_data'

        @urlmatch(netloc=r'localhost', path=r'/api/report/58362185a7a7f10843133337/raw_report_object/graph/')
        def mass_mock_file(url, request):
            self.assertAuthorized(request)
            with open(test_file_path, 'rb') as data_file:
                content = data_file.read()
            return content

        with open('tests/data/report.json') as f:
            data = Report._deserialize(json.load(f))
            report = Report._create_instance_from_data(data)

        with HTTMock(mass_mock_file), tempfile.TemporaryFile() as tmpfile, open(test_file_path, 'rb') as data_file:
            report.download_raw_report_object_to_file('graph', tmpfile)
            tmpfile.seek(0)
            self.assertEqual(data_file.read(), tmpfile.read())

    def test_raising_exception_for_invalid_filter_parameters(self):
        with self.assertRaises(ValueError):
            Sample.query(invalid_filter='example')

    def test_getting_sample_list(self):
        self.assertCorrectHTTPListRetrieval(Sample, r'/api/sample/', 'tests/data/file_sample_list.json')

    def test_getting_sample_iter(self):
        self.assertCorrectHTTPIterRetrieval(Sample, r'/api/sample/', ['tests/data/sample_list_with_paging_1.json', 'tests/data/sample_list_with_paging_2.json'])

    def test_getting_scheduled_analysis_list(self):
        self.assertCorrectHTTPListRetrieval(ScheduledAnalysis, r'/api/scheduled_analysis/', 'tests/data/scheduled_analyses.json')

    def test_getting_analysis_system_detail(self):
        self.assertCorrectHTTPDetailRetrieval(AnalysisSystem, 'strings', r'/api/analysis_system/strings/',
                                              'tests/data/analysis_system.json')

    def test_getting_analysis_system_instance_detail(self):
        self.assertCorrectHTTPDetailRetrieval(AnalysisSystemInstance, '5a391093-f251-4c08-991d-26fc5e0e5793',
                                              r'/api/analysis_system_instance/5a391093-f251-4c08-991d-26fc5e0e5793',
                                              'tests/data/analysis_system_instance.json')

    def test_getting_analysis_request_detail(self):
        self.assertCorrectHTTPDetailRetrieval(AnalysisRequest, '58399e60a7a7f10cada00463',
                                              r'/api/analysis_request/58399e60a7a7f10cada00463/',
                                              'tests/data/analysis_request.json')

    def test_getting_report_detail(self):
        self.assertCorrectHTTPDetailRetrieval(Report, '58362185a7a7f10843133337',
                                              r'/api/report/58362185a7a7f10843133337/',
                                              'tests/data/report.json')

    def test_getting_sample_detail(self):
        self.assertCorrectHTTPDetailRetrieval(Sample, '59f7908215b77f2a3b562840',
                                              r'/api/sample/59f7908215b77f2a3b562840/',
                                              'tests/data/file_sample.json')
