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
                   return_value=self.test_topics) as mock_topic_service_get_all_topics:
            # Act
            response = client.get("/topics/")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_topic_service_get_all_topics.assert_called_once()

    def test_getAllTopics_return_emptyList_when_noDataIsPresent(self):
        # Arrange
        with patch('services.topic_service.get_all_topics',
                   return_value=[]) as mock_topic_service_get_all_topics:
            # Act
            response = client.get("/topics/")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([], response.json())
            mock_topic_service_get_all_topics.assert_called_once()

    def test_getAllTopics_return_topics_whenSortAsc(self):
        # Arrange
        with (patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_topic_service_get_all_topics,
             patch('services.topic_service.sort_topics',
                   return_value=self.test_topics) as mock_topic_service_sort_topics):

            # Act
            response = client.get("/topics/?sort=asc")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_topic_service_get_all_topics.assert_called_once()
            mock_topic_service_sort_topics.assert_called_once_with(self.test_topics, reverse=False)

    def test_getAllTopics_return_topics_when_sortDesc(self):
        # Arrange
        with (patch('services.topic_service.get_all_topics',
                   return_value=self.test_topics) as mock_topic_service_get_all_topics,
              patch('services.topic_service.sort_topics',
                  return_value=self.test_topics[::-1]) as mock_topic_service_sort_topics):

            # Act
            response = client.get("/topics/?sort=desc")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics[::-1]], response.json())
            mock_topic_service_get_all_topics.assert_called_once()
            mock_topic_service_sort_topics.assert_called_once_with(self.test_topics, reverse=True)

    def test_getAllTopics_return_notFound_when_authorDoesNotExist(self):
        # Arrange
        with patch('services.user_service.id_exists',
                   return_value=False) as mock_user_service_id_exists:
            # Act
            response = client.get("/topics/?author_id=1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('Author not found', response.json()['detail'])
            mock_user_service_id_exists.assert_called_once()


    def test_getAllTopics_return_forbiddenAccess_when_categoryId_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch('services.category_service.exists',
                    return_value=True) as mock_category_service_exists,
              patch('services.category_service.validate_user_access',
                    return_value=False) as mock_category_service_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_user_service_is_admin):
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('User does not have access to this category', response.json()['detail'])
            mock_category_service_exists.assert_called_once_with(1)
            mock_category_service_validate_user_access.assert_called_once_with(1, 1)
            mock_user_service_is_admin.assert_called_once_with(1)

    def test_getAllTopics_return_topics_when_categoryId_userNotAdmin_userHasAccess(self):
        # Arrange
        with (patch('services.category_service.exists',
                    return_value=True) as mock_category_service_exists,
              patch('services.category_service.validate_user_access',
                    return_value=True) as mock_category_service_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_user_service_is_admin,
              patch('services.topic_service.get_all_topics',
                    return_value=self.test_topics) as mock_topic_service_get_all_topics):
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), list)
            self.assertEqual([t.model_dump() for t in self.test_topics], response.json())
            mock_category_service_validate_user_access.assert_called_once_with(1, 1)
            mock_user_service_is_admin.assert_called_once_with(1)
            mock_topic_service_get_all_topics.assert_called_once()
            mock_category_service_exists.assert_called_once_with(1)

    def test_getAllTopics_return_notFound_when_categoryId_categoryDoesNotExist(self):
        # Arrange
        with patch('services.category_service.exists',
                   return_value=False) as mock_category_service_exists:
            # Act
            response = client.get("/topics/?category_id=1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('Category not found', response.json()['detail'])
            mock_category_service_exists.assert_called_once_with(1)


    # TODO - Add more tests for the rest of the endpoints
    #
    #
    # def test_getTopicById_return_topic_when_userIsNotAdmin_hasAccess(self):
    #     # Arrange
    #     mock_topic_service.get_by_id_with_replies = lambda topic_id: self.topic_with_replies
    #     mock_user_service.is_admin = lambda user_id: False
    #     mock_category_service.validate_user_access = lambda user_id, category_id: True
    #
    #     # Act
    #     response = client.get("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(200, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual(self.topic_with_replies.model_dump(), response.json())
    #
    #
    # def test_getAllTopics_return_notFound_when_categoryDoesNotExist(self):
    #     # Arrange
    #     with patch('services.category_service.exists',
    #                return_value=False):
    #         # Act
    #         response = client.get("/topics/?category_id=1")
    #
    #         # Assert
    #         self.assertEqual(404, response.status_code)
    #         self.assertIsInstance(response.json(), dict)
    #         self.assertEqual('Category not found', response.json()['detail'])
    #
    #
    #
    # def test_createTopic_return_topic_when_categoryExists_userIsAdmin(self):
    #     # Arrange
    #     mock_category_service.get_by_id = lambda category_id: fake_category()
    #     mock_user_service.is_admin = lambda user_id: True
    #     test_topic = self.test_topics[0]
    #     mock_topic_service.create = lambda topic, user_id: test_topic
    #
    #     # Act
    #     response = client.post("/topics/", json=test_topic.dict())
    #
    #     # Assert
    #     self.assertEqual(201, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual(test_topic.model_dump(), response.json())


    #
    # def test_getTopicById_return_topic_when_topicExists(self):
    #
    #     mock_topic_service.get_by_id_with_replies = lambda topic_id: self.topic_with_replies
    #     mock_user_service.is_admin = lambda user_id: True
    #
    #     # Act
    #     response = client.get("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(200, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual(self.topic_with_replies.model_dump(), response.json())
    #
    # def test_getTopicById_return_notFound_when_topicDoesNotExist(self):
    #     # Arrange
    #     mock_topic_service.get_by_id_with_replies = lambda topic_id: None
    #
    #     # Act
    #     response = client.get("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(404, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Topic not found', response.json()['detail'])
    #
    # def test_createTopic_return_locked_when_categoryIsLocked(self):
    #     # Arrange
    #     category = fake_category()
    #     category.is_locked = True
    #     mock_category_service.get_by_id = lambda category_id: category
    #
    #     # Act
    #     response = client.post("/topics/", json=self.test_topics[0].dict())
    #
    #     # Assert
    #     self.assertEqual(400, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('This category is locked', response.json()['detail'])
    #
    # def test_createTopic_return_badRequest_when_userIsNotAdmin_topicToBeLocked(self):
    #     # Arrange
    #     mock_category_service.get_by_id = lambda category_id: fake_category()
    #     mock_user_service.is_admin = lambda user_id: False
    #     test_topic = self.test_topics[0]
    #     test_topic.is_locked = True
    #
    #     # Act
    #     response = client.post("/topics/", json=test_topic.dict())
    #
    #     # Assert
    #     self.assertEqual(403, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Only admins can create locked topics', response.json()['detail'])
    #
    # def test_createTopic_return_forbiddenAccess_when_userIsNotAdmin_categoryIsPrivate_userDoesNotHaveAccess(self):
    #     # Arrange
    #     category = fake_category()
    #     category.is_private = True
    #     mock_category_service.get_by_id = lambda category_id: category
    #     mock_user_service.is_admin = lambda user_id: False
    #     mock_category_service.validate_user_access = lambda user_id, category_id, access_type: False
    #
    #     # Act
    #     response = client.post("/topics/", json=self.test_topics[0].dict())
    #
    #     # Assert
    #     self.assertEqual(403, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('User does not have access to this category', response.json()['detail'])
    #
    # def test_createTopic_return_topic_when_userIsNotAdmin_categoryIsPrivate_userHasAccess(self):
    #     # Arrange
    #     category = fake_category()
    #     category.is_private = True
    #     mock_category_service.get_by_id = lambda category_id: category
    #     mock_user_service.is_admin = lambda user_id: False
    #     mock_category_service.validate_user_access = lambda user_id, category_id, access_type: True
    #     test_topic = self.test_topics[0]
    #     mock_topic_service.create = lambda topic, user_id: test_topic
    #
    #     # Act
    #     response = client.post("/topics/", json=test_topic.dict())
    #
    #     # Assert
    #     self.assertEqual(201, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual(test_topic.model_dump(), response.json())
    #
    # def test_lockTopic_return_OK_when_userIsAdmin_topicIsNotLocked(self):
    #     # Arrange
    #     mock_user_service.is_admin = lambda user_id: True
    #     test_topic = self.test_topics[0]
    #     mock_topic_service.get_by_id = lambda topic_id: test_topic
    #     mock_topic_service.lock_topic = lambda topic_id: None
    #
    #     # Act
    #     response = client.put("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(200, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Topic is successfully locked', response.json()['detail'])
    #
    # def test_lockTopic_return_notFound_when_topicDoesNotExist(self):
    #     # Arrange
    #     mock_user_service.is_admin = lambda user_id: True
    #     mock_topic_service.get_by_id = lambda topic_id: None
    #
    #     # Act
    #     response = client.put("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(404, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Topic not found', response.json()['detail'])
    #
    # def test_lockTopic_return_badRequest_when_topicIsLocked(self):
    #     # Arrange
    #     mock_user_service.is_admin = lambda user_id: True
    #     test_topic = self.test_topics[0]
    #     test_topic.is_locked = True
    #     mock_topic_service.get_by_id = lambda topic_id: test_topic
    #
    #     # Act
    #     response = client.put("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(400, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Topic is already locked', response.json()['detail'])
    #
    # def test_lockTopic_return_forbiddenAccess_when_userIsNotAdmin(self):
    #     # Arrange
    #     mock_user_service.is_admin = lambda user_id: False
    #
    #     # Act
    #     response = client.put("/topics/1")
    #
    #     # Assert
    #     self.assertEqual(403, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Only admins can lock topics', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_OK(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     mock_topic_service.validate_topic_author = lambda topic, user_id: True
    #     mock_reply_service.id_exists = lambda reply_id: True
    #     mock_reply_service.reply_belongs_to_topic = lambda reply_id, topic_id: True
    #     mock_topic_service.get_topic_best_reply = lambda topic_id: None
    #     mock_topic_service.update_best_reply = lambda topic_id, reply_id, prev_best_reply: None
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(200, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Best reply successfully chosen', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_badRequest_when_replyAlreadyBestReply(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     mock_topic_service.validate_topic_author = lambda topic, user_id: True
    #     mock_reply_service.id_exists = lambda reply_id: True
    #     mock_reply_service.reply_belongs_to_topic = lambda reply_id, topic_id: True
    #     mock_topic_service.get_topic_best_reply = lambda topic_id: 1
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(400, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Reply is already the best reply for this topic', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_notFound_when_replyDoesNotBelongToTopic(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     mock_topic_service.validate_topic_author = lambda topic, user_id: True
    #     mock_reply_service.id_exists = lambda reply_id: True
    #     mock_reply_service.reply_belongs_to_topic = lambda reply_id, topic_id: False
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(404, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Reply not found', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_notFound_when_replyDoesNotExist(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     mock_topic_service.validate_topic_author = lambda topic, user_id: True
    #     mock_reply_service.id_exists = lambda reply_id: False
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(404, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Reply not found', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_forbiddenAccess_when_userIsNotAuthor(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     mock_topic_service.validate_topic_author = lambda topic, user_id: False
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(403, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('User is not the author of this topic', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_locked_when_topicIsLocked(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: self.test_topics[0]
    #     self.test_topics[0].is_locked = True
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(400, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('This topic is locked', response.json()['detail'])
    #
    # def test_choseTopicBestReply_return_notFound_when_topicDoesNotExist(self):
    #     # Arrange
    #     mock_topic_service.get_by_id = lambda topic_id: None
    #
    #     # Act
    #     response = client.put("/topics/1/replies/1")
    #
    #     # Assert
    #     self.assertEqual(404, response.status_code)
    #     self.assertIsInstance(response.json(), dict)
    #     self.assertEqual('Topic not found', response.json()['detail'])