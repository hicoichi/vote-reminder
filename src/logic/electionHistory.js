// EPIC-10 選挙履歴を確認できる。
import { getResults } from "./candidates.js"
import { listAllElectionsForRegion } from "./regionElections.js"
import { listVotedElections } from "./voteRecords.js"

// 登録地域に関係する過去の選挙を一覧で確認する。
export function listPastElections(regionId) {
  const today = new Date().toISOString().slice(0, 10)
  const past = listAllElectionsForRegion(regionId).filter((e) => e.vote_date < today)
  return past.sort((a, b) => (a.vote_date < b.vote_date ? 1 : -1))
}

// 過去の選挙の開票結果を確認する。
export function getPastElectionResults(electionId) {
  return getResults(electionId)
}

// 自分の投票済み履歴を確認する。
export function listVotingHistory(regionId) {
  return listVotedElections(regionId)
}
