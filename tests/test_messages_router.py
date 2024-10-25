import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from common.auth import get_current_user
from main import app
from schemas.message import Message

client = TestClient(app)

class TestCreateMessage(unittest.TestCase):

    def setUp(self):
        self.message = Message(text="Hello")
        app.dependency_overrides = {
            get_current_user: lambda: 1
        }

    def tearDown(self):
        app.dependency_overrides = {}

    @patch('services.user_service.id_exists', return_value=False)
    def test_create_message_returns_404_when_receiver_id_does_not_exist(self, mock_id_exists):
        response = client.post("/messages/1", json=self.message.dict())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User ID: 1 not found"})

    def test_create_message_returns_400_when_message_is_empty(self):
        self.message.text = "   "
        response = client.post("/messages/1", json=self.message.dict())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Message cannot be empty"})

    @patch('services.user_service.id_exists', return_value=True)
    @patch('services.message_service.create', return_value={"id": 1, "text": "Hello"})
    def test_create_message_success(self, mock_create, mock_id_exists):
        response = client.post("/messages/1", json=self.message.dict())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "text": "Hello"})