import unittest
from unittest.mock import patch
from schemas.message import Message
from services import message_service


class MessageServiceShould(unittest.TestCase):
    def test_create_returns_message_when_dataIsPresent(self):
        with patch('services.message_service.get_user_by_id') as mock_get_user_by_id:
            with patch('services.message_service.insert_query') as mock_insert_query:
                with patch('services.message_service._get_conversation_id') as mock_get_conversation_id:
                    # Arrange
                    message = Message(text="test")
                    mock_get_user_by_id.return_value.first_name = "Test"
                    mock_insert_query.return_value = 1
                    mock_get_conversation_id.return_value = 1

                    # Act
                    result = message_service.create(message, 1, 1)

                    # Assert
                    self.assertEqual("The message to Test was sent successfully!", result)

    def test_get_conversation_id_returns_conversation_id_withPreviousConv_when_dataIsPresent(self):
        with patch('services.message_service.conversation_service.get_conversation_id') as mock_get_conversation_id:
            with patch('services.message_service.insert_query') as mock_insert_query:
                with patch('services.message_service.read_query') as mock_read_query:
                    # Arrange
                    mock_get_conversation_id.return_value = 1

                    # Act
                    result = message_service._get_conversation_id(1, 1)

                    # Assert
                    self.assertEqual(1, result)
                    mock_insert_query.assert_not_called()
                    mock_read_query.assert_not_called()

    def test_get_conversation_id_returns_conversation_id_withNoPreviousConv_when_dataIsPresent(self):
        with patch('services.message_service.conversation_service.get_conversation_id') as mock_get_conversation_id:
            with patch('services.message_service.insert_query') as mock_insert_query:
                with patch('services.message_service.read_query') as mock_read_query:
                    # Arrange
                    mock_get_conversation_id.return_value = None
                    mock_read_query.return_value = [(1,)]

                    # Act
                    result = message_service._get_conversation_id(1, 1)

                    # Assert
                    self.assertEqual(1, result)
                    mock_insert_query.assert_called_once()
                    mock_read_query.assert_called_once()