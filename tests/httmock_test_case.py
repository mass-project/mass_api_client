import unittest

from mass_api_client import ConnectionManager


class HTTMockTestCase(unittest.TestCase):
    def setUp(self):
        self.api_key = '1234567890abcdef'
        self.base_url = 'http://localhost/api/'
        self.example_data = {'lorem': 'ipsum', 'integer': 1}
        ConnectionManager().register_connection(api_key=self.api_key, base_url=self.base_url, alias='default')
        self.connection = ConnectionManager().get_connection('default')

    def assertAuthorized(self, request):
        self.assertEqual(request.headers['Authorization'], 'APIKEY {}'.format(self.api_key))

    def assertHasForm(self, request, form_index, file, content_type=None):
        request_form = request.original.files[form_index]
        self.assertEqual(request_form[0], None)
        self.assertEqual(request_form[1], file)

        if content_type:
            self.assertEqual(request_form[2], content_type)

    def assertHasFile(self, request, file_index, file_name, file, content_type=None):
        request_file = request.original.files[file_index]
        self.assertEqual(request_file[0], file_name)
        self.assertEqual(request_file[1], file)

        if content_type:
            self.assertEqual(request_file[2], content_type)
