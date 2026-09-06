"""vote-reminder CLIエントリーポイント。"""
import argparse
import json
import sys

from app import db, election_detail, elections, region_elections, regions


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def cmd_region_register(args, conn):
    _print(regions.register_region(conn, args.zipcode))


def cmd_region_show(args, conn):
    _print(regions.get_region(conn, args.region_id))


def cmd_region_update(args, conn):
    _print(regions.update_region(conn, args.region_id, args.zipcode))


def cmd_region_delete(args, conn):
    regions.delete_region(conn, args.region_id)
    print(f"地域 id={args.region_id} を削除しました")


def cmd_election_add(args, conn):
    _print(elections.add_election(
        conn,
        name=args.name,
        election_type=args.type,
        prefecture=args.prefecture,
        city=args.city,
        announcement_date=args.announcement_date,
        vote_date=args.vote_date,
        source_url=args.source_url,
    ))


def cmd_election_show(args, conn):
    _print(elections.get_election(conn, args.election_id))


def cmd_election_list(args, conn):
    _print(elections.list_elections(conn))


def cmd_election_update(args, conn):
    _print(elections.update_election(
        conn, args.election_id, source_url=args.source_url,
        vote_date=args.vote_date, announcement_date=args.announcement_date,
    ))


def cmd_election_status(args, conn):
    _print(elections.set_election_status(conn, args.election_id, args.status))


def cmd_election_stale(args, conn):
    _print(elections.find_stale_elections(conn, days=args.days))


def cmd_fetch_log_list(args, conn):
    _print(elections.list_fetch_failures(conn))


def cmd_my_elections_list(args, conn):
    _print(region_elections.list_elections_for_region(conn, args.region_id, args.type))


def cmd_my_elections_next(args, conn):
    _print(region_elections.next_election_for_region(conn, args.region_id))


def cmd_election_detail_show(args, conn):
    _print(election_detail.get_election_detail(conn, args.election_id))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vote-reminder")
    sub = parser.add_subparsers(dest="command", required=True)

    region = sub.add_parser("region", help="地域の登録・確認・変更・削除")
    region_sub = region.add_subparsers(dest="region_command", required=True)

    p = region_sub.add_parser("register", help="郵便番号から地域を登録する")
    p.add_argument("zipcode")
    p.set_defaults(func=cmd_region_register)

    p = region_sub.add_parser("show", help="登録地域を確認する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_region_show)

    p = region_sub.add_parser("update", help="登録地域の郵便番号を変更する")
    p.add_argument("region_id", type=int)
    p.add_argument("zipcode")
    p.set_defaults(func=cmd_region_update)

    p = region_sub.add_parser("delete", help="登録地域を削除する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_region_delete)

    election = sub.add_parser("election", help="選挙情報の登録・更新（管理用）")
    election_sub = election.add_subparsers(dest="election_command", required=True)

    p = election_sub.add_parser("add", help="選挙情報を登録する")
    p.add_argument("name")
    p.add_argument("--type", required=True, choices=sorted(elections.ELECTION_TYPES))
    p.add_argument("--prefecture", default=None)
    p.add_argument("--city", default=None)
    p.add_argument("--announcement-date", required=True, dest="announcement_date")
    p.add_argument("--vote-date", required=True, dest="vote_date")
    p.add_argument("--source-url", required=True, dest="source_url")
    p.set_defaults(func=cmd_election_add)

    p = election_sub.add_parser("show", help="選挙情報を確認する")
    p.add_argument("election_id", type=int)
    p.set_defaults(func=cmd_election_show)

    p = election_sub.add_parser("list", help="登録済みの選挙を一覧表示する")
    p.set_defaults(func=cmd_election_list)

    p = election_sub.add_parser("update", help="選挙情報を更新する（投票日変更の反映など）")
    p.add_argument("election_id", type=int)
    p.add_argument("--source-url", required=True, dest="source_url")
    p.add_argument("--vote-date", default=None, dest="vote_date")
    p.add_argument("--announcement-date", default=None, dest="announcement_date")
    p.set_defaults(func=cmd_election_update)

    p = election_sub.add_parser("status", help="選挙の中止・延期・終了を反映する")
    p.add_argument("election_id", type=int)
    p.add_argument("status", choices=sorted(elections.STATUSES))
    p.set_defaults(func=cmd_election_status)

    p = election_sub.add_parser("stale", help="出典が古い選挙情報を判別する")
    p.add_argument("--days", type=int, default=30)
    p.set_defaults(func=cmd_election_stale)

    fetch_log = sub.add_parser("fetch-log", help="選挙データ取得ログ")
    fetch_log_sub = fetch_log.add_subparsers(dest="fetch_log_command", required=True)
    p = fetch_log_sub.add_parser("list", help="データ取得に失敗した履歴を確認する")
    p.set_defaults(func=cmd_fetch_log_list)

    my_elections = sub.add_parser("my-elections", help="自分の地域に関係する選挙を確認する")
    my_elections_sub = my_elections.add_subparsers(dest="my_elections_command", required=True)

    p = my_elections_sub.add_parser("list", help="地域に紐づく実施予定の選挙を一覧表示する")
    p.add_argument("region_id", type=int)
    p.add_argument("--type", default=None, choices=sorted(elections.ELECTION_TYPES))
    p.set_defaults(func=cmd_my_elections_list)

    p = my_elections_sub.add_parser("next", help="次回の選挙を判定する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_my_elections_next)

    p = election_sub.add_parser(
        "detail", help="選挙名・投票日・残り日数など選挙の詳細を確認する"
    )
    p.add_argument("election_id", type=int)
    p.set_defaults(func=cmd_election_detail_show)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    conn = db.connect()
    try:
        args.func(args, conn)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
