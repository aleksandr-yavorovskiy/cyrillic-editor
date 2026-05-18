import uuid

from fastapi.testclient import TestClient
from api.app import app


client = TestClient(app)

FONT_CONTENT = b"fake font content"


def get_token():
    resp = client.post("/api/auth/token/", json={
        "username": "expert",
        "password": "expert123",
    })
    return resp.json()["token"]


def unique_name(prefix):
    return prefix + uuid.uuid4().hex[:8]


class TestListFonts:
    def test_list_fonts_returns_200(self):
        response = client.get("/api/fonts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestUploadFont:
    def test_upload_without_auth(self):
        response = client.post(
            "/api/fonts/",
            data={"name": "NoAuth"},
            files={"file": ("test.ttf", FONT_CONTENT)},
        )
        assert response.status_code == 401

    def test_upload_invalid_extension(self):
        token = get_token()
        response = client.post(
            "/api/fonts/",
            files={"file": ("test.exe", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400

    def test_upload_success(self):
        name = unique_name("Up")
        token = get_token()
        response = client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("test.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name

    def test_upload_duplicate(self):
        name = unique_name("Dup")
        token = get_token()
        client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("test.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("test.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 409

    def test_upload_with_path_traversal_name(self):
        name = "../" + unique_name("Safe")
        token = get_token()
        response = client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("test.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "/" not in data["name"]
        assert data["name"] != name


class TestGetFont:
    def test_get_font_404(self):
        response = client.get("/api/fonts/nonexistent/")
        assert response.status_code == 404

    def test_get_uploaded_font(self):
        name = unique_name("Get")
        token = get_token()
        client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("gettest.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.get(f"/api/fonts/{name}/")
        assert response.status_code == 200
        assert response.content == FONT_CONTENT

    def test_get_font_with_path_traversal(self):
        response = client.get("/api/fonts/../etc/passwd/")
        assert response.status_code == 404


class TestDeleteFont:
    def test_delete_without_auth(self):
        response = client.delete("/api/fonts/somefont/")
        assert response.status_code == 401

    def test_delete_success(self):
        name = unique_name("Del")
        token = get_token()
        client.post(
            "/api/fonts/",
            data={"name": name},
            files={"file": ("del.ttf", FONT_CONTENT)},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = client.delete(
            f"/api/fonts/{name}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    def test_delete_nonexistent(self):
        token = get_token()
        response = client.delete(
            "/api/fonts/nonexistent/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
