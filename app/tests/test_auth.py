from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from app.core.helper import generateOtp
from app.main import app

client = TestClient(app)


def mock_generate_otp() -> str:
    return "123456"


app.dependency_overrides[generateOtp] = mock_generate_otp


class TestAuth:
    @patch("app.core.mail.smtplib.SMTP")
    def test_sign(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        with TestClient(app) as client:
            # Validation error
            response = client.post(
                "/api/signin",
                json={},
            )
            assert response.status_code == 422
            result = response.json()
            assert len(result["error"]) == 4
            assert result["error"]["name"] == "Field required"
            assert result["error"]["email"] == "Field required"
            assert result["error"]["password"] == "Field required"
            assert result["error"]["confirm_password"] == "Field required"

            # invalid data
            response = client.post(
                "/api/signin",
                json={
                    "name": "demo",
                    "email": "testgmail.com",
                    "password": "Test",
                    "confirm_password": "",
                },
            )
            assert response.status_code == 422
            result = response.json()
            assert "email" in result["error"]
            assert "password" in result["error"]

            # Invalid confirm password
            response = client.post(
                "/api/signin",
                json={
                    "name": "demo",
                    "email": "test@gmail.com",
                    "password": "Test@123",
                    "confirm_password": "Test@789",
                },
            )
            assert response.status_code == 422
            result = response.json()
            assert "Passwords do not match" in result["error"]["confirm_password"]

            # Success create
            response = client.post(
                "/api/signin",
                json={
                    "name": "demo",
                    "email": "test@gmail.com",
                    "password": "Test@123",
                    "confirm_password": "Test@123",
                },
            )
            assert response.status_code == 200
            result = response.json()
            assert result["data"]["id"] >= 1

            # Duplicate email
            response = client.post(
                "/api/signin",
                json={
                    "name": "demo",
                    "email": "test@gmail.com",
                    "password": "Test@123",
                    "confirm_password": "Test@123",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "Email already exist"

    def test_verify_mail(self):
        with TestClient(app) as client:
            # Validation error
            response = client.post(
                "/api/verify-otp",
                json={},
            )
            assert response.status_code == 422
            result = response.json()
            assert result["error"]["email"] == "Field required"
            assert result["error"]["otp"] == "Field required"

            # Invalid Data error
            response = client.post(
                "/api/verify-otp",
                json={
                    "email": "testgmail.com",
                    "otp": "123",
                },
            )
            assert response.status_code == 422
            result = response.json()
            assert "email" in result["error"]
            assert "otp" in result["error"]

            # Invalid Otp
            response = client.post(
                "/api/verify-otp",
                json={
                    "email": "test@gmail.com",
                    "otp": "123123",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "OTP is invalid"

            # Success
            response = client.post(
                "/api/verify-otp",
                json={
                    "email": "test@gmail.com",
                    "otp": "123456",
                },
            )
            assert response.status_code == 200

            # Once verified again verify the mail
            response = client.post(
                "/api/verify-otp",
                json={
                    "email": "test@gmail.com",
                    "otp": "123456",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "OTP is invalid"

    def test_login(self):
        # Validation error
        response = client.post(
            "/api/login",
            json={},
        )
        assert response.status_code == 422
        result = response.json()
        assert result["error"]["email"] == "Field required"
        assert result["error"]["password"] == "Field required"

        # Invalid Data error
        response = client.post(
            "/api/login",
            json={
                "email": "testgmail.com",
                "password": "Test",
            },
        )
        assert response.status_code == 422
        result = response.json()
        assert "email" in result["error"]
        assert "password" in result["error"]

        # Invalid email
        response = client.post(
            "/api/login",
            json={
                "email": "test1@gmail.com",
                "password": "Test@123",
            },
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Email & password incorrect"

        # Invalid email
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@1234",
            },
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Email & password incorrect"

        # Success
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@123",
            },
        )
        assert response.status_code == 200

    def test_profile(self):
        # Login
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@123",
            },
        )
        assert response.status_code == 200
        result = response.json()
        access_token = result["data"]["token"]

        # Invalid Token
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer "},
        )
        assert response.status_code == 401

        # Success
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer " + access_token},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["email"] == "test@gmail.com"

    def test_change_password(self):
        # Login
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@123",
            },
        )
        assert response.status_code == 200
        result = response.json()
        access_token = result["data"]["token"]

        # Invalid Token
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer "},
            json={
                "old_password": "Test@123",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        assert response.status_code == 401

        # Validation error
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={},
        )
        assert response.status_code == 422
        result = response.json()
        assert result["error"]["old_password"] == "Field required"
        assert result["error"]["password"] == "Field required"

        # Invalid Data error
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={
                "old_password": "Test",
                "password": "Test",
                "confirm_password": "Test",
            },
        )
        assert response.status_code == 422
        result = response.json()
        assert "old_password" in result["error"]
        assert "password" in result["error"]

        # confirm password shoud not same
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={
                "old_password": "Test@123",
                "password": "Test@1234",
                "confirm_password": "Test@12345",
            },
        )
        assert response.status_code == 422
        result = response.json()
        assert "confirm_password" in result["error"]

        # Invalid old password
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={
                "old_password": "Test@1234",
                "password": "Test@123",
                "confirm_password": "Test@123",
            },
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Password is incorrect"

        # Change same password
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={
                "old_password": "Test@123",
                "password": "Test@123",
                "confirm_password": "Test@123",
            },
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Password has been previously used"

        # Success
        response = client.post(
            "/api/change-password",
            headers={"Authorization": "Bearer " + access_token},
            json={
                "old_password": "Test@123",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        assert response.status_code == 200

        # Check login with old password
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@123",
            },
        )
        assert response.status_code == 400
        result = response.json()
        assert result["message"] == "Email & password incorrect"

        # Check login with changed password
        response = client.post(
            "/api/login",
            json={
                "email": "test@gmail.com",
                "password": "Test@1234",
            },
        )
        assert response.status_code == 200

    @patch("app.core.mail.smtplib.SMTP")
    def test_forgot_password(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        with TestClient(app) as client:
            # Validation error
            response = client.post(
                "/api/forgot-password",
                json={},
            )
            assert response.status_code == 422
            result = response.json()
            assert result["error"]["email"] == "Field required"

            # Invalid Data error
            response = client.post(
                "/api/forgot-password",
                json={
                    "email": "testgmail.com",
                },
            )
            assert response.status_code == 422
            result = response.json()
            assert "email" in result["error"]

            # Success
            response = client.post(
                "/api/forgot-password",
                json={
                    "email": "test@gmail.com",
                },
            )
            assert response.status_code == 200

            # Change password
            # Validation error
            response = client.post(
                "/api/reset-password",
                json={},
            )
            assert response.status_code == 422
            result = response.json()
            assert result["error"]["email"] == "Field required"
            assert result["error"]["otp"] == "Field required"
            assert result["error"]["password"] == "Field required"
            assert result["error"]["confirm_password"] == "Field required"

            # Invalid Data error
            response = client.post(
                "/api/reset-password",
                json={
                    "email": "testgmail.com",
                    "otp": "123",
                    "password": "Test",
                    "confirm_password": "Test@1234",
                },
            )
            assert response.status_code == 422
            result = response.json()
            assert "email" in result["error"]
            assert "otp" in result["error"]
            assert "password" in result["error"]

            # Invalid email
            response = client.post(
                "/api/reset-password",
                json={
                    "email": "tests@gmail.com",
                    "otp": "123456",
                    "password": "Test@1234",
                    "confirm_password": "Test@1234",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "OTP is invalid"

            # Invalid otp
            response = client.post(
                "/api/reset-password",
                json={
                    "email": "test@gmail.com",
                    "otp": "123123",
                    "password": "Test@1234",
                    "confirm_password": "Test@1234",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "OTP is invalid"

            # Chanage same password
            response = client.post(
                "/api/reset-password",
                json={
                    "email": "test@gmail.com",
                    "otp": "123456",
                    "password": "Test@1234",
                    "confirm_password": "Test@1234",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "Password has been previously used"

            # success
            response = client.post(
                "/api/reset-password",
                json={
                    "email": "test@gmail.com",
                    "otp": "123456",
                    "password": "Test@123",
                    "confirm_password": "Test@123",
                },
            )
            assert response.status_code == 200

            # Check login with old password
            response = client.post(
                "/api/login",
                json={
                    "email": "test@gmail.com",
                    "password": "Test@1234",
                },
            )
            assert response.status_code == 400
            result = response.json()
            assert result["message"] == "Email & password incorrect"

            # Check login with changed password
            response = client.post(
                "/api/login",
                json={
                    "email": "test@gmail.com",
                    "password": "Test@123",
                },
            )
            assert response.status_code == 200
