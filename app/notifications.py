"""EPIC-04 投票日を通知できる。"""
import sqlite3
from datetime import date, datetime, timezone

from app.elections import ELECTION_TYPES, finalize_past_elections
from app.region_elections import list_elections_for_region

DEFAULT_DAYS_BEFORE = [7, 1, 0]
ALL_TYPES = "*"


def _parse_days_before(value: str) -> list[int]:
    return [int(v) for v in value.split(",") if v != ""]


def get_setting(conn: sqlite3.Connection, region_id: int, election_type: str) -> dict:
    """選挙種別ごとの通知設定を取得する。個別設定がなければ全種別共通設定、
    それもなければシステムデフォルト（有効・7日前/前日/当日）を返す。"""
    for target_type in (election_type, ALL_TYPES):
        row = conn.execute(
            "SELECT * FROM notification_settings WHERE region_id = ? AND election_type = ?",
            (region_id, target_type),
        ).fetchone()
        if row is not None:
            return {"enabled": bool(row["enabled"]), "days_before": _parse_days_before(row["days_before"])}
    return {"enabled": True, "days_before": list(DEFAULT_DAYS_BEFORE)}


def set_setting(
    conn: sqlite3.Connection,
    region_id: int,
    election_type: str,
    *,
    enabled: bool | None = None,
    days_before: list[int] | None = None,
) -> dict:
    """通知のON/OFF、通知タイミング、選挙種別ごとの設定を変更する。"""
    if election_type != ALL_TYPES and election_type not in ELECTION_TYPES:
        raise ValueError(f"未対応の選挙種別です: {election_type}")
    current = get_setting(conn, region_id, election_type)
    new_enabled = current["enabled"] if enabled is None else enabled
    new_days_before = current["days_before"] if days_before is None else days_before
    conn.execute(
        "INSERT INTO notification_settings (region_id, election_type, enabled, days_before) "
        "VALUES (?, ?, ?, ?) "
        "ON CONFLICT(region_id, election_type) DO UPDATE SET enabled = excluded.enabled, "
        "days_before = excluded.days_before",
        (region_id, election_type, int(new_enabled), ",".join(str(d) for d in new_days_before)),
    )
    conn.commit()
    return {"enabled": new_enabled, "days_before": new_days_before}


def notify_due(conn: sqlite3.Connection, region_id: int) -> list[dict]:
    """通知タイミングが到来した選挙について通知を作成する（未送信分のみ）。"""
    finalize_past_elections(conn)
    today = date.today()
    created = []
    for election in list_elections_for_region(conn, region_id):
        setting = get_setting(conn, region_id, election["election_type"])
        if not setting["enabled"]:
            continue
        days_until = (date.fromisoformat(election["vote_date"]) - today).days
        if days_until < 0 or days_until not in setting["days_before"]:
            continue
        notify_type = f"d{days_until}"
        existing = conn.execute(
            "SELECT 1 FROM notifications WHERE region_id = ? AND election_id = ? AND notify_type = ?",
            (region_id, election["id"], notify_type),
        ).fetchone()
        if existing is not None:
            continue
        message = f"【投票日通知】{election['name']}の投票日まであと{days_until}日です（投票日: {election['vote_date']}）"
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO notifications (region_id, election_id, notify_type, sent_at, message) "
            "VALUES (?, ?, ?, ?, ?)",
            (region_id, election["id"], notify_type, now, message),
        )
        conn.commit()
        created.append({
            "region_id": region_id, "election_id": election["id"],
            "notify_type": notify_type, "sent_at": now, "message": message,
        })
    return created


def list_notifications(conn: sqlite3.Connection, region_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM notifications WHERE region_id = ? ORDER BY sent_at DESC", (region_id,)
    ).fetchall()
    return [dict(r) for r in rows]
