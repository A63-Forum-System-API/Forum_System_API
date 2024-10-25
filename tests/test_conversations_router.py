import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from common.auth import get_current_user
from main import app

client = TestClient(app)

class TestViewConversation(unittest.TestCase):

    def setUp(self):
        app.dependency_overrides = {
            get_current_user: lambda: 1
        }

    def tearDown(self):
        app.dependency_overrides = {}

    @patch('services.user_service.id_exists', return_value=False)
    def test_view_conversation_returns_404_when_receiver_id_does_not_exist(self, mock_id_exists):
        response = client.get("/conversations/1")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User ID: 1 not found"})

    @patch('services.user_service.id_exists', return_value=True)
    @patch('services.conversation_service.get_conversation_id', return_value=None)
    def test_view_conversation_returns_404_when_no_conversation_found(self, mock_get_conversation_id, mock_id_exists):
        response = client.get("/conversations/1")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Conversation with user ID: 1 not found"})

    @patch('services.user_service.id_exists', return_value=True)
    @patch('services.conversation_service.get_conversation_id', return_value=1)
    @patch('services.conversation_service.get_conversation', return_value={"id": 1, "messages": []})
    def test_view_conversation_success(self, mock_get_conversation, mock_get_conversation_id, mock_id_exists):
        response = client.get("/conversations/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "messages": []})

    @patch('services.conversation_service.get_conversations', return_value=[])
    def test_view_conversations_returns_404_when_no_conversations_found(self, mock_get_conversations):
        response = client.get("/conversations/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Conversations not found"})

    @patch('services.conversation_service.get_conversations', return_value=[{"id": 1, "messages": []}])
    def test_view_conversations_success(self, mock_get_conversations):
        response = client.get("/conversations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": 1, "messages": []}])