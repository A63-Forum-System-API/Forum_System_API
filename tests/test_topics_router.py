import unittest
from unittest.mock import Mock, patch
from routers import topics as topics_router

from fastapi.testclient import TestClient
from main import app
from schemas.reply import Reply
from schemas.topic import Topic, SingleTopic, CreateTopicRequest

client = TestClient(app)

def fake_category(id=1, is_locked=False, is_private=False):
    category = Mock()
    category.id = id
    category.is_locked = is_locked
    category.is_private = is_private

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

        self.test_create_topic = CreateTopicRequest(title="Test Title", content="Test Content",
                                                    is_locked=False, category_id=1)

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
            self.assertEqual("User ID: 1 not found", response.json()['detail'])
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
            self.assertEqual("Category ID: 1 not found", response.json()['detail'])
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

    def test_getById_return_topic_when_userIsAdmin(self):
        # Arrange
        with (patch('services.topic_service.get_by_id_with_replies',
                   return_value=self.topic_with_replies) as mock_get_by_id_with_replies,
              patch('services.user_service.is_admin',
                    return_value=True) as mock_is_admin):
            # Act
            response = client.get("/topics/1")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.topic_with_replies.model_dump(), response.json())
            mock_get_by_id_with_replies.assert_called_once_with(1)
            mock_is_admin.assert_called_once_with(1)

    def test_getById_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch('services.topic_service.get_by_id_with_replies',
                   return_value=self.topic_with_replies) as mock_get_by_id_with_replies,
              patch('services.category_service.validate_user_access',
                    return_value=False) as mock_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin):
            # Act
            response = client.get("/topics/1")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('User does not have access to this category', response.json()['detail'])
            mock_get_by_id_with_replies.assert_called_once_with(1)
            mock_validate_user_access.assert_called_once_with(1, 1)
            mock_is_admin.assert_called_once_with(1)


    def test_getById_return_topic_when_userNotAdmin_userHasAccess(self):
        # Arrange
        with (patch('services.topic_service.get_by_id_with_replies',
                   return_value=self.topic_with_replies) as mock_get_by_id_with_replies,
              patch('services.category_service.validate_user_access',
                    return_value=True) as mock_validate_user_access,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin):
            # Act
            response = client.get("/topics/1")

            # Assert
            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.topic_with_replies.model_dump(), response.json())
            mock_get_by_id_with_replies.assert_called_once_with(1)
            mock_validate_user_access.assert_called_once_with(1, 1)
            mock_is_admin.assert_called_once_with(1)

    def test_getById_return_notFound_when_topicDoesNotExist(self):
        # Arrange
        with patch('services.topic_service.get_by_id_with_replies',
                   return_value=None) as mock_get_by_id_with_replies:

            # Act
            response = client.get("/topics/1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Topic ID: 1 not found", response.json()['detail'])
            mock_get_by_id_with_replies.assert_called_once_with(1)

    def test_createTopic_return_topic(self):
        # Arrange
        with (patch('services.category_service.get_by_id',
                    return_value=fake_category()) as mock_get_by_id,
              patch('services.user_service.is_admin',
                    return_value=True) as mock_is_admin,
             patch('services.topic_service.create',
                   return_value=self.test_topics[0]) as mock_create):
            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(201, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.test_topics[0].model_dump(), response.json())
            mock_get_by_id.assert_called_once_with(1)
            mock_is_admin.assert_called_once_with(1)
            mock_create.assert_called_once()

    def test_createTopic_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch('services.category_service.get_by_id',
                   return_value=fake_category(is_private=True)) as mock_get_by_id,
             patch('services.category_service.validate_user_access',
                   return_value=False) as mock_validate_user_access,
             patch('services.user_service.is_admin',
                   return_value=False) as mock_is_admin):
            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual('User does not have access to this category', response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_user_access.assert_called_once_with(1, 1, 'write')
            mock_is_admin.assert_called_once_with(1)

    def test_createTopic_return_forbiddenAccess_when_userNotAdmin_userHasAccess(self):
        # Arrange
        with (patch('services.category_service.get_by_id',
                   return_value=fake_category(is_private=True)) as mock_get_by_id,
             patch('services.category_service.validate_user_access',
                   return_value=True) as mock_validate_user_access,
             patch('services.user_service.is_admin',
                   return_value=False) as mock_is_admin,
              patch('services.topic_service.create',
                    return_value=self.test_topics[0])):

            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(201, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.test_topics[0].model_dump(), response.json())
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_user_access.assert_called_once_with(1, 1, 'write')
            mock_is_admin.assert_called_once_with(1)

    def test_createTopic_return_forbiddenAccess_when_userNotAdmin_topicIsLocked(self):
        # Arrange
        with (patch('services.user_service.is_admin',
                   return_value=False) as mock_is_admin,
              patch('services.category_service.get_by_id',
                   return_value=fake_category()) as mock_get_by_id):
            self.test_create_topic.is_locked = True

            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Only admin can create locked topics", response.json()['detail'])
            mock_is_admin.assert_called_once_with(1)
            mock_get_by_id.assert_called_once_with(1)

    def test_createTopic_return_locked_when_categoryIsLocked(self):
        # Arrange
        with (patch('services.category_service.get_by_id',
                   return_value=fake_category(is_locked=True)) as mock_get_by_id,
              patch('services.user_service.is_admin',
                    return_value=True) as mock_is_admin):
            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(400, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Category ID: 1 is locked", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_is_admin.assert_called_once_with(1)

    def test_createTopic_return_notFound_when_categoryDoesNotExist(self):
        # Arrange
        with patch('services.category_service.get_by_id',
                   return_value=None) as mock_get_by_id:
            # Act
            response = client.post("/topics/", json=self.test_create_topic.model_dump())

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Category ID: 1 not found", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)

    def test_lockTopic_return_OK_when_userIsAdmin(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                     return_value=self.test_topics[0]) as mock_get_by_id,
                patch('services.user_service.is_admin',
                        return_value=True) as mock_is_admin,
                patch('services.topic_service.change_topic_lock_status',
                        return_value=None) as mock_change_topic_lock_status):
            # Act
            response = client.put("/topics/1/locked-status/lock")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Topic ID: 1 successfully locked", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_is_admin.assert_called_once_with(1)
            mock_change_topic_lock_status.assert_called_once_with(1, 1)


    def test_lockTopic_return_OK_when_topicAlreadyLocked(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.user_service.is_admin',
                    return_value=True) as mock_is_admin):
            self.test_topics[0].is_locked = True
            # Act
            response = client.put("/topics/1/locked-status/lock")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Topic ID: 1 is already locked", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_is_admin.assert_called_once_with(1)

    def test_lockTopic_return_notFound_when_topicDoesNotExist(self):
        # Arrange
        with (patch('services.user_service.is_admin',
                   return_value=True) as mock_is_admin,
              patch('services.topic_service.get_by_id',
                   return_value=None) as mock_get_by_id):
            # Act
            response = client.put("/topics/1/locked-status/lock")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Topic ID: 1 not found", response.json()['detail'])
            mock_is_admin.assert_called_once_with(1)
            mock_get_by_id.assert_called_once_with(1)

    def test_lockTopic_return_forbiddenAccess_when_userNotAdmin(self):
        # Arrange
        with (patch('services.user_service.is_admin',
                    return_value=False) as mock_is_admin):
            # Act
            response = client.put("/topics/1/locked-status/lock")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Only admin can change locked status for topics", response.json()['detail'])
            mock_is_admin.assert_called_once_with(1)

    def test_choseTopicBestReply_return_OK_when_userIsAdmin(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.topic_service.validate_topic_author',
                    return_value=True) as mock_validate_topic_author,
              patch('services.reply_service.id_exists',
                    return_value=True) as mock_id_exists,
              patch('services.reply_service.reply_belongs_to_topic',
                    return_value=True) as mock_reply_belongs_to_topic,
              patch('services.topic_service.get_topic_best_reply',
                    return_value=None) as mock_get_topic_best_reply,
              patch('services.topic_service.update_best_reply',
                    return_value=None) as mock_update_best_reply):
            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(200, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f'Reply ID: 1 is now the best reply for topic ID: {self.test_topics[0].id}', response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_topic_author.assert_called_once_with(1, 1)
            mock_id_exists.assert_called_once_with(1)
            mock_reply_belongs_to_topic.assert_called_once_with(1, 1)
            mock_get_topic_best_reply.assert_called_once_with(1)
            mock_update_best_reply.assert_called_once_with(1, 1, None)

    def test_choseTopicBestReply_return_badRequest_when_previousBestReplyIsNotTheSame(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.topic_service.validate_topic_author',
                    return_value=True) as mock_validate_topic_author,
              patch('services.reply_service.id_exists',
                    return_value=True) as mock_id_exists,
              patch('services.reply_service.reply_belongs_to_topic',
                    return_value=True) as mock_reply_belongs_to_topic,
              patch('services.topic_service.get_topic_best_reply',
                    return_value=1) as mock_get_topic_best_reply):

            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(400, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Reply ID: 1 is already the best reply for topic ID: {self.test_topics[0].id}",
                             response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_topic_author.assert_called_once_with(1, 1)
            mock_id_exists.assert_called_once_with(1)
            mock_reply_belongs_to_topic.assert_called_once_with(1, 1)
            mock_get_topic_best_reply.assert_called_once_with(1)

    def test_choseTopicBestReply_return_notFound_when_replyDoesNotBelongToTopic(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.topic_service.validate_topic_author',
                    return_value=True) as mock_validate_topic_author,
              patch('services.reply_service.id_exists',
                    return_value=True) as mock_id_exists,
              patch('services.reply_service.reply_belongs_to_topic',
                    return_value=False) as mock_reply_belongs_to_topic):

            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Reply ID: 1 not found", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_topic_author.assert_called_once_with(1, 1)
            mock_id_exists.assert_called_once_with(1)
            mock_reply_belongs_to_topic.assert_called_once_with(1, 1)

    def test_choseTopicBestReply_return_notFound_when_replyDoesNotExist(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.topic_service.validate_topic_author',
                    return_value=True) as mock_validate_topic_author,
              patch('services.reply_service.id_exists',
                    return_value=False) as mock_id_exists):

            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Reply ID: 1 not found", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_topic_author.assert_called_once_with(1, 1)
            mock_id_exists.assert_called_once_with(1)

    def test_choseTopicBestReply_return_forbiddenAccess_when_userNotAuthor(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id,
              patch('services.topic_service.validate_topic_author',
                    return_value=False) as mock_validate_topic_author):

            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Only the author can choose best reply for the topic", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)
            mock_validate_topic_author.assert_called_once_with(1, 1)


    def test_choseTopicBestReply_return_badRequest_when_topicIsLocked(self):
        # Arrange
        with (patch('services.topic_service.get_by_id',
                   return_value=self.test_topics[0]) as mock_get_by_id):
            self.test_topics[0].is_locked = True
            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(400, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Topic ID: {self.test_topics[0].id} is locked", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)


    def test_choseTopicBestReply_return_notFound_when_topicDoesNotExist(self):
        # Arrange
        with patch('services.topic_service.get_by_id',
                   return_value=None) as mock_get_by_id:
            # Act
            response = client.put("/topics/1/replies/1")

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("Topic ID: 1 not found", response.json()['detail'])
            mock_get_by_id.assert_called_once_with(1)

