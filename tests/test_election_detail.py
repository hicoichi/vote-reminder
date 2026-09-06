import os
import unittest
from datetime import date, timedelta

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, election_detail, elections  # noqa: E402


class ElectionDetailTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()

    def tearDown(self):
        self.conn.close()

    def test_days_until_vote_is_computed(self):
        vote_date = date.today() + timedelta(days=10)
        election = elections.add_election(
            self.conn,
            name="テスト選挙",
            election_type="衆議院議員選挙",
            prefecture=None,
            city=None,
            announcement_date=date.today().isoformat(),
            vote_date=vote_date.isoformat(),
            source_url="https://example.jp/election",
        )
        detail = election_detail.get_election_detail(self.conn, election["id"])
        self.assertEqual(detail["days_until_vote"], 10)
        self.assertEqual(detail["name"], "テスト選挙")
        self.assertEqual(detail["vote_start_time"], "07:00")
        self.assertEqual(detail["vote_end_time"], "20:00")


if __name__ == "__main__":
    unittest.main()
