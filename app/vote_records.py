"""EPIC-07 投票済みを記録できる。"""
import sqlite3
from datetime import datetime, timezone

from app.elections import get_election
from app.regions import get_region


def mark_voted(conn: sqlite3.Connection, region_id: int, election_id: int) -> dict:
    """「投票した」と記録する。同じ選挙への記録は冪等（二重記録しない）。"""
    get_region(conn, region_id)  # 存在確認
    get_election(conn, election_id)  # 存在確認
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO vote_records (region_id, election_id, voted_at) VALUES (?, ?, ?)",
        (region_id, election_id, now),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM vote_records WHERE region_id = ? AND election_id = ?",
        (region_id, election_id),
    ).fetchone()
    return dict(row)


def list_voted_elections(conn: sqlite3.Connection, region_id: int) -> list[dict]:
    """投票済みの選挙・過去の投票履歴を確認する。"""
    rows = conn.execute(
        "SELECT vote_records.voted_at, elections.* FROM vote_records "
        "JOIN elections ON elections.id = vote_records.election_id "
        "WHERE vote_records.region_id = ? ORDER BY vote_records.voted_at DESC",
        (region_id,),
    ).fetchall()
    return [dict(r) for r in rows]
