// EPIC-04 投票日を通知できる。
import { loadState, saveState, nextId, nowIso } from "./db.js"
import { ELECTION_TYPES, finalizePastElections } from "./elections.js"
import { listElectionsForRegion } from "./regionElections.js"

export const DEFAULT_DAYS_BEFORE = [7, 1, 0]
export const ALL_TYPES = "*"

function parseDaysBefore(value) {
  return value
    .split(",")
    .filter((v) => v !== "")
    .map((v) => Number(v))
}

// 選挙種別ごとの通知設定を取得する。個別設定がなければ全種別共通設定、
// それもなければシステムデフォルト（有効・7日前/前日/当日）を返す。
export function getSetting(regionId, electionType, state = loadState()) {
  for (const targetType of [electionType, ALL_TYPES]) {
    const row = state.notification_settings.find(
      (s) => s.region_id === regionId && s.election_type === targetType
    )
    if (row) {
      return { enabled: row.enabled, days_before: parseDaysBefore(row.days_before) }
    }
  }
  return { enabled: true, days_before: [...DEFAULT_DAYS_BEFORE] }
}

// 通知のON/OFF、通知タイミング、選挙種別ごとの設定を変更する。
export function setSetting(regionId, electionType, { enabled = null, daysBefore = null } = {}) {
  if (electionType !== ALL_TYPES && !ELECTION_TYPES.includes(electionType)) {
    throw new Error(`未対応の選挙種別です: ${electionType}`)
  }
  const state = loadState()
  const current = getSetting(regionId, electionType, state)
  const newEnabled = enabled === null ? current.enabled : enabled
  const newDaysBefore = daysBefore === null ? current.days_before : daysBefore
  const existing = state.notification_settings.find(
    (s) => s.region_id === regionId && s.election_type === electionType
  )
  const daysBeforeStr = newDaysBefore.join(",")
  if (existing) {
    existing.enabled = newEnabled
    existing.days_before = daysBeforeStr
  } else {
    state.notification_settings.push({
      region_id: regionId,
      election_type: electionType,
      enabled: newEnabled,
      days_before: daysBeforeStr,
    })
  }
  saveState(state)
  return { enabled: newEnabled, days_before: newDaysBefore }
}

// 通知タイミングが到来した選挙について通知を作成する（未送信分のみ）。
export function notifyDue(regionId) {
  finalizePastElections()
  const state = loadState()
  const todayStr = new Date().toISOString().slice(0, 10)
  const todayDate = new Date(todayStr)
  const created = []
  for (const election of listElectionsForRegion(regionId)) {
    const setting = getSetting(regionId, election.election_type, state)
    if (!setting.enabled) continue
    const voteDate = new Date(election.vote_date)
    const daysUntil = Math.round((voteDate - todayDate) / (24 * 60 * 60 * 1000))
    if (daysUntil < 0 || !setting.days_before.includes(daysUntil)) continue
    const notifyType = `d${daysUntil}`
    const existing = state.notifications.find(
      (n) => n.region_id === regionId && n.election_id === election.id && n.notify_type === notifyType
    )
    if (existing) continue
    const message = `【投票日通知】${election.name}の投票日まであと${daysUntil}日です（投票日: ${election.vote_date}）`
    const now = nowIso()
    const notification = {
      id: nextId(state, "notifications"),
      region_id: regionId,
      election_id: election.id,
      notify_type: notifyType,
      sent_at: now,
      message,
    }
    state.notifications.push(notification)
    created.push(notification)
  }
  saveState(state)
  return created
}

export function listNotifications(regionId) {
  return loadState()
    .notifications.filter((n) => n.region_id === regionId)
    .sort((a, b) => (a.sent_at < b.sent_at ? 1 : -1))
}
