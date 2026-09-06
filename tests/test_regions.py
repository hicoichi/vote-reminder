import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, regions  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class RegionsTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()

    def tearDown(self):
        self.conn.close()

    @patch("urllib.request.urlopen", side_effect=_mock_urlopen)
    def test_register_and_show_region(self, _mock):
        region = regions.register_region(self.conn, "100-0001")
        self.assertEqual(region["prefecture"], "東京都")
        self.assertEqual(region["city"], "千代田区")

        fetched = regions.get_region(self.conn, region["id"])
        self.assertEqual(fetched, region)

    @patch("urllib.request.urlopen", side_effect=_mock_urlopen)
    def test_update_region(self, _mock):
        region = regions.register_region(self.conn, "1000001")
        updated = regions.update_region(self.conn, region["id"], "100-0001")
        self.assertEqual(updated["zipcode"], "1000001")

    @patch("urllib.request.urlopen", side_effect=_mock_urlopen)
    def test_delete_region(self, _mock):
        region = regions.register_region(self.conn, "1000001")
        regions.delete_region(self.conn, region["id"])
        with self.assertRaises(ValueError):
            regions.get_region(self.conn, region["id"])

    def test_invalid_zipcode_format(self):
        with self.assertRaises(ValueError):
            regions.register_region(self.conn, "abc")


if __name__ == "__main__":
    unittest.main()
