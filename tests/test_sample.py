import json
import tempfile

from httmock import urlmatch, HTTMock

from mass_api_client.resources import DomainSample, IPSample, URISample, FileSample, ExecutableBinarySample
from tests.httmock_test_case import HTTMockTestCase
from tests.serialization_test_case import SerializationTestCase


class DomainSampleTestCase(SerializationTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/domain_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(DomainSample, data)


class IPSampleTestCase(SerializationTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/ip_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(IPSample, data)


class URISampleTestCase(SerializationTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/uri_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(URISample, data)


class FileSampleTestCase(SerializationTestCase, HTTMockTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/file_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(FileSample, data)

    def test_temporary_file(self):
        @urlmatch()
        def mass_mock(url, req):
            return b'Content'

        with open('tests/data/file_sample.json') as data_file:
            data = json.load(data_file)

        file_sample = FileSample._create_instance_from_data(data)
        with HTTMock(mass_mock):
            with file_sample.temporary_file() as f:
                self.assertTrue(isinstance(f, tempfile._TemporaryFileWrapper))
                f.seek(0)
                self.assertEqual(f.read(), b'Content')


class ExecutableBinarySampleTestCase(SerializationTestCase):
    def test_is_data_correct_after_serialization(self):
        with open('tests/data/executable_binary_sample.json') as data_file:
            data = json.load(data_file)

        self.assertEqualAfterSerialization(ExecutableBinarySample, data)
 
