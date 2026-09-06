import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

os.environ["VOTE_REMINDER_DB"] = ":memory:"

from app import db, polling_places, regions  # noqa: E402

ZIPCLOUD_RESPONSE = {
    "results": [{"address1": "東京都", "address2": "千代田区", "address3": "千代田"}]
}


def _mock_urlopen(*_args, **_kwargs):
    return BytesIO(json.dumps(ZIPCLOUD_RESPONSE).encode())


class PollingPlacesTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()
        with patch("urllib.request.urlopen", side_effect=_mock_urlopen):
            self.region = regions.register_region(self.conn, "100-0001")

    def tearDown(self):
        self.conn.close()

    def test_no_polling_place_registered_returns_none(self):
        self.assertIsNone(polling_places.get_polling_place_for_region(self.conn, self.region["id"]))

    def test_get_polling_place_for_region_includes_map_and_route(self):
        polling_places.add_polling_place(
            self.conn, prefecture="東京都", city="千代田区", name="千代田区役所投票所",
            address="東京都千代田区九段南1-2-1",
        )
        place = polling_places.get_polling_place_for_region(self.conn, self.region["id"])
        self.assertEqual(place["name"], "千代田区役所投票所")
        self.assertIn("maps/search", place["map_url"])
        self.assertIn("maps/dir", place["route_url"])
        self.assertEqual(place["open_time"], "07:00")
        self.assertEqual(place["close_time"], "20:00")


if __name__ == "__main__":
    unittest.main()
