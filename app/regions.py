"""EPIC-01 地域を登録できる。"""
import json
import re
import sqlite3
import urllib.request
from datetime import datetime, timezone

ZIPCLOUD_URL = "https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"


def _normalize_zipcode(zipcode: str) -> str:
    digits = zipcode.replace("-", "").strip()
    if not re.fullmatch(r"\d{7}", digits):
        raise ValueError(f"郵便番号の形式が不正です: {zipcode}")
    return digits


def lookup_municipality(zipcode: str) -> dict:
    """郵便番号から都道府県・市区町村・町域を特定する（zipcloud APIを利用）。"""
    digits = _normalize_zipcode(zipcode)
    with urllib.request.urlopen(ZIPCLOUD_URL.format(zipcode=digits), timeout=10) as res:
        body = json.loads(res.read())
    results = body.get("results")
    if not results:
        raise ValueError(f"郵便番号に該当する住所が見つかりません: {zipcode}")
    top = results[0]
    return {
        "prefecture": top["address1"],
        "city": top["address2"],
        "town": top["address3"],
    }


def register_region(conn: sqlite3.Connection, zipcode: str) -> dict:
    municipality = lookup_municipality(zipcode)
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO regions (zipcode, prefecture, city, town, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (_normalize_zipcode(zipcode), municipality["prefecture"], municipality["city"],
         municipality["town"], now, now),
    )
    conn.commit()
    return get_region(conn, cur.lastrowid)


def get_region(conn: sqlite3.Connection, region_id: int) -> dict:
    row = conn.execute("SELECT * FROM regions WHERE id = ?", (region_id,)).fetchone()
    if row is None:
        raise ValueError(f"地域が見つかりません: id={region_id}")
    return dict(row)


def update_region(conn: sqlite3.Connection, region_id: int, zipcode: str) -> dict:
    get_region(conn, region_id)  # 存在確認
    municipality = lookup_municipality(zipcode)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE regions SET zipcode = ?, prefecture = ?, city = ?, town = ?, updated_at = ? "
        "WHERE id = ?",
        (_normalize_zipcode(zipcode), municipality["prefecture"], municipality["city"],
         municipality["town"], now, region_id),
    )
    conn.commit()
    return get_region(conn, region_id)


def delete_region(conn: sqlite3.Connection, region_id: int) -> None:
    get_region(conn, region_id)  # 存在確認
    conn.execute("DELETE FROM regions WHERE id = ?", (region_id,))
    conn.commit()
