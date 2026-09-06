// EPIC-06 期日前投票を確認できる。
import { loadState, saveState, nextId } from "./db.js"
import { getElection } from "./elections.js"
import { listElectionsForRegion } from "./regionElections.js"

export function addEarlyVotingPlace({
  electionId,
  name,
  address,
  periodStart,
  periodEnd,
  openTime = "08:30",
  closeTime = "20:00",
}) {
  const state = loadState()
  getElection(electionId, state) // 存在確認
  const place = {
    id: nextId(state, "early_voting_places"),
    election_id: electionId,
    name,
    address,
    period_start: periodStart,
    period_end: periodEnd,
    open_time: openTime,
    close_time: closeTime,
  }
  state.early_voting_places.push(place)
  saveState(state)
  return place
}

// 登録地域に関係する選挙について、期日前投票の期間・投票所・住所・受付時間を確認する。
export function listEarlyVotingPlacesForRegion(regionId, electionId) {
  const relevantIds = new Set(listElectionsForRegion(regionId).map((e) => e.id))
  if (!relevantIds.has(electionId)) {
    throw new Error(`この選挙は指定地域に関係しません: election_id=${electionId}`)
  }
  return loadState()
    .early_voting_places.filter((p) => p.election_id === electionId)
    .sort((a, b) => (a.period_start < b.period_start ? -1 : 1))
}
