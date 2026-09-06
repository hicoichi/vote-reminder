import os
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, elections  # noqa: E402


class ElectionsTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()

    def tearDown(self):
        self.conn.close()

    def _add(self, **overrides):
        params = dict(
            name="第50回衆議院議員総選挙",
            election_type="衆議院議員選挙",
            prefecture=None,
            city=None,
            announcement_date="2026-10-01",
            vote_date="2026-10-15",
            source_url="https://example.jp/election",
        )
        params.update(overrides)
        return elections.add_election(self.conn, **params)

    def test_add_and_get_election(self):
        election = self._add()
        self.assertEqual(elections.get_election(self.conn, election["id"]), election)

    def test_add_rejects_unknown_type(self):
        with self.assertRaises(ValueError):
            self._add(election_type="謎の選挙")

    def test_update_election_reflects_vote_date_change(self):
        election = self._add()
        updated = elections.update_election(
            self.conn, election["id"], source_url="https://example.jp/updated",
            vote_date="2026-10-22",
        )
        self.assertEqual(updated["vote_date"], "2026-10-22")
        self.assertEqual(updated["source_url"], "https://example.jp/updated")

    def test_set_election_status_reflects_cancellation(self):
        election = self._add()
        updated = elections.set_election_status(self.conn, election["id"], "cancelled")
        self.assertEqual(updated["status"], "cancelled")

    def test_find_stale_elections(self):
        election = self._add()
        old = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        self.conn.execute(
            "UPDATE elections SET source_updated_at = ? WHERE id = ?",
            (old, election["id"]),
        )
        self.conn.commit()
        stale = elections.find_stale_elections(self.conn, days=30)
        self.assertEqual([e["id"] for e in stale], [election["id"]])

    def test_fetch_log_records_failure(self):
        elections.log_fetch(self.conn, "soumu.go.jp", success=False, message="timeout")
        failures = elections.list_fetch_failures(self.conn)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["target"], "soumu.go.jp")


if __name__ == "__main__":
    unittest.main()
