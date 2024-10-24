import unittest
from unittest.mock import patch

from services import vote_service


class VoteService_Should(unittest.TestCase):

    def test_exists_return_True_when_voteExists(self):
        # Arrange
        with patch('services.vote_service.read_query') as mock_read_query:
            mock_read_query.return_value = [(1,)]

            # Act
            result = vote_service.get_vote(1, 1)

            # Assert
            self.assertEqual(True, result)

    def test_exists_return_False_when_voteDoesNotExist(self):
        # Arrange
        with patch('services.vote_service.read_query') as mock_read_query:
            mock_read_query.return_value = []

            # Act
            result = vote_service.get_vote(1, 1)

            # Assert
            self.assertEqual(None, result)

    def test_createVote_calls_insertQuery(self):
        # Arrange
        with patch('services.vote_service.insert_query') as mock_insert_query:
            # Act
            vote_service.create_vote(1, 1, 1)

            # Assert
            mock_insert_query.assert_called_once()

    def test_updateVote_calls_updateQuery(self):
        # Arrange
        with patch('services.vote_service.update_query') as mock_update_query:
            # Act
            vote_service.update_vote(1, 1, 1)

            # Assert
            mock_update_query.assert_called_once()

    def test_deleteVote_calls_deleteQuery(self):
        # Arrange
        with patch('services.vote_service.delete_query') as mock_delete_query:
            # Act
            vote_service.delete_vote(1, 1)

            # Assert
            mock_delete_query.assert_called_once()