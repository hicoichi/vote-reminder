import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, election_history, elections, regions, vote_records  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class ElectionHistoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        with patch("urllib.request.urlopen", side_effect=_mock_urlopen):
            self.region = regions.register_region(self.conn, "100-0001")

    def tearDown(self):
        self.conn.close()

    def test_list_past_elections_excludes_upcoming(self):
        past = elections.add_election(
            self.conn, name="過去の選挙", election_type="衆議院議員選挙",
            prefecture=None, city=None, announcement_date="2020-10-01",
            vote_date="2020-10-15", source_url="https://example.jp/past",
        )
        elections.add_election(
            self.conn, name="未来の選挙", election_type="衆議院議員選挙",
            prefecture=None, city=None, announcement_date="2099-01-01",
            vote_date="2099-01-15", source_url="https://example.jp/future",
        )
        result = election_history.list_past_elections(self.conn, self.region["id"])
        self.assertEqual([e["id"] for e in result], [past["id"]])

    def test_list_voting_history_reflects_vote_records(self):
        election = elections.add_election(
            self.conn, name="過去の選挙", election_type="衆議院議員選挙",
            prefecture=None, city=None, announcement_date="2020-10-01",
            vote_date="2020-10-15", source_url="https://example.jp/past",
        )
        vote_records.mark_voted(self.conn, self.region["id"], election["id"])
        result = election_history.list_voting_history(self.conn, self.region["id"])
        self.assertEqual([e["id"] for e in result], [election["id"]])


if __name__ == "__main__":
    unittest.main()
