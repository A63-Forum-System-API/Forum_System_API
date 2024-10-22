import unittest
from unittest.mock import patch
import test_data as td
from schemas.reply import Reply, CreateReplyRequest
from services import reply_service


class ReplyService_Should(unittest.TestCase):

    def test_getById_returns_reply_when_dataIsPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1, td.TEST_CONTENT, 1, td.TEST_CREATED_AT, 0, 1, 1)]

            expected = Reply.from_query_result(1, td.TEST_CONTENT, 1, td.TEST_CREATED_AT, 0, 1, 1)

            # Act
            result = reply_service.get_by_id(1)

            # Arrange
            self.assertEqual(expected, result)

    def test_getById_returns_None_when_dataIsNotPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = reply_service.get_by_id(1)

            # Arrange
            self.assertIsNone(result)
            mock_read_query.assert_called_once()

    def test_idExists_returns_True_when_dataIsPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = reply_service.id_exists(1)

            # Arrange
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_idExists_returns_False_when_dataIsNotPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = reply_service.id_exists(1)

            # Arrange
            self.assertFalse(result)
            mock_read_query.assert_called_once()

    def test_create_returns_reply_when_dataIsPresent(self):
        with patch('services.reply_service.insert_query') as mock_insert_query:
            with patch('services.reply_service.get_by_id') as mock_get_by_id:
                # Arrange
                mock_insert_query.return_value = 1
                mock_get_by_id.return_value = Reply.from_query_result(1, td.TEST_CONTENT, 1,
                                                                      td.TEST_CREATED_AT, 0,
                                                                      1, 1)

                create_reply = CreateReplyRequest(content=td.TEST_CONTENT, topic_id=1)

                expected = Reply.from_query_result(1, td.TEST_CONTENT, 1,
                                                   td.TEST_CREATED_AT, 0,
                                                   1, 1)

                # Act
                result = reply_service.create(create_reply, 1)

                # Arrange
                self.assertEqual(expected, result)
                mock_insert_query.assert_called_once()
                mock_get_by_id.assert_called_once()

    def test_replyBelongsToTopic_returns_True_when_dataIsPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = reply_service.reply_belongs_to_topic(1, 1)

            # Arrange
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_replyBelongsToTopic_returns_False_when_dataIsNotPresent(self):
        with patch('services.reply_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = reply_service.reply_belongs_to_topic(1, 1)

            # Arrange
            self.assertFalse(result)
            mock_read_query.assert_called_once()