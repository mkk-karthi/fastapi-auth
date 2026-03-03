import io
import os
import pathlib

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestUser:
    def test_create_user(self):
        # Validation error
        response = client.post(
            "/api/users",
            json={},
        )
        assert response.status_code == 422
        result = response.json()
        assert len(result["error"]) == 3
        assert result["error"]["name"] == "Field required"
        assert result["error"]["email"] == "Field required"
        assert result["error"]["password"] == "Field required"

        # invalid data
        response = client.post(
            "/api/users",
            json={"name": "demo", "email": "demogmail.com", "password": "Test"},
        )
        assert response.status_code == 422
        result = response.json()
        assert len(result["error"]) == 2
        assert "email" in result["error"]
        assert "password" in result["error"]

        # Success create
        response = client.post(
            "/api/users",
            json={"name": "demo", "email": "demo@gmail.com", "password": "Test@123"},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["id"] >= 1

        # Duplicate email
        response = client.post(
            "/api/users",
            json={"name": "demo", "email": "demo@gmail.com", "password": "Test@123"},
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Email already exist"

    def test_list_user(self):
        response = client.get("/api/users?size=10&page=1")
        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]["items"]) > 0
        assert result["data"]["total"] > 0

    def test_get_user(self):
        # Success
        response = client.get("/api/users/1")
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["id"] == 1

        # Get invalid id
        response = client.get("/api/users/12")
        assert response.status_code == 404

    def test_update_user(self):
        # Validation error
        response = client.put("/api/users/1", json={"name": ""})
        assert response.status_code == 422
        result = response.json()
        assert result["error"]["name"] == "String should have at least 3 characters"

        # Success update
        response = client.put("/api/users/1", json={"name": "test"})
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["name"] == "test"

        # Invalid id
        response = client.put("/api/users/12", json={"name": "test"})
        assert response.status_code == 404

    def test_upload_avatar(self, tmp_path: pathlib.Path):
        with TestClient(app) as client:
            # Invalid file
            file_name = "test.txt"
            path = tmp_path / file_name
            path.write_bytes(b"This is a test file content.")

            with open(path, "rb") as file:
                files = {"avatar": (file_name, file)}
                response = client.post("/api/users/upload-avatar/1", files=files)

            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "Invalid file type"

            # Success
            # Create a dummy image file for testing
            file = io.BytesIO(b"fake image content")
            files = {"avatar": ("avatar.png", file, "image/png")}

            response = client.post("/api/users/upload-avatar/1", files=files)

            result = response.json()
            print(result)
            assert response.status_code == 200

    def test_delete_user(self):
        # Success delete
        response = client.delete("/api/users/1")
        assert response.status_code == 200

        # Invalid id delete
        response = client.delete("/api/users/1")
        assert response.status_code == 404
