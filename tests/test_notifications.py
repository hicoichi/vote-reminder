import os
import unittest
from datetime import date, timedelta

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, elections, notifications  # noqa: E402
from unittest.mock import patch
from io import BytesIO
import json
from app import regions  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class NotificationsTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        with patch("urllib.request.urlopen", side_effect=_mock_urlopen):
            self.region = regions.register_region(self.conn, "100-0001")

    def tearDown(self):
        self.conn.close()

    def _add_election(self, days_until_vote, **overrides):
        vote_date = date.today() + timedelta(days=days_until_vote)
        params = dict(
            name="テスト選挙",
            election_type="衆議院議員選挙",
            prefecture=None,
            city=None,
            announcement_date=date.today().isoformat(),
            vote_date=vote_date.isoformat(),
            source_url="https://example.jp/election",
        )
        params.update(overrides)
        return elections.add_election(self.conn, **params)

    def test_default_setting_is_enabled_with_7_1_0(self):
        setting = notifications.get_setting(self.conn, self.region["id"], "衆議院議員選挙")
        self.assertEqual(setting, {"enabled": True, "days_before": [7, 1, 0]})

    def test_notify_due_creates_notification_at_7_days_before(self):
        election = self._add_election(7)
        created = notifications.notify_due(self.conn, self.region["id"])
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0]["election_id"], election["id"])
        self.assertEqual(created[0]["notify_type"], "d7")

    def test_notify_due_is_idempotent(self):
        self._add_election(7)
        notifications.notify_due(self.conn, self.region["id"])
        second = notifications.notify_due(self.conn, self.region["id"])
        self.assertEqual(second, [])

    def test_notify_due_skips_days_not_configured(self):
        self._add_election(3)
        created = notifications.notify_due(self.conn, self.region["id"])
        self.assertEqual(created, [])

    def test_disable_setting_stops_notifications(self):
        self._add_election(0)
        notifications.set_setting(self.conn, self.region["id"], notifications.ALL_TYPES, enabled=False)
        created = notifications.notify_due(self.conn, self.region["id"])
        self.assertEqual(created, [])

    def test_custom_days_before_per_election_type(self):
        self._add_election(3, election_type="参議院議員選挙")
        notifications.set_setting(
            self.conn, self.region["id"], "参議院議員選挙", days_before=[3],
        )
        created = notifications.notify_due(self.conn, self.region["id"])
        self.assertEqual(len(created), 1)

    def test_past_election_is_finalized_and_excluded(self):
        election = self._add_election(-1)
        notifications.notify_due(self.conn, self.region["id"])
        updated = elections.get_election(self.conn, election["id"])
        self.assertEqual(updated["status"], "finished")


if __name__ == "__main__":
    unittest.main()
