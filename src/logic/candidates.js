// EPIC-09 候補者・選挙情報を確認できる。
import { loadState, saveState, nextId } from "./db.js"
import { getElection } from "./elections.js"

export function addCandidate({ electionId, name, party = null, profile = null, sourceUrl = null }) {
  const state = loadState()
  getElection(electionId, state) // 存在確認
  const candidate = {
    id: nextId(state, "candidates"),
    election_id: electionId,
    name,
    party,
    profile,
    source_url: sourceUrl,
  }
  state.candidates.push(candidate)
  saveState(state)
  return candidate
}

export function getCandidate(candidateId, state = loadState()) {
  const candidate = state.candidates.find((c) => c.id === candidateId)
  if (!candidate) {
    throw new Error(`候補者が見つかりません: id=${candidateId}`)
  }
  return candidate
}

export function listCandidates(electionId) {
  return loadState()
    .candidates.filter((c) => c.election_id === electionId)
    .sort((a, b) => a.id - b.id)
}

// 選挙公報を登録・更新する。
export function setGazette(electionId, content, sourceUrl) {
  const state = loadState()
  getElection(electionId, state) // 存在確認
  const existing = state.election_gazettes.find((g) => g.election_id === electionId)
  if (existing) {
    existing.content = content
    existing.source_url = sourceUrl
  } else {
    state.election_gazettes.push({ election_id: electionId, content, source_url: sourceUrl })
  }
  saveState(state)
  return getGazette(electionId)
}

export function getGazette(electionId) {
  const gazette = loadState().election_gazettes.find((g) => g.election_id === electionId)
  return gazette ?? null
}

// 候補者の開票結果を登録・更新する。
export function setResult(candidateId, votes, elected) {
  const state = loadState()
  getCandidate(candidateId, state) // 存在確認
  const existing = state.election_results.find((r) => r.candidate_id === candidateId)
  if (existing) {
    existing.votes = votes
    existing.elected = elected
  } else {
    state.election_results.push({ candidate_id: candidateId, votes, elected })
  }
  saveState(state)
  return state.election_results.find((r) => r.candidate_id === candidateId)
}

// 選挙の開票結果を候補者情報とあわせて確認する。
export function getResults(electionId) {
  const state = loadState()
  const rows = state.candidates
    .filter((c) => c.election_id === electionId)
    .map((c) => {
      const result = state.election_results.find((r) => r.candidate_id === c.id)
      return { ...c, votes: result ? result.votes : null, elected: result ? result.elected : false }
    })
  return rows.sort((a, b) => {
    if (a.votes === null && b.votes === null) return 0
    if (a.votes === null) return 1
    if (b.votes === null) return -1
    return b.votes - a.votes
  })
}
