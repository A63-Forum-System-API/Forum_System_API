import unittest
from datetime import timedelta
from unittest.mock import patch

import test_data as td
from schemas.category import Category, ViewAllCategories
from schemas.topic import ViewAllTopics, SingleTopic, Topic, CreateTopicRequest, ListOfTopics
from services import category_service


class CategoryService_Should(unittest.TestCase):
    def test_get_categories_returns_list_of_categories_when_data(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT)
        category_2 = (2, "Title Private", "Description Private", True, True, td.TEST_CREATED_AT)
        current_user_id = 1

        with (patch('services.category_service.read_query',
                return_value=[category_1, category_2]) as mock_read_query,
                patch('services.category_service.user_service') as mock_user_service):
            mock_user_service.is_admin.return_value = True
            
            expected = [
                ViewAllCategories.from_query_result(*category_1),
                ViewAllCategories.from_query_result(*category_2)
            ]

            # Act
            result = category_service.get_categories(
                search=None, sort=None, sort_by=None,
                limit=10, offset=0,
                current_user_id=current_user_id,)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()
            mock_user_service.is_admin.assert_called_once_with(current_user_id)

    
    def test_get_categories_returns_correct_query_when_admin(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT)
        category_2 = (2, "Title Private", "Description Private", True, True, td.TEST_CREATED_AT)
        current_user_id = 1
        limit = 10
        offset = 0

        with patch('services.category_service.read_query') as mock_read_query, \
             patch('services.category_service.user_service') as mock_user_service:
            
            mock_user_service.is_admin.return_value = True
            
            expected_query = (
            "SELECT id, title, description, is_private, is_locked, created_at "
            "FROM categories "
            "WHERE is_private in (0, 1) "
            "LIMIT ? OFFSET ?"
        )
            expected_params = [limit, offset]

            mock_read_query.return_value = [category_1, category_2]

            # Act
            category_service.get_categories(
            search=None, sort=None, sort_by=None,
            limit=10, offset=0,
            current_user_id=current_user_id,)
            
            actual_query, actual_params = mock_read_query.call_args[0]
            normalized_expected_query = " ".join(expected_query.split())
            normalized_actual_query = " ".join(actual_query.split())

            # Assert
            self.assertEqual(normalized_expected_query, normalized_actual_query)
            self.assertEqual(expected_params, actual_params)
            mock_user_service.is_admin.assert_called_once_with(current_user_id)
    

    def test_get_categories_returns_correct_query_when_not_admin(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT)
        category_2 = (2, "Title Private", "Description Private", True, True, td.TEST_CREATED_AT)
        current_user_id = 1
        limit = 10
        offset = 0

        with patch('services.category_service.read_query') as mock_read_query, \
             patch('services.category_service.user_service') as mock_user_service:
            
            mock_user_service.is_admin.return_value = False
            
            expected_query = (
            "SELECT id, title, description, is_private, is_locked, created_at "
            "FROM categories "
            "LEFT JOIN category_accesses ca "
            "ON categories.id = ca.category_id "
            "WHERE (is_private = 0 OR (ca.user_id = ?)) "
            "LIMIT ? OFFSET ?"
        )
            expected_params = [current_user_id, limit, offset]

            mock_read_query.return_value = [category_1]

            # Act
            category_service.get_categories(
            search=None, sort=None, sort_by=None,
            limit=10, offset=0,
            current_user_id=current_user_id,)
            
            actual_query, actual_params = mock_read_query.call_args[0]
            normalized_expected_query = " ".join(expected_query.split())
            normalized_actual_query = " ".join(actual_query.split())

            # Assert
            self.assertEqual(normalized_expected_query, normalized_actual_query)
            self.assertEqual(expected_params, actual_params)
            mock_user_service.is_admin.assert_called_once_with(current_user_id)


    def test_get_categories_returns_correct_query_when_search(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT)
        category_2 = (2, "Title Private", "Description Private", True, True, td.TEST_CREATED_AT)
        current_user_id = 1
        limit = 10
        offset = 0
        search="Public"

        with patch('services.category_service.read_query') as mock_read_query, \
             patch('services.category_service.user_service') as mock_user_service:
            
            mock_user_service.is_admin.return_value = False
            
            expected_query = (
            "SELECT id, title, description, is_private, is_locked, created_at "
            "FROM categories "
            "LEFT JOIN category_accesses ca "
            "ON categories.id = ca.category_id "
            "WHERE (is_private = 0 OR (ca.user_id = ?)) "
            "AND lower(title) LIKE ? "
            "LIMIT ? OFFSET ?"
        )
            expected_params = [current_user_id, f"%{search.lower()}%", limit, offset]

            mock_read_query.return_value = [category_1]

            # Act
            category_service.get_categories(
            search=search, sort=None, sort_by=None,
            limit=10, offset=0,
            current_user_id=current_user_id,)
            
            actual_query, actual_params = mock_read_query.call_args[0]
            normalized_expected_query = " ".join(expected_query.split())
            normalized_actual_query = " ".join(actual_query.split())

            # Assert
            self.assertEqual(normalized_expected_query, normalized_actual_query)
            self.assertEqual(expected_params, actual_params)
            mock_user_service.is_admin.assert_called_once_with(current_user_id)


    def test_get_categories_returns_correct_query_when_sort_and_sort_by(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT)
        category_2 = (2, "Title Private", "Description Private", False, True, td.TEST_CREATED_AT)
        current_user_id = 1
        limit = 10
        offset = 0
        sort="desc"
        sort_by="title"

        with patch('services.category_service.read_query') as mock_read_query, \
             patch('services.category_service.user_service') as mock_user_service:
            
            mock_user_service.is_admin.return_value = False
            
            expected_query = (
            "SELECT id, title, description, is_private, is_locked, created_at "
            "FROM categories "
            "LEFT JOIN category_accesses ca "
            "ON categories.id = ca.category_id "
            "WHERE (is_private = 0 OR (ca.user_id = ?)) "
            f"ORDER BY {sort_by} {sort} "
            "LIMIT ? OFFSET ?"
        )
            expected_params = [current_user_id, limit, offset]

            mock_read_query.return_value = [category_2, category_1]

            # Act
            category_service.get_categories(
            search=None, sort=sort, sort_by=sort_by,
            limit=10, offset=0,
            current_user_id=current_user_id,)
            
            actual_query, actual_params = mock_read_query.call_args[0]
            normalized_expected_query = " ".join(expected_query.split())
            normalized_actual_query = " ".join(actual_query.split())

            # Assert
            self.assertEqual(normalized_expected_query, normalized_actual_query)
            self.assertEqual(expected_params, actual_params)
            mock_user_service.is_admin.assert_called_once_with(current_user_id)


    def test_get_category_topics_when_data(self):
        # Arrange
        test_topic_1 = (1, td.TEST_TITLE, False, td.TEST_CREATED_AT, 1, 1)
        test_topic_2 = (2, td.TEST_TITLE, True, td.TEST_CREATED_AT, 2, 1)

        category_id = 1

        with patch('services.category_service.read_query') as mock_read_query:

            mock_read_query.return_value = [test_topic_1, test_topic_2]

            expected = [
                ListOfTopics(id=1, title=td.TEST_TITLE, is_locked=False, created_at=td.TEST_CREATED_AT, author_id=1, category_id=1),
                ListOfTopics(id=2, title=td.TEST_TITLE, is_locked=True, created_at=td.TEST_CREATED_AT, author_id=2, category_id=1)
            ]

            # Act
            result = category_service.get_category_topics(category_id=category_id)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()
    

    def test_get_category_topics_returns_empty_list_when_not_data(self):
        # Arrange
        category_id = 1

        with patch('services.category_service.read_query') as mock_read_query:

            mock_read_query.return_value = []
            expected = []

            # Act
            result = category_service.get_category_topics(category_id=category_id)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()
    
    
    def test_get_by_id_returns_correct_query(self):
        # Arrange
        category_1 = (1, "Title Public", "Description Public", False, False, td.TEST_CREATED_AT, 2)
        category_id = 1

        with patch('services.category_service.read_query') as mock_read_query:
            
            expected_query = (
            "SELECT id, title, description, is_private, is_locked, created_at, admin_id "
            "FROM categories "
            "WHERE id = ?"
        )
            expected_params = (category_id,)

            mock_read_query.return_value = [category_1]

            # Act
            category_service.get_by_id(category_id=category_id)
            
            actual_query, actual_params = mock_read_query.call_args[0]
            normalized_expected_query = " ".join(expected_query.split())
            normalized_actual_query = " ".join(actual_query.split())

            # Assert
            self.assertEqual(normalized_expected_query, normalized_actual_query)
            self.assertEqual(expected_params, actual_params)
