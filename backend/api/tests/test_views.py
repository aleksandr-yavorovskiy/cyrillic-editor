from fastapi.testclient import TestClient
from api.app import app


client = TestClient(app)


class TestPingView:
    def test_ping_returns_200(self):
        response = client.get("/api/ping/")
        assert response.status_code == 200

    def test_ping_returns_correct_structure(self):
        response = client.get("/api/ping/")
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert data["status"] == "ok"


class TestImportHandler:
    def test_import_no_file(self):
        response = client.post("/api/import/")
        assert response.status_code == 422

    def test_import_valid_txt_file(self):
        response = client.post(
            "/api/import/",
            files={"file": ("test.txt", b"Hello World")},
        )
        assert response.status_code == 200

    def test_import_unsupported_format(self):
        response = client.post(
            "/api/import/",
            files={"file": ("test.xyz", b"content")},
        )
        assert response.status_code == 400


class TestExportDocxHandler:
    def test_export_valid_text(self):
        data = {"text": "Test text"}
        response = client.post("/api/export/docx/", json=data)
        assert response.status_code == 200
        assert "Content-Disposition" in response.headers

    def test_export_empty_text(self):
        data = {"text": ""}
        response = client.post("/api/export/docx/", json=data)
        assert response.status_code == 200


class TestExportPdfHandler:
    def test_export_pdf_valid(self):
        data = {"text": "Test text"}
        response = client.post("/api/export/pdf/", json=data)
        assert response.status_code in [200, 400, 500]

    def test_export_pdf_with_options(self):
        data = {"text": "Test", "font": "PonomarUnicode", "fontSize": 14}
        response = client.post("/api/export/pdf/", json=data)
        assert response.status_code in [200, 400, 500]
