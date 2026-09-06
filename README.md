# vote-reminder

> 「投票日を知らなかった」をなくす。

ユーザーが一度だけ居住地域を登録すると、自分に関係する選挙を自動で判定し、投票日までリマインドするアプリです。

## プロダクトゴール

居住地域（郵便番号）を登録するだけで、以下を自動的に行います。

1. 自治体・選挙区を特定する
2. 対象となる選挙（衆院選・参院選・知事選・地方議会選など）を判定する
3. 次回の選挙の投票日・選挙名を表示する
4. 投票日までの残り日数を表示する
5. 投票日の7日前・前日・当日に通知する

## ドキュメント

* [ユーザーストーリーマップ](docs/user-story-map.md) — プロダクトゴール、リリース計画（v0.1〜v1.0）、EPIC一覧、優先順位の全体像
* [GitHub Project](https://github.com/users/hicoichi/projects/2) — EPIC単位のタスク管理ボード
* [Issues](https://github.com/hicoichi/vote-reminder/issues) — EPICごとのユーザーストーリー（チェックリスト形式）

## リリース計画

| バージョン | テーマ | 状態 |
|---|---|---|
| v0.1 | 忘れない（地域登録〜通知） | PoC実装済み |
| v0.2 | 投票できる（投票所・期日前投票） | PoC実装済み |
| v0.3 | 選挙を知る（候補者・選挙公報・開票結果） | PoC実装済み |
| v1.0 | 選挙のインフラ | — |

v0.1（MVP）の完了条件は[ユーザーストーリーマップ内のDefinition of Done](docs/user-story-map.md#mvp-definition-of-done)を参照してください。

## 開発状況

**本プロジェクトは試しに作るPoC（概念実証）であり、作り込みは行っていません。** 詳細は[.claude/CLAUDE.md](.claude/CLAUDE.md)を参照してください。

EPIC-01〜10のユーザーストーリーをPythonのCLIアプリケーションとして実装済みです。フロントエンドや実際の通知配信（メール/プッシュ）、外部の選挙データ連携は行っておらず、CLIとSQLiteによるデータモデル・ロジックの検証にとどまります。

### セットアップ・実行方法

Python 3.12（標準ライブラリのみ、追加インストール不要）で動作します。

```bash
# 地域を登録する（郵便番号 → 自治体をzipcloud APIで特定）
python3 -m app.cli region register 100-0001

# 登録地域に関係する選挙を確認する（選挙情報はadminコマンドで別途登録する）
python3 -m app.cli my-elections list 1
python3 -m app.cli my-elections next 1

# 通知タイミングが到来した選挙の通知を作成する
python3 -m app.cli notify check 1

# 「投票した」と記録する
python3 -m app.cli vote-record mark 1 1
```

全コマンドは `python3 -m app.cli --help` で確認できます。DBファイルは既定で `data/vote_reminder.db`（`VOTE_REMINDER_DB` 環境変数で変更可）に作成されます。

### テスト

```bash
python3 -m unittest discover -s tests
```

## ライセンス

[MIT License](LICENSE)
