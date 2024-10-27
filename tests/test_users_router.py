import unittest
from unittest.mock import Mock, patch

import mariadb
from fastapi.testclient import TestClient

from common.auth import get_current_user
from main import app
from schemas.user import UserCreate

client = TestClient(app)


class UsersRouterShould(unittest.TestCase):

    def setUp(self):
        self.user = UserCreate(username="testuser", email="testuser@example.com", password="Password1!",
                               first_name="Test", last_name="User")
        app.dependency_overrides = {
            get_current_user: lambda: 1
        }

        self.form_data = {
            "username": "testuser",
            "password": "Password1!"
        }

    def tearDown(self):
        app.dependency_overrides = {}

    @patch('services.user_service.create', return_value={"id": 1, "username": "testuser"})
    def test_create_user_success(self, mock_create):
        response = client.post("/users/register", json=self.user.model_dump())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1, "username": "testuser"})

    @patch('services.user_service.create', side_effect=mariadb.IntegrityError("username_UNIQUE"))
    def test_create_user_username_already_exists(self, mock_create):
        response = client.post("/users/register", json=self.user.model_dump())
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "User with username 'testuser' already exists"})

    @patch('services.user_service.create', side_effect=mariadb.IntegrityError("email_UNIQUE"))
    def test_create_user_email_already_exists(self, mock_create):
        response = client.post("/users/register", json=self.user.model_dump())
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "User with email 'testuser@example.com' already exists"})

    @patch('services.user_service.create', side_effect=mariadb.IntegrityError("other_error"))
    def test_create_user_internal_server_error(self, mock_create):
        response = client.post("/users/register", json=self.user.model_dump())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "An unexpected error occurred"})

    @patch('common.auth.authenticate_user', return_value=None)
    def test_login_invalid_credentials(self, mock_authenticate_user):
        response = client.post("/users/login", data=self.form_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid username or password"})

    @patch('services.user_service.is_admin', return_value=False)
    def test_update_user_only_admin_access(self, mock_is_admin):
        response = client.put("/users/2", params={"is_admin": True})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Only admin can update user status"})

    @patch('services.user_service.is_admin', return_value=True)
    @patch('services.user_service.id_exists', return_value=False)
    def test_update_user_not_found(self, mock_id_exists, mock_is_admin):
        response = client.put("/users/2", params={"is_admin": True})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User ID: 2 not found"})

    @patch('services.user_service.is_admin', return_value=True)
    @patch('services.user_service.id_exists', return_value=True)
    def test_update_user_bad_request(self, mock_id_exists, mock_is_admin):
        app.dependency_overrides[get_current_user] = lambda: 2
        response = client.put("/users/2", params={"is_admin": True})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "You are not allowed to update your own user status"})

    @patch('services.user_service.is_admin', return_value=True)
    @patch('services.user_service.id_exists', return_value=True)
    @patch('services.user_service.is_admin', return_value=True)
    def test_update_user_forbidden_access(self, mock_is_admin1, mock_id_exists, mock_is_admin2):
        app.dependency_overrides[get_current_user] = lambda: 3
        response = client.put("/users/2", params={"is_admin": True})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "This user is already an admin"})

    @patch('services.user_service.is_admin', return_value=True)
    @patch('services.user_service.id_exists', return_value=True)
    @patch('services.user_service.update', return_value={"id": 2, "is_admin": True})
    def test_update_user_success(self, mock_update, mock_id_exists, mock_is_admin):
        response = client.put("/users/2", params={"is_admin": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 2, "is_admin": True})