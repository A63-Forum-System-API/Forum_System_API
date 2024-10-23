import unittest
from unittest.mock import Mock
from routers import messages as messages_router


mock_message_service = Mock(spec='services.message_service')
mock_user_service = Mock(spec='services.user_service')


messages_router.product_service = mock_message_service
messages_router.order_service = mock_user_service


class MessageRouterShould(unittest.TestCase):

    def setUp(self) -> None:
        mock_message_service.reset_mock()
        mock_user_service.reset_mock()

    def test_createMessage_returns404_whenReceiverIdDoesNotExist(self):
        # Arrange
        receiver_id = 1
        message = Mock()
        message.text = 'text'
        mock_user_service.id_exists = lambda x: False

        # Act
        result = messages_router.create_message(receiver_id, message)

        # Assert
        self.assertEqual(404, result.status_code)