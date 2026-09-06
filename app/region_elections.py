"""EPIC-02 自分に関係する選挙を取得できる。"""
import sqlite3
from datetime import date

from app.regions import get_region


def _matches_region(election: dict, region: dict) -> bool:
    if election["prefecture"] is not None and election["prefecture"] != region["prefecture"]:
        return False
    if election["city"] is not None and election["city"] != region["city"]:
        return False
    return True


def list_elections_for_region(
    conn: sqlite3.Connection, region_id: int, election_type: str | None = None
) -> list[dict]:
    """登録地域（自治体・都道府県）に紐づく実施予定の選挙を取得する。"""
    region = get_region(conn, region_id)
    rows = conn.execute(
        "SELECT * FROM elections WHERE status = 'scheduled' ORDER BY vote_date"
    ).fetchall()
    result = [dict(r) for r in rows if _matches_region(dict(r), region)]
    if election_type is not None:
        result = [e for e in result if e["election_type"] == election_type]
    return result


def next_election_for_region(conn: sqlite3.Connection, region_id: int) -> dict | None:
    """登録地域における次回の選挙を判定する。"""
    today = date.today().isoformat()
    upcoming = [
        e for e in list_elections_for_region(conn, region_id) if e["vote_date"] >= today
    ]
    return upcoming[0] if upcoming else None
