import unittest
from datetime import timedelta
from unittest.mock import patch

import test_data as td
from schemas.reply import Reply
from schemas.topic import ViewAllTopics, SingleTopic, Topic, CreateTopicRequest
from services import topic_service


class TopicService_Should(unittest.TestCase):

    def test_getAllTopics_returns_listOfTopics_when_dataIsPresent(self):
        # Arrange
        test_topic_1 = (1, td.TEST_TITLE, False, td.TEST_CREATED_AT, 1, 1, 5)
        test_topic_2 = (2, td.TEST_TITLE, True, td.TEST_CREATED_AT, 2, 1, 3)

        with (patch('services.topic_service.read_query',
                    return_value=[test_topic_1, test_topic_2]) as mock_read_query,
              patch('services.topic_service._build_conditions_and_params',
                    return_value=([], [])) as mock_build_conditions_and_params,
              patch('services.topic_service._build_final_query',
                    return_value=('', [])) as mock_build_final_query):



            expected = [
                ViewAllTopics.from_query_result(*test_topic_1),
                ViewAllTopics.from_query_result(*test_topic_2)
            ]

            # Act
            result = topic_service.get_all_topics(
                search=None, category_id=None,
                author_id=None, is_locked=None,
                user_id=1, limit=10, offset=0)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()
            mock_build_conditions_and_params.assert_called_once()
            mock_build_final_query.assert_called_once()

    def test_getAllTopics_returns_emptyList_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.get_all_topics(
                search=None, category_id=None,
                author_id=None, is_locked=None,
                user_id=1, limit=10, offset=0)

            # Assert
            self.assertEqual([], result)
            mock_read_query.assert_called_once()

    def test_buildConditionsAndParams_returns_correctTuple_when_searchIsPresent(self):
        with patch('services.topic_service.user_service') as mock_user_service:
            # Arrange
            search = 'search'
            category_id = None
            author_id = None
            is_locked = None
            user_id = 1
            mock_user_service.is_admin.return_value = True

            expected = (['t.title like ?'], ['%search%'])

            # Act
            result = topic_service._build_conditions_and_params(
                search, category_id, author_id, is_locked, user_id)

            # Assert
            self.assertEqual(expected, result)
            mock_user_service.is_admin.assert_called_once_with(user_id)

    def test_buildConditionsAndParams_returns_correctTuple_when_categoryIdIsPresent(self):
        with patch('services.topic_service.user_service') as mock_user_service:
            # Arrange
            search = None
            category_id = 1
            author_id = None
            is_locked = None
            user_id = 1
            mock_user_service.is_admin.return_value = True

            expected = (['t.category_id = ?'], [1])

            # Act
            result = topic_service._build_conditions_and_params(
                search, category_id, author_id, is_locked, user_id)

            # Assert
            self.assertEqual(expected, result)
            mock_user_service.is_admin.assert_called_once_with(user_id)

    def test_buildConditionsAndParams_returns_correctTuple_when_authorIdIsPresent(self):
        with patch('services.topic_service.user_service') as mock_user_service:
            # Arrange
            search = None
            category_id = None
            author_id = 1
            is_locked = None
            user_id = 1
            mock_user_service.is_admin.return_value = True

            expected = (['t.author_id = ?'], [1])

            # Act
            result = topic_service._build_conditions_and_params(
                search, category_id, author_id, is_locked, user_id)

            # Assert
            self.assertEqual(expected, result)
            mock_user_service.is_admin.assert_called_once_with(user_id)

    def test_buildConditionsAndParams_returns_correctTuple_when_isLockedIsPresent(self):
        with patch('services.topic_service.user_service') as mock_user_service:
            # Arrange
            search = None
            category_id = None
            author_id = None
            is_locked = True
            user_id = 1
            mock_user_service.is_admin.return_value = True

            expected = (['t.is_locked = ?'], [True])

            # Act
            result = topic_service._build_conditions_and_params(
                search, category_id, author_id, is_locked, user_id)

            # Assert
            self.assertEqual(expected, result)
            mock_user_service.is_admin.assert_called_once_with(user_id)

    def test_buildConditionsAndParams_returns_correctTuple_when_userNotAdmin(self):
        with patch('services.topic_service.user_service') as mock_user_service:
            # Arrange
            search = None
            category_id = None
            author_id = None
            is_locked = None
            user_id = 1
            mock_user_service.is_admin.return_value = False

            expected = (['(c.is_private = 0 OR (c.is_private = 1 AND EXISTS (SELECT 1 FROM category_accesses ca WHERE ca.category_id = t.category_id AND ca.user_id = ?)))'], [1])

            # Act
            result = topic_service._build_conditions_and_params(
                search, category_id, author_id, is_locked, user_id)

            # Assert
            self.assertEqual(expected, result)
            mock_user_service.is_admin.assert_called_once_with(user_id)

    def test_buildFinalQuery_returns_correctTuple(self):
        # Arrange
        base_query = 'SELECT * FROM topics t'
        where_conditions = ['t.title like ?']
        params = ['%search%']
        limit = 10
        offset = 0

        expected = ('SELECT * FROM topics t WHERE t.title like ? GROUP BY t.id LIMIT ? OFFSET ?', ['%search%', 10, 0])

        # Act
        result = topic_service._build_final_query(
            base_query, where_conditions, params, limit, offset)

        # Assert
        self.assertEqual(expected, result)

    def test_sortTopics_returns_sortedList_when_reverseIsFalse(self):
        # Arrange
        test_topic_1 = ViewAllTopics.from_query_result(
            1, td.TEST_TITLE, False, td.TEST_CREATED_AT + timedelta(days=1), 1, 1, 5)
        test_topic_2 = ViewAllTopics.from_query_result(
            2, td.TEST_TITLE, True, td.TEST_CREATED_AT, 2, 1, 3)

        topics = [test_topic_1, test_topic_2]

        expected = [test_topic_2, test_topic_1]

        # Act
        result = topic_service.sort_topics(topics, reverse=False)

        # Assert
        self.assertEqual(expected, result)

    def test_sortTopics_returns_sortedList_when_reverseIsTrue(self):
        # Arrange
        test_topic_1 = ViewAllTopics.from_query_result(
            1, td.TEST_TITLE, False, td.TEST_CREATED_AT + timedelta(days=1), 1, 1, 5)
        test_topic_2 = ViewAllTopics.from_query_result(
            2, td.TEST_TITLE, True, td.TEST_CREATED_AT, 2, 1, 3)

        topics = [test_topic_1, test_topic_2]

        expected = [test_topic_1, test_topic_2]

        # Act
        result = topic_service.sort_topics(topics, reverse=True)

        # Assert
        self.assertEqual(expected, result)

    def test_getByIdWithReplies_returns_topic_when_dataIsPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            test_data = [
                (1, td.TEST_TITLE, td.TEST_CONTENT, False, 1, td.TEST_CREATED_AT, None, 1,
                 1, 'Reply content 1', 1, td.TEST_CREATED_AT, False, 1, 0),
                (1, td.TEST_TITLE, td.TEST_CONTENT, False, 1, td.TEST_CREATED_AT, None, 1,
                 2, 'Reply content 2', 1, td.TEST_CREATED_AT, False, 1, 0)]

            mock_read_query.return_value = test_data

            test_topic = Topic.from_query_result(
                1, td.TEST_TITLE, td.TEST_CONTENT, False,
                1, td.TEST_CREATED_AT, None, 1)

            test_replies = [
                Reply.from_query_result(
                    1, 'Reply content 1', 1,
                    td.TEST_CREATED_AT, False, 1, 0),
                Reply.from_query_result(
                    2, 'Reply content 2', 1,
                    td.TEST_CREATED_AT, False, 1, 0)]

            expected = SingleTopic(topic=test_topic, all_replies=test_replies)

            # Act
            result = topic_service.get_by_id_with_replies(1)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()

    def test_getByIdWithReplies_returns_None_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.get_by_id_with_replies(1)

            # Assert
            self.assertIsNone(result)
            mock_read_query.assert_called_once()

    def test_createReplyFromRow_returns_reply_when_dataIsPresent(self):
        # Arrange
        test_data = [1, td.TEST_TITLE, td.TEST_CONTENT, False, 1, td.TEST_CREATED_AT, None, 1,
                 1, 'Reply content', 1, td.TEST_CREATED_AT, False, 1, 0]
        expected = Reply.from_query_result(1, 'Reply content', 1, td.TEST_CREATED_AT, False, 1, 0)

        # Act
        result = topic_service._create_reply_from_row(test_data)

        # Assert
        self.assertEqual(expected, result)

    def test_getById_returns_topic_when_dataIsPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            test_data = (1, td.TEST_TITLE, td.TEST_CONTENT, False, 1, td.TEST_CREATED_AT, None, 1)

            mock_read_query.return_value = [test_data]

            expected = Topic.from_query_result(*test_data)

            # Act
            result = topic_service.get_by_id(1)

            # Assert
            self.assertEqual(expected, result)
            mock_read_query.assert_called_once()

    def test_getById_returns_None_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.get_by_id(1)

            # Assert
            self.assertIsNone(result)
            mock_read_query.assert_called_once()

    def test_create_returns_topic_when_dataIsPresent(self):
        with patch('services.topic_service.insert_query') as mock_insert_query:
            with patch('services.topic_service.get_by_id') as mock_get_by_id:
                # Arrange
                mock_insert_query.return_value = 1
                test_topic = Topic.from_query_result(1, td.TEST_TITLE, td.TEST_CONTENT, False,
                                                     1, td.TEST_CREATED_AT, None, 1)
                mock_get_by_id.return_value = test_topic

                create_topic = CreateTopicRequest(title=td.TEST_TITLE, content=td.TEST_CONTENT, category_id=1)
                expected = test_topic

                # Act
                result = topic_service.create(create_topic, 1)

                # Assert
                self.assertEqual(expected, result)
                mock_insert_query.assert_called_once()
                mock_get_by_id.assert_called_once_with(1)

    def test_idExists_returns_true_when_dataIsPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = topic_service.id_exists(1)

            # Assert
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_idExists_returns_false_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.id_exists(1)

            # Assert
            self.assertFalse(result)
            mock_read_query.assert_called_once()

    def test_lockTopic_calls_UpdateQueryCorrectly(self):
        with patch('services.topic_service.update_query') as mock_update_query:
            # Arrange
            test_topic_id = 1
            mock_update_query.return_value = None

            # Act
            topic_service.change_topic_lock_status(test_topic_id, 1)

            # Assert
            mock_update_query.assert_called_once()

    def test_validateTopicAuthor_returns_true_when_dataIsPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = topic_service.validate_topic_author(1, 1)

            # Assert
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_validateTopicAuthor_returns_false_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.validate_topic_author(1, 1)

            # Assert
            self.assertFalse(result)
            mock_read_query.assert_called_once()

    def test_updateBestReply_calls_MarkReplyAsNotBest_when_previousBestReplyExists(self):
        with patch('services.topic_service._mark_reply_as_not_best') as mock_mark_reply_as_not_best:
            with patch('services.topic_service._update_topic_best_reply') as mock_update_topic_best_reply:
                with patch('services.topic_service._mark_reply_as_best') as mock_mark_reply_as_best:
                    # Arrange
                    test_topic_id = 1
                    test_reply_id = 2
                    test_prev_best_reply = 1

                    mock_mark_reply_as_not_best.return_value = None
                    mock_update_topic_best_reply.return_value = None
                    mock_mark_reply_as_best.return_value = None

                    # Act
                    topic_service.update_best_reply(test_topic_id, test_reply_id, test_prev_best_reply)

                    # Assert
                    mock_mark_reply_as_not_best.assert_called_once_with(1)
                    mock_update_topic_best_reply.assert_called_once_with(1, 2)
                    mock_mark_reply_as_best.assert_called_once_with(2)

    def test_updateBestReply_doesNotCall_MarkReplyAsNotBest_when_noPreviousBestReply(self):
        with patch('services.topic_service._mark_reply_as_not_best') as mock_mark_reply_as_not_best:
            with patch('services.topic_service._update_topic_best_reply') as mock_update_topic_best_reply:
                with patch('services.topic_service._mark_reply_as_best') as mock_mark_reply_as_best:
                    # Arrange
                    test_topic_id = 1
                    test_reply_id = 2
                    test_prev_best_reply = None

                    mock_mark_reply_as_not_best.return_value = None
                    mock_update_topic_best_reply.return_value = None
                    mock_mark_reply_as_best.return_value = None

                    # Act
                    topic_service.update_best_reply(test_topic_id, test_reply_id, test_prev_best_reply)

                    # Assert
                    mock_mark_reply_as_not_best.assert_not_called()
                    mock_update_topic_best_reply.assert_called_once_with(1, 2)
                    mock_mark_reply_as_best.assert_called_once_with(2)

    def test_getTopicBestReply_returns_replyId_when_dataIsPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = [(1,)]

            # Act
            result = topic_service.get_topic_best_reply(1)

            # Assert
            self.assertEqual(1, result)
            mock_read_query.assert_called_once()

    def test_getTopicBestReply_returns_None_when_dataIsNotPresent(self):
        with patch('services.topic_service.read_query') as mock_read_query:
            # Arrange
            mock_read_query.return_value = []

            # Act
            result = topic_service.get_topic_best_reply(1)

            # Assert
            self.assertIsNone(result)
            mock_read_query.assert_called_once()

    def test_markReplyAsNotBest_calls_UpdateQueryCorrectly(self):
        with patch('services.topic_service.update_query') as mock_update_query:
            # Arrange
            test_reply_id = 1
            mock_update_query.return_value = None

            # Act
            topic_service._mark_reply_as_not_best(test_reply_id)

            # Assert
            mock_update_query.assert_called_once()

    def test_updateTopicBestReply_calls_UpdateQueryCorrectly(self):
        with patch('services.topic_service.update_query') as mock_update_query:
            # Arrange
            test_topic_id = 1
            test_reply_id = 2
            mock_update_query.return_value = None

            # Act
            topic_service._update_topic_best_reply(test_topic_id, test_reply_id)

            # Assert
            mock_update_query.assert_called_once()

    def test_markReplyAsBest_calls_UpdateQueryCorrectly(self):
        with patch('services.topic_service.update_query') as mock_update_query:
            # Arrange
            test_reply_id = 1
            mock_update_query.return_value = None

            # Act
            topic_service._mark_reply_as_best(test_reply_id)

            # Assert
            mock_update_query.assert_called_once()