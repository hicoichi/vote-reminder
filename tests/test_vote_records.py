import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, elections, regions, vote_records  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class VoteRecordsTest(unittest.TestCase):
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

    def test_mark_voted_and_list(self):
        vote_records.mark_voted(self.conn, self.region["id"], self.election["id"])
        voted = vote_records.list_voted_elections(self.conn, self.region["id"])
        self.assertEqual(len(voted), 1)
        self.assertEqual(voted[0]["id"], self.election["id"])

    def test_mark_voted_is_idempotent(self):
        vote_records.mark_voted(self.conn, self.region["id"], self.election["id"])
        vote_records.mark_voted(self.conn, self.region["id"], self.election["id"])
        voted = vote_records.list_voted_elections(self.conn, self.region["id"])
        self.assertEqual(len(voted), 1)

    def test_list_voted_elections_empty_when_none_recorded(self):
        self.assertEqual(vote_records.list_voted_elections(self.conn, self.region["id"]), [])


if __name__ == "__main__":
    unittest.main()
