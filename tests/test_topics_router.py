import unittest
from unittest.mock import Mock, patch
from routers import topics as topics_router

from fastapi.testclient import TestClient
from main import app
from schemas.reply import Reply
from schemas.topic import Topic, SingleTopic

client = TestClient(app)

def fake_category():
    category = Mock()
    category.is_locked = False
    category.is_private = False

    return category

class TopicsRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        self.test_topics = [Topic.from_query_result(id=1, title="Test Topic", content="Test Content",
                                               is_locked=False, category_id=1, created_at=None,
                                               best_reply_id=None, author_id=1),
                            Topic.from_query_result(id=2, title="Test Topic 2", content="Test Content 2",
                                               is_locked=False, category_id=1, created_at=None,
                                               best_reply_id=None, author_id=1)]

        self.test_replies = [Reply.from_query_result(id=1, content="Test Reply", topic_id=1, created_at=None,
                                                     is_best_reply=False, author_id=1, vote_count=0),
                             Reply.from_query_result(id=2, content="Test Reply 2", topic_id=1, created_at=None,
                                                     is_best_reply=False, author_id=1, vote_count=0)]

        self.topic_with_replies = SingleTopic(topic=self.test_topics[0],
                                               all_replies=self.test_replies)

        app.dependency_overrides = {
            topics_router.get_current_user: lambda: 1
        }

    def tearDown(self) -> None:
        app.dependency_overrides = {}

    def test_getAllTopics_return_topics_when_DataIsPresent(self):
        # Arrange
        with patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_get_all_topics:
            # Act
            response = client.get("/topics/")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_get_all_topics.assert_called_once()

    def test_getAllTopics_return_emptyList_when_noDataIsPresent(self):
        # Arrange
        with patch('services.topic_service.get_all_topics',
                   return_value=[]) as mock_get_all_topics:
            # Act
            response = client.get("/topics/")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([], response.json())
            mock_get_all_topics.assert_called_once()

    def test_getAllTopics_return_topics_whenSortAsc(self):
        # Arrange
        with (patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_get_all_topics,
             patch('services.topic_service.sort_topics',
                   return_value=self.test_topics) as mock_sort_topics):

            # Act
            response = client.get("/topics/?sort=asc")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_get_all_topics.assert_called_once()
            mock_sort_topics.assert_called_once_with(self.test_topics, reverse=False)

    def test_getAllTopics_return_topics_when_sortDesc(self):
        # Arrange
        with (patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_get_all_topics,
              patch('services.topic_service.sort_topics',
                  return_value=self.test_topics[::-1]) as mock_sort_topics):

            # Act
            response = client.get("/topics/?sort=desc")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics[::-1]], response.json())
            mock_get_all_topics.assert_called_once()
            mock_sort_topics.assert_called_once_with(self.test_topics, reverse=True)

    def test_getAllTopics_return_notFound_when_authorDoesNotExist(self):
        # Arrange
        with patch('services.user_service.id_exists',
                   return_value=False) as mock_id_exists:
            # Act
            response = client.get("/topics/?author_id=1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('Author not found', response.json()['detail'])
            mock_id_exists.assert_called_once()

    def test_getAllTopics_return_forbiddenAccess_when_categoryId_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch('services.category_service.exists',
                    return_value=True) as mock_exists,
              patch('services.category_service.validate_user_access',
                    return_value=False) as mock_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin):
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('User does not have access to this category', response.json()['detail'])
            mock_exists.assert_called_once_with(1)
            mock_validate_user_access.assert_called_once_with(1, 1)
            mock_is_admin.assert_called_once_with(1)

    def test_getAllTopics_return_topics_when_categoryId_userNotAdmin_userHasAccess(self):
        # Arrange
        with (patch('services.category_service.exists',
                    return_value=True) as mock_exists,
              patch('services.category_service.validate_user_access',
                    return_value=True) as mock_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin,
              patch('services.topic_service.get_all_topics',
                    return_value=self.test_topics) as mock_get_all_topics):
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_validate_user_access.assert_called_once_with(1, 1)
            mock_is_admin.assert_called_once_with(1)
            mock_get_all_topics.assert_called_once()
            mock_exists.assert_called_once_with(1)

    def test_getAllTopics_return_notFound_when_categoryId_categoryDoesNotExist(self):
        # Arrange
        with patch('services.category_service.exists',
                   return_value=False) as mock_exists:
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('Category not found', response.json()['detail'])
            mock_exists.assert_called_once_with(1)


    def test_getAllTopics_return_topics_when_isLocked_isTrue(self):
        # Arrange
        with (patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_get_all_topics):
            # Act
            response = client.get("/topics/?is_locked=true")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_get_all_topics.assert_called_once_with(None, None, None, True, 1, 10, 0)

    def test_getById_return_topic(self):
        # Arrange
        with (patch('services.topic_service.get_topic_by_id',
                   return_value=self.topic_with_replies) as mock_get_topic_by_id):
            # Act
            response = client.get("/topics/1")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.topic_with_replies.model_dump(), response.json())
            mock_get_topic_by_id.assert_called_once_with(1)

    def test_getById_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch('services.category_service.validate_user_access',
                    return_value=False) as mock_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin):
            # Act
            response = client.get("/topics/1")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('User does not have access to this category', response.json()['detail'])
            mock_validate_user_access.assert_called_once_with(1, 1)
            mock_is_admin.assert_called_once_with(1)

    def test_getById_return_topic_when_userNotAdmin_userHasAccess(self):
        pass
