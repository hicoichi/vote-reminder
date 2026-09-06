import os
import unittest

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import candidates, db, elections  # noqa: E402


class CandidatesTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        self.election = elections.add_election(
            self.conn, name="テスト選挙", election_type="衆議院議員選挙",
            prefecture=None, city=None, announcement_date="2026-10-01",
            vote_date="2026-10-15", source_url="https://example.jp/election",
        )

    def tearDown(self):
        self.conn.close()

    def test_add_and_list_candidates(self):
        candidates.add_candidate(
            self.conn, election_id=self.election["id"], name="候補者A", party="無所属",
            source_url="https://example.jp/candidate-a",
        )
        result = candidates.list_candidates(self.conn, self.election["id"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "候補者A")
        self.assertEqual(result[0]["source_url"], "https://example.jp/candidate-a")

    def test_gazette_set_and_show(self):
        self.assertIsNone(candidates.get_gazette(self.conn, self.election["id"]))
        candidates.set_gazette(
            self.conn, self.election["id"], content="公報の内容",
            source_url="https://example.jp/gazette",
        )
        gazette = candidates.get_gazette(self.conn, self.election["id"])
        self.assertEqual(gazette["content"], "公報の内容")

    def test_results_ordered_by_votes_desc(self):
        a = candidates.add_candidate(self.conn, election_id=self.election["id"], name="A")
        b = candidates.add_candidate(self.conn, election_id=self.election["id"], name="B")
        candidates.set_result(self.conn, a["id"], votes=100, elected=False)
        candidates.set_result(self.conn, b["id"], votes=200, elected=True)
        results = candidates.get_results(self.conn, self.election["id"])
        self.assertEqual([r["name"] for r in results], ["B", "A"])
        self.assertEqual(results[0]["elected"], 1)


if __name__ == "__main__":
    unittest.main()
