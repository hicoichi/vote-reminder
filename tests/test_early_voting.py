import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, early_voting, elections, regions  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class EarlyVotingTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        with patch("urllib.request.urlopen", side_effect=_mock_urlopen):
            self.region = regions.register_region(self.conn, "100-0001")
        self.election = elections.add_election(
            self.conn, name="テスト選挙", election_type="衆議院議員選挙",
            prefecture=None, city=None, announcement_date="2026-10-01",
            vote_date="2026-10-15", source_url="https://example.jp/election",
        )

    def tearDown(self):
        self.conn.close()

    def test_list_early_voting_places_for_relevant_election(self):
        early_voting.add_early_voting_place(
            self.conn, election_id=self.election["id"], name="千代田区役所",
            address="東京都千代田区九段南1-2-1", period_start="2026-10-05", period_end="2026-10-14",
        )
        places = early_voting.list_early_voting_places_for_region(
            self.conn, self.region["id"], self.election["id"]
        )
        self.assertEqual(len(places), 1)
        self.assertEqual(places[0]["period_start"], "2026-10-05")
        self.assertEqual(places[0]["open_time"], "08:30")

    def test_rejects_election_unrelated_to_region(self):
        other_election = elections.add_election(
            self.conn, name="他地域の選挙", election_type="市区町村長選挙",
            prefecture="大阪府", city="大阪市", announcement_date="2026-10-01",
            vote_date="2026-10-15", source_url="https://example.jp/other",
        )
        with self.assertRaises(ValueError):
            early_voting.list_early_voting_places_for_region(
                self.conn, self.region["id"], other_election["id"]
            )


if __name__ == "__main__":
    unittest.main()
