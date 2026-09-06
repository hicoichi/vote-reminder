// EPIC-08 選挙情報を正確に提供できる（選挙データの基盤）。
import { loadState, saveState, nextId, nowIso } from "./db.js"

export const ELECTION_TYPES = [
  "衆議院議員選挙",
  "参議院議員選挙",
  "都道府県知事選挙",
  "市区町村長選挙",
  "都道府県議会議員選挙",
  "市区町村議会議員選挙",
  "補欠選挙",
  "再選挙",
]

export const STATUSES = ["scheduled", "postponed", "cancelled", "finished"]

function validateDate(value, field) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || Number.isNaN(Date.parse(value))) {
    throw new Error(`${field}の形式が不正です（YYYY-MM-DD）: ${value}`)
  }
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

export function addElection(
  {
    name,
    electionType,
    prefecture,
    city,
    announcementDate,
    voteDate,
    sourceUrl,
    voteStartTime = "07:00",
    voteEndTime = "20:00",
  }
) {
  if (!ELECTION_TYPES.includes(electionType)) {
    throw new Error(`未対応の選挙種別です: ${electionType}`)
  }
  validateDate(announcementDate, "公示日・告示日")
  validateDate(voteDate, "投票日")
  if (!sourceUrl) {
    throw new Error("出典URLは必須です")
  }
  const state = loadState()
  const now = nowIso()
  const election = {
    id: nextId(state, "elections"),
    name,
    election_type: electionType,
    prefecture: prefecture ?? null,
    city: city ?? null,
    announcement_date: announcementDate,
    vote_date: voteDate,
    vote_start_time: voteStartTime,
    vote_end_time: voteEndTime,
    status: "scheduled",
    source_url: sourceUrl,
    source_updated_at: now,
    created_at: now,
    updated_at: now,
  }
  state.elections.push(election)
  saveState(state)
  return election
}

export function getElection(electionId, state = loadState()) {
  const election = state.elections.find((e) => e.id === electionId)
  if (!election) {
    throw new Error(`選挙が見つかりません: id=${electionId}`)
  }
  return election
}

export function updateElection(electionId, { sourceUrl, voteDate = null, announcementDate = null }) {
  const state = loadState()
  const election = getElection(electionId, state)
  if (!sourceUrl) {
    throw new Error("出典URLは必須です")
  }
  if (voteDate !== null) {
    validateDate(voteDate, "投票日")
    election.vote_date = voteDate
  }
  if (announcementDate !== null) {
    validateDate(announcementDate, "公示日・告示日")
    election.announcement_date = announcementDate
  }
  const now = nowIso()
  election.source_url = sourceUrl
  election.source_updated_at = now
  election.updated_at = now
  saveState(state)
  return election
}

export function setElectionStatus(electionId, status) {
  if (!STATUSES.includes(status)) {
    throw new Error(`未対応のステータスです: ${status}`)
  }
  const state = loadState()
  const election = getElection(electionId, state)
  election.status = status
  election.updated_at = nowIso()
  saveState(state)
  return election
}

export function listElections(state = loadState()) {
  return [...state.elections].sort((a, b) => (a.vote_date < b.vote_date ? -1 : 1))
}

// 出典データが一定期間更新されていない、かつ実施予定の選挙を判別する。
export function findStaleElections(days = 30) {
  const state = loadState()
  const threshold = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString()
  return state.elections
    .filter((e) => e.status === "scheduled" && e.source_updated_at < threshold)
    .sort((a, b) => (a.source_updated_at < b.source_updated_at ? -1 : 1))
}

// 選挙データ取得の成否を記録する（取得失敗の検知用）。
export function logFetch(target, success, message = "") {
  const state = loadState()
  state.fetch_logs.push({
    id: nextId(state, "fetch_logs"),
    target,
    success,
    message,
    created_at: nowIso(),
  })
  saveState(state)
}

// 投票日を過ぎた実施予定の選挙を終了扱いにし、通知対象から除外する。
export function finalizePastElections() {
  const state = loadState()
  const todayStr = today()
  const targets = state.elections.filter((e) => e.status === "scheduled" && e.vote_date < todayStr)
  const now = nowIso()
  for (const election of targets) {
    election.status = "finished"
    election.updated_at = now
  }
  saveState(state)
  return targets
}

export function listFetchFailures() {
  return loadState()
    .fetch_logs.filter((f) => !f.success)
    .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
}
