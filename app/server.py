"""ブラウザから操作できる最小限のWebサーバー（標準ライブラリのみ）。

`python3 -m app.server` で起動し、http://localhost:8000 を開く。
静的な1ページ（static/index.html）から /api/* のJSON APIを呼び出す構成。
"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import (
    candidates, db, early_voting, election_detail, election_history, elections,
    notifications, polling_places, region_elections, regions, vote_records,
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _int(match, name):
    return int(match.group(name))


# --- ルートハンドラ ---------------------------------------------------
# 各関数は (conn, match, body, query) -> (status_code, response_body) を返す。

def h_region_register(conn, match, body, query):
    return 201, regions.register_region(conn, body["zipcode"])


def h_region_show(conn, match, body, query):
    return 200, regions.get_region(conn, _int(match, "region_id"))


def h_region_update(conn, match, body, query):
    return 200, regions.update_region(conn, _int(match, "region_id"), body["zipcode"])


def h_region_delete(conn, match, body, query):
    regions.delete_region(conn, _int(match, "region_id"))
    return 200, {"deleted": True}


def h_election_add(conn, match, body, query):
    return 201, elections.add_election(
        conn,
        name=body["name"], election_type=body["election_type"],
        prefecture=body.get("prefecture") or None, city=body.get("city") or None,
        announcement_date=body["announcement_date"], vote_date=body["vote_date"],
        source_url=body["source_url"],
        vote_start_time=body.get("vote_start_time", "07:00"),
        vote_end_time=body.get("vote_end_time", "20:00"),
    )


def h_election_list(conn, match, body, query):
    return 200, elections.list_elections(conn)


def h_election_detail(conn, match, body, query):
    return 200, election_detail.get_election_detail(conn, _int(match, "election_id"))


def h_election_update(conn, match, body, query):
    return 200, elections.update_election(
        conn, _int(match, "election_id"), source_url=body["source_url"],
        vote_date=body.get("vote_date"), announcement_date=body.get("announcement_date"),
    )


def h_election_status(conn, match, body, query):
    return 200, elections.set_election_status(conn, _int(match, "election_id"), body["status"])


def h_election_stale(conn, match, body, query):
    days = int(query.get("days", ["30"])[0])
    return 200, elections.find_stale_elections(conn, days=days)


def h_fetch_log_list(conn, match, body, query):
    return 200, elections.list_fetch_failures(conn)


def h_region_elections_list(conn, match, body, query):
    election_type = query.get("type", [None])[0]
    return 200, region_elections.list_elections_for_region(
        conn, _int(match, "region_id"), election_type
    )


def h_region_elections_next(conn, match, body, query):
    return 200, region_elections.next_election_for_region(conn, _int(match, "region_id"))


def h_notify_check(conn, match, body, query):
    return 200, notifications.notify_due(conn, _int(match, "region_id"))


def h_notify_list(conn, match, body, query):
    return 200, notifications.list_notifications(conn, _int(match, "region_id"))


def h_notify_setting_show(conn, match, body, query):
    election_type = query.get("type", [notifications.ALL_TYPES])[0]
    return 200, notifications.get_setting(conn, _int(match, "region_id"), election_type)


def h_notify_setting_set(conn, match, body, query):
    days_before = body.get("days_before")
    if isinstance(days_before, str):
        days_before = [int(v) for v in days_before.split(",") if v.strip() != ""]
    return 200, notifications.set_setting(
        conn, _int(match, "region_id"), body.get("election_type", notifications.ALL_TYPES),
        enabled=body.get("enabled"), days_before=days_before,
    )


def h_polling_place_add(conn, match, body, query):
    return 201, polling_places.add_polling_place(
        conn, prefecture=body["prefecture"], city=body["city"], name=body["name"],
        address=body["address"], open_time=body.get("open_time", "07:00"),
        close_time=body.get("close_time", "20:00"),
    )


def h_polling_place_show(conn, match, body, query):
    return 200, polling_places.get_polling_place_for_region(conn, _int(match, "region_id"))


def h_early_voting_add(conn, match, body, query):
    return 201, early_voting.add_early_voting_place(
        conn, election_id=int(body["election_id"]), name=body["name"], address=body["address"],
        period_start=body["period_start"], period_end=body["period_end"],
        open_time=body.get("open_time", "08:30"), close_time=body.get("close_time", "20:00"),
    )


def h_early_voting_show(conn, match, body, query):
    return 200, early_voting.list_early_voting_places_for_region(
        conn, _int(match, "region_id"), _int(match, "election_id")
    )


def h_vote_record_mark(conn, match, body, query):
    return 201, vote_records.mark_voted(conn, _int(match, "region_id"), int(body["election_id"]))


def h_vote_record_list(conn, match, body, query):
    return 200, vote_records.list_voted_elections(conn, _int(match, "region_id"))


def h_candidate_add(conn, match, body, query):
    return 201, candidates.add_candidate(
        conn, election_id=int(body["election_id"]), name=body["name"],
        party=body.get("party"), profile=body.get("profile"), source_url=body.get("source_url"),
    )


def h_candidate_list(conn, match, body, query):
    return 200, candidates.list_candidates(conn, _int(match, "election_id"))


def h_gazette_set(conn, match, body, query):
    return 200, candidates.set_gazette(
        conn, _int(match, "election_id"), body["content"], body["source_url"]
    )


def h_gazette_show(conn, match, body, query):
    return 200, candidates.get_gazette(conn, _int(match, "election_id"))


def h_result_set(conn, match, body, query):
    return 200, candidates.set_result(
        conn, _int(match, "candidate_id"), int(body["votes"]), bool(body.get("elected", False))
    )


def h_result_show(conn, match, body, query):
    return 200, candidates.get_results(conn, _int(match, "election_id"))


def h_history_elections(conn, match, body, query):
    return 200, election_history.list_past_elections(conn, _int(match, "region_id"))


def h_history_results(conn, match, body, query):
    return 200, election_history.get_past_election_results(conn, _int(match, "election_id"))


def h_history_votes(conn, match, body, query):
    return 200, election_history.list_voting_history(conn, _int(match, "region_id"))


ROUTES = [
    ("POST", r"/api/regions", h_region_register),
    ("GET", r"/api/regions/(?P<region_id>\d+)", h_region_show),
    ("PUT", r"/api/regions/(?P<region_id>\d+)", h_region_update),
    ("DELETE", r"/api/regions/(?P<region_id>\d+)", h_region_delete),

    ("POST", r"/api/elections", h_election_add),
    ("GET", r"/api/elections", h_election_list),
    ("GET", r"/api/elections/stale", h_election_stale),
    ("GET", r"/api/elections/(?P<election_id>\d+)", h_election_detail),
    ("PUT", r"/api/elections/(?P<election_id>\d+)/status", h_election_status),
    ("PUT", r"/api/elections/(?P<election_id>\d+)", h_election_update),
    ("GET", r"/api/elections/(?P<election_id>\d+)/candidates", h_candidate_list),
    ("GET", r"/api/elections/(?P<election_id>\d+)/gazette", h_gazette_show),
    ("PUT", r"/api/elections/(?P<election_id>\d+)/gazette", h_gazette_set),
    ("GET", r"/api/elections/(?P<election_id>\d+)/results", h_result_show),
    ("GET", r"/api/elections/(?P<election_id>\d+)/history/results", h_history_results),

    ("GET", r"/api/fetch-logs", h_fetch_log_list),

    ("GET", r"/api/regions/(?P<region_id>\d+)/elections/next", h_region_elections_next),
    ("GET", r"/api/regions/(?P<region_id>\d+)/elections", h_region_elections_list),
    ("GET", r"/api/regions/(?P<region_id>\d+)/elections/(?P<election_id>\d+)/early-voting",
     h_early_voting_show),

    ("POST", r"/api/regions/(?P<region_id>\d+)/notify/check", h_notify_check),
    ("GET", r"/api/regions/(?P<region_id>\d+)/notifications", h_notify_list),
    ("GET", r"/api/regions/(?P<region_id>\d+)/notify-settings", h_notify_setting_show),
    ("PUT", r"/api/regions/(?P<region_id>\d+)/notify-settings", h_notify_setting_set),

    ("GET", r"/api/regions/(?P<region_id>\d+)/polling-place", h_polling_place_show),
    ("POST", r"/api/polling-places", h_polling_place_add),

    ("POST", r"/api/early-voting-places", h_early_voting_add),

    ("POST", r"/api/regions/(?P<region_id>\d+)/vote-records", h_vote_record_mark),
    ("GET", r"/api/regions/(?P<region_id>\d+)/vote-records", h_vote_record_list),

    ("POST", r"/api/candidates", h_candidate_add),
    ("PUT", r"/api/candidates/(?P<candidate_id>\d+)/result", h_result_set),

    ("GET", r"/api/regions/(?P<region_id>\d+)/history/elections", h_history_elections),
    ("GET", r"/api/regions/(?P<region_id>\d+)/history/votes", h_history_votes),
]

_COMPILED_ROUTES = [(m, re.compile(f"^{p}$"), fn) for m, p, fn in ROUTES]

_CONTENT_TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                   ".css": "text/css; charset=utf-8"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 標準出力を汚さない（PoCのため詳細ログは省略）

    def _send_json(self, status: int, obj) -> None:
        payload = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _serve_static(self, filename: str) -> None:
        path = (STATIC_DIR / filename).resolve()
        if STATIC_DIR not in path.parents or not path.is_file():
            self._send_json(404, {"error": "not found"})
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if method == "GET" and path == "/":
            self._serve_static("index.html")
            return
        if method == "GET" and path.startswith("/static/"):
            self._serve_static(path[len("/static/"):])
            return

        for route_method, pattern, fn in _COMPILED_ROUTES:
            if route_method != method:
                continue
            match = pattern.fullmatch(path)
            if match is None:
                continue
            try:
                body = self._read_json_body() if method in ("POST", "PUT") else None
                conn = db.connect()
                try:
                    status, result = fn(conn, match, body, query)
                finally:
                    conn.close()
            except ValueError as e:
                self._send_json(400, {"error": str(e)})
                return
            except KeyError as e:
                self._send_json(400, {"error": f"必須項目が不足しています: {e}"})
                return
            self._send_json(status, result)
            return

        self._send_json(404, {"error": "not found"})

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")


def run(port: int = 8000) -> None:
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"vote-reminder サーバーを起動しました: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
