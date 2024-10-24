import unittest
from unittest.mock import patch
from schemas.user import UserCreate, User, UserUpdate,UserLogIn
from services import user_service


class UserServiceShould(unittest.TestCase):
    def fake_user(self):
        return User(
            username='validuser',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            picture='some_picture_url'
        )

    def test_is_admin_returnsTrue_when_dataIsPresent(self):
        with patch('services.user_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = user_service.is_admin(1)

            # Arrange
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_is_admin_returnsFalse_when_dataIsNotPresent(self):
        with patch('services.user_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(0,)]

            # Act
            result = user_service.is_admin(1)

            # Arrange
            self.assertFalse(result)
            mock_read_query.assert_called_once()

    def test_idExists_returns_True_when_dataIsPresent(self):
        with patch('services.user_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = user_service.id_exists(1)

            # Arrange
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_idExists_returns_False_when_dataIsNotPresent(self):
        with patch('services.user_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = user_service.id_exists(1)

            # Arrange
            self.assertFalse(result)
            mock_read_query.assert_called_once()

    def test_get_user_by_id_returns_user_when_dataIsPresent(self):
        with patch('services.user_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [('validuser',
                                            'John', 'Doe',
                                            'john.doe@example.com',
                                            'some_picture_url')]

            # Act
            result = user_service.get_user_by_id(1)

            # Assert
            self.assertEqual(self.fake_user(), result)
            mock_read_query.assert_called_once()



