# vote-reminder — プロジェクト指示

## プロジェクトの位置づけ

**本プロジェクトは試しに作るものであり、作り込みは行わない。**

* PoC・検証目的の実装であり、本番運用や長期保守を前提としない。
* 過剰な設計・抽象化・汎用化は避け、要求された範囲を最小限の実装で満たすことを優先する。
* 網羅的なテスト、CI/CD整備、エラーハンドリングの作り込み、将来拡張を見越した設計は行わない（明示的に依頼された場合を除く）。
* 詳細なコーディング規約は [.claude/rules/coding-conventions.md](rules/coding-conventions.md) を参照すること（下記でインポート）。

@rules/coding-conventions.md

## プロダクト概要

「投票日を知らなかった」をなくすリマインダーアプリ。ユーザーが郵便番号を登録すると、自分に関係する選挙を自動判定し、投票日までリマインドする。

詳細な要件・スコープは以下を必ず参照すること。

* [docs/user-story-map.md](../docs/user-story-map.md) — プロダクトゴール、ユーザーストーリーマップ、リリース計画（v0.1〜v1.0）、EPIC一覧、MVP Definition of Done

## 現在の開発フェーズ

要件定義フェーズ。実装コード・技術スタックはまだ存在しない。新規に技術選定を行う際は、まずユーザーに方針を確認すること。

## タスク管理

* EPIC単位でGitHub Issueを作成し、[GitHub Project](https://github.com/users/hicoichi/projects/2)で管理している。
* 各Issueには `epic` ラベルと優先度ラベル（`P0`/`P1`/`P2`）を付与している。
  * P0 = MVP（v0.1）必須: EPIC-01, 02, 03, 04, 08
  * P1 = 次に実装（v0.2）: EPIC-05, 06, 07
  * P2 = 将来（v0.3以降）: EPIC-09, 10
* Issue本文のユーザーストーリーはチェックリスト形式。実装が進んだらチェックを更新する。

## 実装時の方針

* v0.1（MVP）のスコープは docs/user-story-map.md の「MVP Definition of Done」を満たすことを目標とする。
* MVPスコープ外の機能（候補者情報、開票結果、経路案内など）を先取りして実装しない。
* コーディング規約は [.claude/rules/coding-conventions.md](rules/coding-conventions.md) に従う。
