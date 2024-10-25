import unittest
from unittest.mock import Mock, patch
from routers import topics as topics_router

from fastapi.testclient import TestClient
from main import app
from schemas.reply import Reply, CreateReplyRequest

client = TestClient(app)

def fake_category(id=1, is_locked=False, is_private=False):
    category = Mock()
    category.id = id
    category.is_locked = is_locked
    category.is_private = is_private

    return category

def fake_topic(id=1, is_locked=False):
    topic = Mock()
    topic.id = id
    topic.is_locked = is_locked

    return topic

class RepliesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        self.test_reply = Reply(id=1, content="Test Content", topic_id=1, created_at=None,
                                is_best_reply=False, author_id=1, vote_count=0)

        self.create_reply = CreateReplyRequest(content="Test Content", topic_id=1)

        app.dependency_overrides = {
            topics_router.get_current_user: lambda: 1
        }

    def tearDown(self) -> None:
        app.dependency_overrides = {}

    def test_createReply_return_201(self):
        # Arrange
        with (patch("services.topic_service.get_by_id",
                   return_value=fake_topic()) as mock_topic_service,
              patch('services.category_service.get_by_id',
                    return_value=fake_category()) as mock_category_service,
              patch('services.user_service.is_admin',
                    return_value=True) as mock_user_service,
              patch('services.reply_service.create',
                    return_value=self.test_reply) as mock_reply_service):

            # Act
            response = client.post("/replies", json=self.create_reply.model_dump())

            # Assert
            self.assertEqual(201, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.test_reply.model_dump(), response.json())
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_reply_service.assert_called_once()

    def test_createReply_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        # Arrange
        with (patch("services.topic_service.get_by_id",
                   return_value=fake_topic()) as mock_topic_service,
              patch('services.category_service.get_by_id',
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_user_service,
              patch('services.category_service.validate_user_access',
                    return_value=False) as mock_validate_user_access):

            # Act
            response = client.post("/replies", json=self.create_reply.model_dump())

            # Assert
            self.assertEqual(403, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual("User does not have access to this category", response.json()["detail"])
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()

    def test_createReply_return_201_when_userNotAdmin_userHasAccess(self):
        # Arrange
        with (patch("services.topic_service.get_by_id",
                   return_value=fake_topic()) as mock_topic_service,
              patch('services.category_service.get_by_id',
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch('services.user_service.is_admin',
                    return_value=False) as mock_user_service,
              patch('services.category_service.validate_user_access',
                    return_value=True) as mock_validate_user_access,
              patch('services.reply_service.create',
                    return_value=self.test_reply) as mock_reply_service):

            # Act
            response = client.post("/replies", json=self.create_reply.model_dump())

            # Assert
            self.assertEqual(201, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(self.test_reply.model_dump(), response.json())
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()
            mock_reply_service.assert_called_once()

    def test_createReply_return_badRequest_when_topicIsLocked(self):
        # Arrange
        with (patch("services.topic_service.get_by_id",
                   return_value=fake_topic(is_locked=True)) as mock_topic_service):

            # Act
            response = client.post("/replies", json=self.create_reply.model_dump())

            # Assert
            self.assertEqual(400, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Topic ID: {self.test_reply.topic_id} is locked", response.json()["detail"])
            mock_topic_service.assert_called_once()

    def test_createReply_return_notFound_when_topicDoesNotExist(self):
        # Arrange
        with (patch("services.topic_service.get_by_id",
                   return_value=None) as mock_topic_service):

            # Act
            response = client.post("/replies", json=self.create_reply.model_dump())

            # Assert
            self.assertEqual(404, response.status_code)
            self.assertIsInstance(response.json(), dict)
            self.assertEqual(f"Topic ID: {self.test_reply.topic_id} not found", response.json()["detail"])
            mock_topic_service.assert_called_once()


