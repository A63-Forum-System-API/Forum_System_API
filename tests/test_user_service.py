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

    @patch('services.user_service.get_password_hash')
    @patch('services.user_service.insert_query')
    def test_create_returns_user_when_dataIsPresent(self, mock_insert_query, mock_get_password_hash):
        # Arrange
        mock_get_password_hash.return_value = 'hashed_password'
        user = UserCreate(username='validuser',
                          first_name='John',
                          last_name='Doe',
                          email='john.doe@example.com',
                          password='Example123@',
                          picture='some_picture_url')

        # Act
        result = user_service.create(user)

        # Assert
        expected_user = User(username='validuser',
                             first_name='John',
                             last_name='Doe',
                             email='john.doe@example.com',
                             picture='some_picture_url')
        self.assertEqual(result, expected_user)
        mock_get_password_hash.assert_called_once_with('Example123@')
        mock_insert_query.assert_called_once_with(
            """
            INSERT INTO users(username, first_name, last_name, email, hash_password, picture)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            ('validuser', 'John', 'Doe', 'john.doe@example.com', 'hashed_password', 'some_picture_url')
        )

    @patch('services.user_service.insert_query')
    def test_update_sets_user_as_admin(self, mock_insert_query):
        # Arrange
        user_id = 1
        is_admin = True

        # Act
        result = user_service.update(user_id, is_admin)

        # Assert
        expected_message = {"msg": "User with #ID 1 successfully updated to admin"}
        self.assertEqual(result, expected_message)
        mock_insert_query.assert_called_once_with(
            """
            UPDATE users
            SET is_admin = ?
            WHERE id = ?
            """,
            (is_admin, user_id)
        )

    @patch('services.user_service.insert_query')
    def test_update_sets_user_as_regular(self, mock_insert_query):
        # Arrange
        user_id = 1
        is_admin = False

        # Act
        result = user_service.update(user_id, is_admin)

        # Assert
        expected_message = {"msg": "User with #ID 1 successfully updated to regular user!"}
        self.assertEqual(result, expected_message)
        mock_insert_query.assert_called_once_with(
            """
            UPDATE users
            SET is_admin = ?
            WHERE id = ?
            """,
            (is_admin, user_id)
        )
