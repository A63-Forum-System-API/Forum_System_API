import unittest
from unittest.mock import patch
from schemas.conversation import Conversation
from services import conversation_service


class ConversationServiceShould(unittest.TestCase):

    def test_get_last_message_returns_message_withExistingConvId_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [('test', 1)]
            expected = ('test', 1)

            # Act
            result = conversation_service._get_last_message(1)

            # Arrange
            self.assertEqual(expected, result)

    def test_get_last_message_returns_None_when_dataIsNotPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = conversation_service._get_last_message(1)

            # Arrange
            self.assertIsNone(result)

    def test_get_conversationId_returns_conversationIdWithTheSameUserIds_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(2,)]
            expected = 2

            # Act
            result = conversation_service.get_conversation_id(1, 1)

            # Arrange
            self.assertEqual(expected, result)

    def test_get_conversationId_returns_conversationIdWithDifferentUserIds_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(2,)]
            expected = 2

            # Act
            result = conversation_service.get_conversation_id(1, 2)

            # Arrange
            self.assertEqual(expected, result)

    def test_get_conversation_returns_conversationWithAscOrder_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [
                ("test", "test", "test", "12"),
                ("test", "test", "test", "13")]
            expected = [{"text": "test",
                         "from": "test",
                         "sent_at": "12"},
                        {"text": "test",
                         "from": "test",
                         "sent_at": "13"}]

            # Act
            result = conversation_service.get_conversation(1)

            # Arrange
            self.assertEqual(expected, result)

    def test_get_conversation_returns_conversationWithDescOrder_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [
                ("test", "test", "test", "13"),
                ("test", "test", "test", "12")]
            expected = [{"text": "test",
                         "from": "test",
                         "sent_at": "13"},
                        {"text": "test",
                         "from": "test",
                         "sent_at": "12"}]

            # Act
            result = conversation_service.get_conversation(1, "desc")

            # Arrange
            self.assertEqual(expected, result)

    def test_get_conversation_returns_emptyList_when_dataIsNotPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = conversation_service.get_conversation(1)

            # Arrange
            self.assertEqual([], result)

    def test_get_conversations_returns_conversationsWithAscOrder_when_dataIsPresent(self):
        with patch('services.conversation_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [
                (1, "test", "test", "test", "12"),
                (2, "test", "test", "test", "13")]
            expected = [{"conversation_id": 1,
                         "with": "test",
                         "last_message": "test",
                         "sent_at": "12"},
                        {"conversation_id": 2,
                         "with": "test",
                         "last_message": "test",
                         "sent_at": "13"}]

            # Act
            result = conversation_service.get_conversations(1)

            # Arrange
            self.assertEqual(expected, result)
