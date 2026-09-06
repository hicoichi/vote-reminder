"""EPIC-10 選挙履歴を確認できる。"""
import sqlite3
from datetime import date

from app.candidates import get_results
from app.region_elections import list_all_elections_for_region
from app.vote_records import list_voted_elections


def list_past_elections(conn: sqlite3.Connection, region_id: int) -> list[dict]:
    """登録地域に関係する過去の選挙を一覧で確認する。"""
    today = date.today().isoformat()
    past = [e for e in list_all_elections_for_region(conn, region_id) if e["vote_date"] < today]
    return sorted(past, key=lambda e: e["vote_date"], reverse=True)


def get_past_election_results(conn: sqlite3.Connection, election_id: int) -> list[dict]:
    """過去の選挙の開票結果を確認する。"""
    return get_results(conn, election_id)


def list_voting_history(conn: sqlite3.Connection, region_id: int) -> list[dict]:
    """自分の投票済み履歴を確認する。"""
    return list_voted_elections(conn, region_id)
