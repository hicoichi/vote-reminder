// EPIC-02 自分に関係する選挙を取得できる。
import { loadState } from "./db.js"
import { getRegion } from "./regions.js"
import { finalizePastElections, listElections } from "./elections.js"

function matchesRegion(election, region) {
  if (election.prefecture !== null && election.prefecture !== region.prefecture) return false
  if (election.city !== null && election.city !== region.city) return false
  return true
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

// ステータスを問わず、登録地域（自治体・都道府県）に紐づく選挙を取得する。
export function listAllElectionsForRegion(regionId) {
  finalizePastElections()
  const state = loadState()
  const region = getRegion(regionId, state)
  return listElections(state).filter((e) => matchesRegion(e, region))
}

// 登録地域（自治体・都道府県）に紐づく実施予定の選挙を取得する。
export function listElectionsForRegion(regionId, electionType = null) {
  let result = listAllElectionsForRegion(regionId).filter((e) => e.status === "scheduled")
  if (electionType !== null) {
    result = result.filter((e) => e.election_type === electionType)
  }
  return result
}

// 登録地域における次回の選挙を判定する。
export function nextElectionForRegion(regionId) {
  const todayStr = today()
  const upcoming = listElectionsForRegion(regionId).filter((e) => e.vote_date >= todayStr)
  return upcoming.length > 0 ? upcoming[0] : null
}
