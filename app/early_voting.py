"""EPIC-06 期日前投票を確認できる。"""
import sqlite3

from app.elections import get_election
from app.region_elections import list_elections_for_region


def add_early_voting_place(
    conn: sqlite3.Connection, *, election_id: int, name: str, address: str,
    period_start: str, period_end: str, open_time: str = "08:30", close_time: str = "20:00",
) -> dict:
    get_election(conn, election_id)  # 存在確認
    cur = conn.execute(
        "INSERT INTO early_voting_places (election_id, name, address, period_start, "
        "period_end, open_time, close_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (election_id, name, address, period_start, period_end, open_time, close_time),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM early_voting_places WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return dict(row)


def list_early_voting_places_for_region(
    conn: sqlite3.Connection, region_id: int, election_id: int
) -> list[dict]:
    """登録地域に関係する選挙について、期日前投票の期間・投票所・住所・受付時間を確認する。"""
    relevant_ids = {e["id"] for e in list_elections_for_region(conn, region_id)}
    if election_id not in relevant_ids:
        raise ValueError(f"この選挙は指定地域に関係しません: election_id={election_id}")
    rows = conn.execute(
        "SELECT * FROM early_voting_places WHERE election_id = ? ORDER BY period_start",
        (election_id,),
    ).fetchall()
    return [dict(r) for r in rows]
