from fastapi.testclient import TestClient
from api.app import app


client = TestClient(app)


class TestAuthRegister:
    def test_register_success(self):
        response = client.post("/api/auth/register/", json={
            "username": "newuser",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["username"] == "newuser"

    def test_register_duplicate(self):
        client.post("/api/auth/register/", json={
            "username": "dupuser",
            "password": "password123",
        })
        response = client.post("/api/auth/register/", json={
            "username": "dupuser",
            "password": "password123",
        })
        assert response.status_code == 409

    def test_register_short_username(self):
        response = client.post("/api/auth/register/", json={
            "username": "ab",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_short_password(self):
        response = client.post("/api/auth/register/", json={
            "username": "validuser",
            "password": "12345",
        })
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self):
        response = client.post("/api/auth/token/", json={
            "username": "expert",
            "password": "expert123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["username"] == "expert"

    def test_login_wrong_password(self):
        response = client.post("/api/auth/token/", json={
            "username": "expert",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_wrong_username(self):
        response = client.post("/api/auth/token/", json={
            "username": "nonexistent",
            "password": "somepass",
        })
        assert response.status_code == 401

    def test_login_empty_username(self):
        response = client.post("/api/auth/token/", json={
            "username": "",
            "password": "somepass",
        })
        assert response.status_code == 422


class TestAuthVerify:
    def test_verify_valid_token(self):
        login_resp = client.post("/api/auth/token/", json={
            "username": "expert",
            "password": "expert123",
        })
        token = login_resp.json()["token"]

        response = client.get("/api/auth/verify/", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_verify_invalid_token(self):
        response = client.get("/api/auth/verify/", headers={
            "Authorization": "Bearer invalid-token",
        })
        assert response.status_code == 401

    def test_verify_no_token(self):
        response = client.get("/api/auth/verify/")
        assert response.status_code == 401
