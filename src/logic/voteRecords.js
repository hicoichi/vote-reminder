// EPIC-07 投票済みを記録できる。
import { loadState, saveState, nextId, nowIso } from "./db.js"
import { getElection } from "./elections.js"
import { getRegion } from "./regions.js"

// 「投票した」と記録する。同じ選挙への記録は冪等（二重記録しない）。
export function markVoted(regionId, electionId) {
  const state = loadState()
  getRegion(regionId, state) // 存在確認
  getElection(electionId, state) // 存在確認
  let record = state.vote_records.find((r) => r.region_id === regionId && r.election_id === electionId)
  if (!record) {
    record = {
      id: nextId(state, "vote_records"),
      region_id: regionId,
      election_id: electionId,
      voted_at: nowIso(),
    }
    state.vote_records.push(record)
    saveState(state)
  }
  return record
}

// 投票済みの選挙・過去の投票履歴を確認する。
export function listVotedElections(regionId) {
  const state = loadState()
  return state.vote_records
    .filter((r) => r.region_id === regionId)
    .map((r) => ({ ...getElection(r.election_id, state), voted_at: r.voted_at }))
    .sort((a, b) => (a.voted_at < b.voted_at ? 1 : -1))
}
