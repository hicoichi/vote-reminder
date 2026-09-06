"""vote-reminder CLIエントリーポイント。"""
import argparse
import json
import sys

from app import db, regions


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
