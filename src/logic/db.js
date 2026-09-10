// ブラウザのlocalStorageを使った簡易データストア（SQLiteの代替）。
// テーブル = 配列、主キー採番はテーブルごとのカウンタで管理する。
const STORAGE_KEY = "vote-reminder-db"

const TABLES = [
  "regions",
  "elections",
  "fetch_logs",
  "polling_places",
  "early_voting_places",
  "candidates",
  "election_gazettes",
  "election_results",
  "notification_settings",
  "election_notification_settings",
  "vote_records",
]

function emptyState() {
  const state = { nextId: {} }
  for (const table of TABLES) {
    state[table] = []
    state.nextId[table] = 1
  }
  return state
}

export function loadState() {
  const raw = localStorage.getItem(STORAGE_KEY)
  const state = raw ? JSON.parse(raw) : emptyState()
  for (const table of TABLES) {
    if (!state[table]) state[table] = []
    if (!state.nextId) state.nextId = {}
    if (!state.nextId[table]) state.nextId[table] = 1
  }
  return state
}

export function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function nextId(state, table) {
  const id = state.nextId[table]
  state.nextId[table] += 1
  return id
}

export function nowIso() {
  return new Date().toISOString()
}
