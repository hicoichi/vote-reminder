"""EPIC-09 候補者・選挙情報を確認できる。"""
import sqlite3

from app.elections import get_election


def add_candidate(
    conn: sqlite3.Connection, *, election_id: int, name: str,
    party: str | None = None, profile: str | None = None, source_url: str | None = None,
) -> dict:
    get_election(conn, election_id)  # 存在確認
    cur = conn.execute(
        "INSERT INTO candidates (election_id, name, party, profile, source_url) "
        "VALUES (?, ?, ?, ?, ?)",
        (election_id, name, party, profile, source_url),
    )
    conn.commit()
    return get_candidate(conn, cur.lastrowid)


def get_candidate(conn: sqlite3.Connection, candidate_id: int) -> dict:
    row = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    if row is None:
        raise ValueError(f"候補者が見つかりません: id={candidate_id}")
    return dict(row)


def list_candidates(conn: sqlite3.Connection, election_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM candidates WHERE election_id = ? ORDER BY id", (election_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def set_gazette(conn: sqlite3.Connection, election_id: int, content: str, source_url: str) -> dict:
    """選挙公報を登録・更新する。"""
    get_election(conn, election_id)  # 存在確認
    conn.execute(
        "INSERT INTO election_gazettes (election_id, content, source_url) VALUES (?, ?, ?) "
        "ON CONFLICT(election_id) DO UPDATE SET content = excluded.content, "
        "source_url = excluded.source_url",
        (election_id, content, source_url),
    )
    conn.commit()
    return get_gazette(conn, election_id)


def get_gazette(conn: sqlite3.Connection, election_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM election_gazettes WHERE election_id = ?", (election_id,)
    ).fetchone()
    return dict(row) if row else None


def set_result(conn: sqlite3.Connection, candidate_id: int, votes: int, elected: bool) -> dict:
    """候補者の開票結果を登録・更新する。"""
    get_candidate(conn, candidate_id)  # 存在確認
    conn.execute(
        "INSERT INTO election_results (candidate_id, votes, elected) VALUES (?, ?, ?) "
        "ON CONFLICT(candidate_id) DO UPDATE SET votes = excluded.votes, "
        "elected = excluded.elected",
        (candidate_id, votes, int(elected)),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM election_results WHERE candidate_id = ?", (candidate_id,)
    ).fetchone()
    return dict(row)


def get_results(conn: sqlite3.Connection, election_id: int) -> list[dict]:
    """選挙の開票結果を候補者情報とあわせて確認する。"""
    rows = conn.execute(
        "SELECT candidates.*, election_results.votes AS votes, "
        "election_results.elected AS elected FROM candidates "
        "LEFT JOIN election_results ON election_results.candidate_id = candidates.id "
        "WHERE candidates.election_id = ? "
        "ORDER BY election_results.votes IS NULL, election_results.votes DESC",
        (election_id,),
    ).fetchall()
    return [dict(r) for r in rows]
