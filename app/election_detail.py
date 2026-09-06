"""EPIC-03 選挙情報を表示できる。"""
import sqlite3
from datetime import date

from app.elections import get_election


def get_election_detail(conn: sqlite3.Connection, election_id: int) -> dict:
    """選挙名・種別・投票日・公示日/告示日・投票時間に加え、投票までの残り日数を返す。"""
    election = get_election(conn, election_id)
    vote_date = date.fromisoformat(election["vote_date"])
    election["days_until_vote"] = (vote_date - date.today()).days
    return election
