"""EPIC-08 選挙情報を正確に提供できる（選挙データの基盤）。"""
import sqlite3
from datetime import date, datetime, timedelta, timezone

ELECTION_TYPES = {
    "衆議院議員選挙",
    "参議院議員選挙",
    "都道府県知事選挙",
    "市区町村長選挙",
    "都道府県議会議員選挙",
    "市区町村議会議員選挙",
    "補欠選挙",
    "再選挙",
}

STATUSES = {"scheduled", "postponed", "cancelled", "finished"}


def _validate_date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as e:
        raise ValueError(f"{field}の形式が不正です（YYYY-MM-DD）: {value}") from e


def add_election(
    conn: sqlite3.Connection,
    *,
    name: str,
    election_type: str,
    prefecture: str | None,
    city: str | None,
    announcement_date: str,
    vote_date: str,
    source_url: str,
    vote_start_time: str = "07:00",
    vote_end_time: str = "20:00",
) -> dict:
    if election_type not in ELECTION_TYPES:
        raise ValueError(f"未対応の選挙種別です: {election_type}")
    _validate_date(announcement_date, "公示日・告示日")
    _validate_date(vote_date, "投票日")
    if not source_url:
        raise ValueError("出典URLは必須です")
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO elections (name, election_type, prefecture, city, announcement_date, "
        "vote_date, vote_start_time, vote_end_time, status, source_url, source_updated_at, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'scheduled', ?, ?, ?, ?)",
        (name, election_type, prefecture, city, announcement_date, vote_date,
         vote_start_time, vote_end_time, source_url, now, now, now),
    )
    conn.commit()
    return get_election(conn, cur.lastrowid)


def get_election(conn: sqlite3.Connection, election_id: int) -> dict:
    row = conn.execute("SELECT * FROM elections WHERE id = ?", (election_id,)).fetchone()
    if row is None:
        raise ValueError(f"選挙が見つかりません: id={election_id}")
    return dict(row)


def update_election(
    conn: sqlite3.Connection,
    election_id: int,
    *,
    source_url: str,
    vote_date: str | None = None,
    announcement_date: str | None = None,
) -> dict:
    """選挙情報を更新する（投票日変更の反映を含む）。出典URLは更新のたびに必須。"""
    get_election(conn, election_id)  # 存在確認
    if not source_url:
        raise ValueError("出典URLは必須です")
    fields = {"source_url": source_url}
    if vote_date is not None:
        _validate_date(vote_date, "投票日")
        fields["vote_date"] = vote_date
    if announcement_date is not None:
        _validate_date(announcement_date, "公示日・告示日")
        fields["announcement_date"] = announcement_date
    now = datetime.now(timezone.utc).isoformat()
    fields["source_updated_at"] = now
    fields["updated_at"] = now
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE elections SET {set_clause} WHERE id = ?",
        (*fields.values(), election_id),
    )
    conn.commit()
    return get_election(conn, election_id)


def set_election_status(conn: sqlite3.Connection, election_id: int, status: str) -> dict:
    """選挙の中止・延期・終了などのステータスを反映する。"""
    if status not in STATUSES:
        raise ValueError(f"未対応のステータスです: {status}")
    get_election(conn, election_id)  # 存在確認
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE elections SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, election_id),
    )
    conn.commit()
    return get_election(conn, election_id)


def list_elections(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM elections ORDER BY vote_date").fetchall()
    return [dict(r) for r in rows]


def find_stale_elections(conn: sqlite3.Connection, days: int = 30) -> list[dict]:
    """出典データが一定期間更新されていない、かつ実施予定の選挙を判別する。"""
    threshold = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM elections WHERE status = 'scheduled' AND source_updated_at < ? "
        "ORDER BY source_updated_at",
        (threshold,),
    ).fetchall()
    return [dict(r) for r in rows]


def log_fetch(conn: sqlite3.Connection, target: str, success: bool, message: str = "") -> None:
    """選挙データ取得の成否を記録する（取得失敗の検知用）。"""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO fetch_logs (target, success, message, created_at) VALUES (?, ?, ?, ?)",
        (target, int(success), message, now),
    )
    conn.commit()


def list_fetch_failures(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM fetch_logs WHERE success = 0 ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]
