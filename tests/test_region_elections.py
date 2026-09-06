import os
import unittest
from unittest.mock import patch
from io import BytesIO
import json

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, elections, region_elections, regions  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class RegionElectionsTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        with patch("urllib.request.urlopen", side_effect=_mock_urlopen):
            self.region = regions.register_region(self.conn, "100-0001")

    def tearDown(self):
        self.conn.close()

    def _add_election(self, **overrides):
        params = dict(
            name="テスト選挙",
            election_type="衆議院議員選挙",
            prefecture=None,
            city=None,
            announcement_date="2026-10-01",
            vote_date="2026-10-15",
            source_url="https://example.jp/election",
        )
        params.update(overrides)
        return elections.add_election(self.conn, **params)

    def test_national_election_matches_any_region(self):
        election = self._add_election()
        result = region_elections.list_elections_for_region(self.conn, self.region["id"])
        self.assertEqual([e["id"] for e in result], [election["id"]])

    def test_prefecture_level_election_requires_prefecture_match(self):
        self._add_election(election_type="都道府県知事選挙", prefecture="大阪府", city=None)
        result = region_elections.list_elections_for_region(self.conn, self.region["id"])
        self.assertEqual(result, [])

    def test_city_level_election_requires_city_match(self):
        election = self._add_election(
            election_type="市区町村長選挙", prefecture="東京都", city="千代田区",
        )
        result = region_elections.list_elections_for_region(self.conn, self.region["id"])
        self.assertEqual([e["id"] for e in result], [election["id"]])

    def test_filter_by_election_type(self):
        self._add_election(election_type="衆議院議員選挙")
        self._add_election(election_type="参議院議員選挙", vote_date="2026-11-01")
        result = region_elections.list_elections_for_region(
            self.conn, self.region["id"], election_type="参議院議員選挙"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["election_type"], "参議院議員選挙")

    def test_next_election_picks_nearest_upcoming(self):
        self._add_election(vote_date="2099-01-01")
        nearer = self._add_election(vote_date="2098-06-01")
        result = region_elections.next_election_for_region(self.conn, self.region["id"])
        self.assertEqual(result["id"], nearer["id"])


if __name__ == "__main__":
    unittest.main()
