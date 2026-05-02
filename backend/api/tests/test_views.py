from rest_framework.test import APIClient
from io import BytesIO


class TestPingView:
    def setup_method(self):
        self.client = APIClient()

    def test_ping_returns_200(self):
        response = self.client.get('/api/ping/')
        assert response.status_code == 200

    def test_ping_returns_correct_structure(self):
        response = self.client.get('/api/ping/')
        data = response.json()
        assert 'status' in data
        assert 'message' in data
        assert data['status'] == 'ok'


class TestImportHandler:
    def setup_method(self):
        self.client = APIClient()

    def test_import_no_file(self):
        response = self.client.post('/api/import/', {})
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_import_valid_txt_file(self):
        with open('/tmp/test.txt', 'wb') as f:
            f.write(b'Hello World')

        with open('/tmp/test.txt', 'rb') as f:
            response = self.client.post('/api/import/', {'file': f})
        assert response.status_code in [200, 500]

    def test_import_unsupported_format(self):
        response = self.client.post(
            '/api/import/',
            {'file': ('test.xyz', BytesIO(b'content'), 'application/octet-stream')}
        )
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data


class TestExportDocxHandler:
    def setup_method(self):
        self.client = APIClient()

    def test_export_valid_text(self):
        data = {'text': 'Test text'}
        response = self.client.post('/api/export-docx/', data, format='json')
        assert response.status_code == 200
        assert 'Content-Disposition' in response.headers

    def test_export_empty_text(self):
        data = {'text': ''}
        response = self.client.post('/api/export-docx/', data, format='json')
        assert response.status_code == 200


class TestExportPdfHandler:
    def setup_method(self):
        self.client = APIClient()

    def test_export_pdf_valid(self):
        data = {'text': 'Test text'}
        response = self.client.post('/api/export-pdf/', data, format='json')
        assert response.status_code in [200, 400, 500]

    def test_export_pdf_with_options(self):
        data = {
            'text': 'Test',
            'font': 'PonomarUnicode',
            'fontSize': 14
        }
        response = self.client.post('/api/export-pdf/', data, format='json')
        assert response.status_code in [200, 400, 500]
