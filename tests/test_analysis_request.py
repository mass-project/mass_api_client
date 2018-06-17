import json

from httmock import HTTMock, urlmatch

from mass_api_client.resources import AnalysisRequest
from tests.httmock_test_case import HTTMockTestCase
from tests.serialization_test_case import SerializationTestCase


class AnalysisReqestTestCase(SerializationTestCase, HTTMockTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/analysis_request.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(AnalysisRequest, data)

    def test_get_sample(self):
        with open('tests/data/analysis_request.json') as data_file:
            @urlmatch()
            def mass_mock(url, req):
                return open('tests/data/file_sample.json').read()

            with HTTMock(mass_mock):
                analysis_request = AnalysisRequest._create_instance_from_data(json.load(data_file))
                sample = analysis_request.get_sample()
                self.assertEqual(sample.unique_features.file.file_size, 10302)