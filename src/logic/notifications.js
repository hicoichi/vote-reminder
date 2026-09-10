// EPIC-04 投票日を通知できる。
import { loadState, saveState } from "./db.js"

export const DEFAULT_DAYS_BEFORE = [7, 1, 0]

function parseDaysBefore(value) {
  return value
    .split(",")
    .filter((v) => v !== "")
    .map((v) => Number(v))
}

// 通知設定（地域ごとの共通設定）を取得する。未設定ならシステムデフォルト（有効・7日前/前日/当日）を返す。
export function getSetting(regionId, state = loadState()) {
  const row = state.notification_settings.find((s) => s.region_id === regionId)
  if (row) {
    return { enabled: row.enabled, days_before: parseDaysBefore(row.days_before) }
  }
  return { enabled: true, days_before: [...DEFAULT_DAYS_BEFORE] }
}

// 通知のON/OFF、通知タイミングを変更する。
export function setSetting(regionId, { enabled = null, daysBefore = null } = {}) {
  const state = loadState()
  const current = getSetting(regionId, state)
  const newEnabled = enabled === null ? current.enabled : enabled
  const newDaysBefore = daysBefore === null ? current.days_before : daysBefore
  const existing = state.notification_settings.find((s) => s.region_id === regionId)
  const daysBeforeStr = newDaysBefore.join(",")
  if (existing) {
    existing.enabled = newEnabled
    existing.days_before = daysBeforeStr
  } else {
    state.notification_settings.push({
      region_id: regionId,
      enabled: newEnabled,
      days_before: daysBeforeStr,
    })
  }
  saveState(state)
  return { enabled: newEnabled, days_before: newDaysBefore }
}

// 選挙ごとの個別通知設定を取得する。個別設定がなければnullを返す。
export function getElectionSetting(regionId, electionId, state = loadState()) {
  const row = state.election_notification_settings.find(
    (s) => s.region_id === regionId && s.election_id === electionId
  )
  if (!row) return null
  return { enabled: row.enabled, days_before: parseDaysBefore(row.days_before) }
}

// 選挙ごとの個別通知設定を保存する。
export function setElectionSetting(regionId, electionId, { enabled, daysBefore }) {
  const state = loadState()
  const existing = state.election_notification_settings.find(
    (s) => s.region_id === regionId && s.election_id === electionId
  )
  const daysBeforeStr = daysBefore.join(",")
  if (existing) {
    existing.enabled = enabled
    existing.days_before = daysBeforeStr
  } else {
    state.election_notification_settings.push({
      region_id: regionId,
      election_id: electionId,
      enabled,
      days_before: daysBeforeStr,
    })
  }
  saveState(state)
  return { enabled, days_before: daysBefore }
}

// 選挙に実際に適用される通知設定（個別設定があればそれ、なければ共通設定）を返す。
export function getEffectiveSetting(regionId, electionId, state = loadState()) {
  return getElectionSetting(regionId, electionId, state) ?? getSetting(regionId, state)
}
