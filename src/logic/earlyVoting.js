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

export function getEarlyVotingPlace(placeId, state = loadState()) {
  const place = state.early_voting_places.find((p) => p.id === placeId)
  if (!place) {
    throw new Error(`期日前投票所が見つかりません: id=${placeId}`)
  }
  return place
}

// 管理画面用に、選挙に紐づく期日前投票所を全件確認する（地域による絞り込みなし）。
export function listEarlyVotingPlaces() {
  return [...loadState().early_voting_places].sort((a, b) => (a.period_start < b.period_start ? -1 : 1))
}

export function updateEarlyVotingPlace(placeId, { electionId, name, address, periodStart, periodEnd, openTime, closeTime }) {
  const state = loadState()
  const place = getEarlyVotingPlace(placeId, state)
  getElection(electionId, state) // 存在確認
  place.election_id = electionId
  place.name = name
  place.address = address
  place.period_start = periodStart
  place.period_end = periodEnd
  place.open_time = openTime
  place.close_time = closeTime
  saveState(state)
  return place
}

export function deleteEarlyVotingPlace(placeId) {
  const state = loadState()
  getEarlyVotingPlace(placeId, state) // 存在確認
  state.early_voting_places = state.early_voting_places.filter((p) => p.id !== placeId)
  saveState(state)
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
