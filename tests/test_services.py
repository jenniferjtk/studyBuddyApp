import unittest
from unittest.mock import MagicMock
from studybuddy.application.services import StudyBuddyService, MatchSuggestion

# to run tests run python -m unittest tests/test_services.py in terminal

class TestStudyBuddyService(unittest.TestCase):
    def setUp(self):
        # Mock the database
        self.mock_db = MagicMock()
        self.service = StudyBuddyService(self.mock_db)

    def test_suggest_matches_returns_matches(self):
        # Setup mock return value for query_all
        self.mock_db.query_all.return_value = [
            {
                "partner_id": 2,
                "day_of_week": 1,
                "overlap_start_min": 600,
                "overlap_end_min": 660,
                "minutes": 60
            }
        ]
        matches = self.service.suggest_matches(1, "CPSC-3720", 30)
        self.assertEqual(len(matches), 1)
        self.assertIsInstance(matches[0], MatchSuggestion)
        self.assertEqual(matches[0].partner_id, 2)
        self.assertEqual(matches[0].minutes, 60)

    def test_suggest_matches_no_matches(self):
        self.mock_db.query_all.return_value = []
        matches = self.service.suggest_matches(1, "CPSC-3720", 30)
        self.assertEqual(matches, [])

    # Add more tests for other service methods as needed
    #def test_list_users(self):
        # Mock return value for query_all
        #self.mock_db.query_all.return_value = [
            #{"id": 1, "name": "Alice"},
            #{"id": 2, "name": "Bob"}
        #]
        #users = self.service.list_users()
        #self.assertEqual(len(users), 2)
        #self.assertEqual(users[0].id, 1)
        #self.assertEqual(users[0].name, "Alice")

    def test_list_courses(self):
        self.mock_db.query_all.return_value = [
            {"code": "CPSC-1010", "title": "Intro to CS"},
            {"code": "MATH-1010", "title": "Calculus"}
        ]
        courses = self.service.list_all_courses()
        self.assertEqual(len(courses), 2)
        self.assertEqual(courses[1]["code"], "MATH-1010")

    def test_list_classmates(self):
        self.mock_db.query_all.return_value = [
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        classmates = self.service.find_classmates(1, "CPSC-1010")
        self.assertEqual(len(classmates), 2)
        self.assertEqual(classmates[1].name, "Charlie")

    def test_request_session(self):
        # Mock execute and query_one for session creation
        self.mock_db.execute.return_value = None
        self.mock_db.query_one.return_value = {"id": 42}
        session_id = self.service.request_session(1, 2, "CPSC-1010", 0, 600, 660)
        self.assertEqual(session_id, 42)
        self.mock_db.execute.assert_called()

    def test_accept_session(self):
        self.mock_db.execute.return_value = None
        self.service.respond_session(1, 2, accept=True)
        self.mock_db.execute.assert_called()

    def test_decline_session(self):
        self.mock_db.execute.return_value = None
        self.service.respond_session(1, 2, accept=False)
        self.mock_db.execute.assert_called()

if __name__ == "__main__":
    unittest.main()
