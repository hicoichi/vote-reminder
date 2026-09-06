"""vote-reminder CLIエントリーポイント。"""
import argparse
import json
import sys

from app import (
    db, early_voting, election_detail, elections, notifications, polling_places,
    region_elections, regions, vote_records,
)


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


def cmd_notify_check(args, conn):
    _print(notifications.notify_due(conn, args.region_id))


def cmd_notify_list(args, conn):
    _print(notifications.list_notifications(conn, args.region_id))


def cmd_notify_setting_set(args, conn):
    days_before = [int(d) for d in args.days_before.split(",")] if args.days_before else None
    enabled = None
    if args.enable:
        enabled = True
    elif args.disable:
        enabled = False
    _print(notifications.set_setting(
        conn, args.region_id, args.type, enabled=enabled, days_before=days_before,
    ))


def cmd_notify_setting_show(args, conn):
    _print(notifications.get_setting(conn, args.region_id, args.type))


def cmd_polling_place_add(args, conn):
    _print(polling_places.add_polling_place(
        conn, prefecture=args.prefecture, city=args.city, name=args.name,
        address=args.address, open_time=args.open_time, close_time=args.close_time,
    ))


def cmd_polling_place_show(args, conn):
    _print(polling_places.get_polling_place_for_region(conn, args.region_id))


def cmd_early_voting_add(args, conn):
    _print(early_voting.add_early_voting_place(
        conn, election_id=args.election_id, name=args.name, address=args.address,
        period_start=args.period_start, period_end=args.period_end,
        open_time=args.open_time, close_time=args.close_time,
    ))


def cmd_early_voting_show(args, conn):
    _print(early_voting.list_early_voting_places_for_region(conn, args.region_id, args.election_id))


def cmd_vote_record_mark(args, conn):
    _print(vote_records.mark_voted(conn, args.region_id, args.election_id))


def cmd_vote_record_list(args, conn):
    _print(vote_records.list_voted_elections(conn, args.region_id))


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

    notify = sub.add_parser("notify", help="投票日の通知")
    notify_sub = notify.add_subparsers(dest="notify_command", required=True)

    p = notify_sub.add_parser("check", help="通知タイミングが到来した選挙の通知を作成する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_notify_check)

    p = notify_sub.add_parser("list", help="通知履歴を確認する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_notify_list)

    p = notify_sub.add_parser("setting-show", help="通知設定を確認する")
    p.add_argument("region_id", type=int)
    p.add_argument("--type", default=notifications.ALL_TYPES,
                    choices=sorted(elections.ELECTION_TYPES) + [notifications.ALL_TYPES])
    p.set_defaults(func=cmd_notify_setting_show)

    p = notify_sub.add_parser(
        "setting-set", help="通知のON/OFF・通知タイミングを選挙種別ごとに変更する"
    )
    p.add_argument("region_id", type=int)
    p.add_argument("--type", default=notifications.ALL_TYPES,
                    choices=sorted(elections.ELECTION_TYPES) + [notifications.ALL_TYPES])
    p.add_argument("--days-before", default=None, dest="days_before",
                    help="カンマ区切りの通知タイミング（例: 7,1,0）")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--enable", action="store_true")
    group.add_argument("--disable", action="store_true")
    p.set_defaults(func=cmd_notify_setting_set)

    polling_place = sub.add_parser("polling-place", help="投票所の確認（管理用登録を含む）")
    polling_place_sub = polling_place.add_subparsers(dest="polling_place_command", required=True)

    p = polling_place_sub.add_parser("add", help="投票所を登録する（管理用）")
    p.add_argument("--prefecture", required=True)
    p.add_argument("--city", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--address", required=True)
    p.add_argument("--open-time", default="07:00", dest="open_time")
    p.add_argument("--close-time", default="20:00", dest="close_time")
    p.set_defaults(func=cmd_polling_place_add)

    p = polling_place_sub.add_parser("show", help="登録地域に対応する投票所を確認する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_polling_place_show)

    early_voting_p = sub.add_parser("early-voting", help="期日前投票の確認（管理用登録を含む）")
    early_voting_sub = early_voting_p.add_subparsers(dest="early_voting_command", required=True)

    p = early_voting_sub.add_parser("add", help="期日前投票所を登録する（管理用）")
    p.add_argument("--election-id", type=int, required=True, dest="election_id")
    p.add_argument("--name", required=True)
    p.add_argument("--address", required=True)
    p.add_argument("--period-start", required=True, dest="period_start")
    p.add_argument("--period-end", required=True, dest="period_end")
    p.add_argument("--open-time", default="08:30", dest="open_time")
    p.add_argument("--close-time", default="20:00", dest="close_time")
    p.set_defaults(func=cmd_early_voting_add)

    p = early_voting_sub.add_parser("show", help="期日前投票の期間・投票所を確認する")
    p.add_argument("region_id", type=int)
    p.add_argument("election_id", type=int)
    p.set_defaults(func=cmd_early_voting_show)

    vote_record = sub.add_parser("vote-record", help="投票済みの記録・確認")
    vote_record_sub = vote_record.add_subparsers(dest="vote_record_command", required=True)

    p = vote_record_sub.add_parser("mark", help="「投票した」と記録する")
    p.add_argument("region_id", type=int)
    p.add_argument("election_id", type=int)
    p.set_defaults(func=cmd_vote_record_mark)

    p = vote_record_sub.add_parser("list", help="投票済みの選挙・投票履歴を確認する")
    p.add_argument("region_id", type=int)
    p.set_defaults(func=cmd_vote_record_list)

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
