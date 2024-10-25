import unittest
from unittest.mock import Mock, patch
from routers import topics as topics_router

from fastapi.testclient import TestClient
from main import app
from schemas.reply import Reply, CreateReplyRequest
from services.category_service import is_private

client = TestClient(app)

def fake_category(id=1, is_private=False):
    category = Mock()
    category.id = id
    category.is_private = is_private

    return category

def fake_topic(id=1, is_locked=False):
    topic = Mock()
    topic.id = id
    topic.is_locked = is_locked

    return topic

def fake_reply(id=1):
    reply = Mock()

    return reply

class VotesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        self.test_reply = Reply(id=1, content="Test Content", topic_id=1, created_at=None,
                                is_best_reply=False, author_id=1, vote_count=0)

        self.create_reply = CreateReplyRequest(content="Test Content", topic_id=1)

        app.dependency_overrides = {
            topics_router.get_current_user: lambda: 1
        }

    def tearDown(self) -> None:
        app.dependency_overrides = {}

    def test_vote_return_OK_when_updateVote_differentVote_voteExists(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category()) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=True) as mock_user_service,
              patch("services.vote_service.get_vote",
                    return_value=0) as mock_get_vote,
              patch("services.vote_service.update_vote",
                    return_value=None) as mock_update_vote):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(200, response.status_code)
            self.assertEqual("Vote is successfully changed to upvote", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_get_vote.assert_called_once()
            mock_update_vote.assert_called_once()

    def test_vote_return_badRequest_when_sameVote_voteExists(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category()) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=True) as mock_user_service,
              patch("services.vote_service.get_vote",
                    return_value=1) as mock_get_vote):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(400, response.status_code)
            self.assertEqual("Current user has already voted for this reply", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_get_vote.assert_called_once()

    def test_vote_return_created_when_voteDoesNotExist(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category()) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=True) as mock_user_service,
              patch("services.vote_service.get_vote",
                    return_value=None) as mock_get_vote,
              patch("services.vote_service.create_vote",
                    return_value=None) as mock_create_vote):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(201, response.status_code)
            self.assertEqual("User voted successfully", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_get_vote.assert_called_once()
            mock_create_vote.assert_called_once()

    def test_vote_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=False) as mock_user_service,
              patch("services.category_service.validate_user_access",
                    return_value=False) as mock_validate_user_access):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(403, response.status_code)
            self.assertEqual("User does not have access to this category", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()

    def test_vote_return_OK_when_userNotAdmin_userHasAccess_voteDoesNotExist(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=False) as mock_user_service,
              patch("services.category_service.validate_user_access",
                    return_value=True) as mock_validate_user_access,
              patch("services.vote_service.get_vote",
                    return_value=None) as mock_get_vote,
              patch("services.vote_service.create_vote",
                    return_value=None) as mock_create_vote):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(201, response.status_code)
            self.assertEqual("User voted successfully", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()
            mock_get_vote.assert_called_once()
            mock_create_vote.assert_called_once()

    def test_vote_return_locked_when_topicIsLocked(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic(is_locked=True)) as mock_topic_service):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(400, response.status_code)
            self.assertEqual("This topic is locked", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()

    def test_vote_return_notFound_when_replyDoesNotExist(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=None) as mock_reply_service):

            response = client.put("/votes/1?vote_type=upvote")

            self.assertEqual(404, response.status_code)
            self.assertEqual("Reply not found", response.json()["detail"])
            mock_reply_service.assert_called_once()

    def test_deleteVote_return_OK_when_voteExists(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category()) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=True) as mock_user_service,
              patch("services.vote_service.get_vote",
                    return_value=1) as mock_get_vote,
              patch("services.vote_service.delete_vote",
                    return_value=None) as mock_delete_vote):

            response = client.delete("/votes/1")

            self.assertEqual(200, response.status_code)
            self.assertEqual("Vote deleted successfully", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_get_vote.assert_called_once()
            mock_delete_vote.assert_called_once()

    def test_deleteVote_return_badRequest_when_voteDoesNotExist(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category()) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=True) as mock_user_service,
              patch("services.vote_service.get_vote",
                    return_value=None) as mock_get_vote):

            response = client.delete("/votes/1")

            self.assertEqual(400, response.status_code)
            self.assertEqual("User has not voted for this reply", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_get_vote.assert_called_once()

    def test_deleteVote_return_forbiddenAccess_when_userNotAdmin_userHasNoAccess(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=False) as mock_user_service,
              patch("services.category_service.validate_user_access",
                    return_value=False) as mock_validate_user_access):

            response = client.delete("/votes/1")

            self.assertEqual(403, response.status_code)
            self.assertEqual("User does not have access to this category", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()

    def test_deleteVote_return_OK_when_userNotAdmin_userHasAccess(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic()) as mock_topic_service,
              patch("services.category_service.get_by_id",
                    return_value=fake_category(is_private=True)) as mock_category_service,
              patch("services.user_service.is_admin",
                    return_value=False) as mock_user_service,
              patch("services.category_service.validate_user_access",
                    return_value=True) as mock_validate_user_access,
              patch("services.vote_service.get_vote",
                    return_value=1) as mock_get_vote,
              patch("services.vote_service.delete_vote",
                    return_value=None) as mock_delete_vote):

            response = client.delete("/votes/1")

            self.assertEqual(200, response.status_code)
            self.assertEqual("Vote deleted successfully", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()
            mock_category_service.assert_called_once()
            mock_user_service.assert_called_once()
            mock_validate_user_access.assert_called_once()
            mock_get_vote.assert_called_once()
            mock_delete_vote.assert_called_once()

    def test_deleteVote_return_locked_when_topicIsLocked(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=fake_reply()) as mock_reply_service,
              patch("services.topic_service.get_by_id",
                    return_value=fake_topic(is_locked=True)) as mock_topic_service):

            response = client.delete("/votes/1")

            self.assertEqual(400, response.status_code)
            self.assertEqual("This topic is locked", response.json()["detail"])
            mock_reply_service.assert_called_once()
            mock_topic_service.assert_called_once()

    def test_deleteVote_return_notFound_when_replyDoesNotExist(self):
        with (patch("services.reply_service.get_by_id",
                    return_value=None) as mock_reply_service):

            response = client.delete("/votes/1")

            self.assertEqual(404, response.status_code)
            self.assertEqual("Reply not found", response.json()["detail"])
            mock_reply_service.assert_called_once()