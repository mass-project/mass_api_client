import json

from mass_api_client import ConnectionManager
from mass_api_client.resources import ScheduledAnalysis
from mass_api_client.resources import FileSample
from tests.serialization_test_case import SerializationTestCase
from tests.httmock_test_case import HTTMockTestCase
from httmock import HTTMock, urlmatch

class ScheduledAnalysisTestCase(SerializationTestCase, HTTMockTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/scheduled_analysis.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(ScheduledAnalysis(), data)

    def test_get_sample(self):
        with open('tests/data/scheduled_analysis.json') as data_file:
            @urlmatch()
            def mass_mock(url, req):
                return open('tests/data/file_sample.json').read()

            with HTTMock(mass_mock):
                scheduled_analysis = ScheduledAnalysis._create_instance_from_data(json.load(data_file))
                sample = scheduled_analysis.get_sample()
                self.assertEqual(sample.file_size, 924449)
             
