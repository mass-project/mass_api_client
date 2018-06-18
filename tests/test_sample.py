import json
import tempfile

from httmock import urlmatch, HTTMock

from mass_api_client.resources import Sample
from tests.httmock_test_case import HTTMockTestCase
from tests.serialization_test_case import SerializationTestCase


class FileSampleTestCase(SerializationTestCase, HTTMockTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/file_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(Sample, data)

    def test_temporary_file(self):
        @urlmatch()
        def mass_mock(url, req):
            return b'Content'

        with open('tests/data/file_sample.json') as data_file:
            data = json.load(data_file)

        file_sample = Sample._create_instance_from_data(data)
        with HTTMock(mass_mock):
            with file_sample.temporary_file() as f:
                self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
                f.seek(0)
                self.assertEqual(f.read(), b'Content')

    def test_convenience_functions(self):
        with open('tests/data/file_sample.json') as f:
            data = Sample._deserialize(json.load(f))
        file_sample = Sample._create_instance_from_data(data)

        self.assertTrue(file_sample.has_file())
        self.assertFalse(file_sample.has_domain())
        self.assertFalse(file_sample.has_ipv4())
        self.assertFalse(file_sample.has_ipv6())
        self.assertFalse(file_sample.has_port())
        self.assertFalse(file_sample.has_uri())
