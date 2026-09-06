"""EPIC-05 投票所を確認できる。"""
import sqlite3
from urllib.parse import quote

from app.regions import get_region


def add_polling_place(
    conn: sqlite3.Connection, *, prefecture: str, city: str, name: str,
    address: str, open_time: str = "07:00", close_time: str = "20:00",
) -> dict:
    cur = conn.execute(
        "INSERT INTO polling_places (prefecture, city, name, address, open_time, close_time) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (prefecture, city, name, address, open_time, close_time),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM polling_places WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def get_polling_place_for_region(conn: sqlite3.Connection, region_id: int) -> dict | None:
    """登録地域（自治体）に対応する投票所を確認する。住所・地図・経路・投票時間を含む。"""
    region = get_region(conn, region_id)
    row = conn.execute(
        "SELECT * FROM polling_places WHERE prefecture = ? AND city = ? LIMIT 1",
        (region["prefecture"], region["city"]),
    ).fetchone()
    if row is None:
        return None
    place = dict(row)
    place["map_url"] = f"https://www.google.com/maps/search/?api=1&query={quote(place['address'])}"
    place["route_url"] = f"https://www.google.com/maps/dir/?api=1&destination={quote(place['address'])}"
    return place
