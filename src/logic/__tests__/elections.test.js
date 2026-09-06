import { beforeEach, describe, expect, it } from "vitest"
import {
  addElection,
  findStaleElections,
  getElection,
  listFetchFailures,
  logFetch,
  setElectionStatus,
  updateElection,
} from "../elections.js"
import { loadState, saveState } from "../db.js"

function addTestElection(overrides = {}) {
  return addElection({
    name: "第50回衆議院議員総選挙",
    electionType: "衆議院議員選挙",
    prefecture: null,
    city: null,
    announcementDate: "2026-10-01",
    voteDate: "2026-10-15",
    sourceUrl: "https://example.jp/election",
    ...overrides,
  })
}

describe("elections", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("選挙を登録して取得できる", () => {
    const election = addTestElection()
    expect(getElection(election.id)).toEqual(election)
  })

  it("未対応の選挙種別は拒否される", () => {
    expect(() => addTestElection({ electionType: "謎の選挙" })).toThrow()
  })

  it("投票日の変更が反映される", () => {
    const election = addTestElection()
    const updated = updateElection(election.id, {
      sourceUrl: "https://example.jp/updated",
      voteDate: "2026-10-22",
    })
    expect(updated.vote_date).toBe("2026-10-22")
    expect(updated.source_url).toBe("https://example.jp/updated")
  })

  it("選挙の中止ステータスが反映される", () => {
    const election = addTestElection()
    const updated = setElectionStatus(election.id, "cancelled")
    expect(updated.status).toBe("cancelled")
  })

  it("出典が古い選挙を判別できる", () => {
    const election = addTestElection()
    const state = loadState()
    const target = state.elections.find((e) => e.id === election.id)
    target.source_updated_at = new Date(Date.now() - 100 * 24 * 60 * 60 * 1000).toISOString()
    saveState(state)
    const stale = findStaleElections(30)
    expect(stale.map((e) => e.id)).toEqual([election.id])
  })

  it("データ取得失敗を記録できる", () => {
    logFetch("soumu.go.jp", false, "timeout")
    const failures = listFetchFailures()
    expect(failures).toHaveLength(1)
    expect(failures[0].target).toBe("soumu.go.jp")
  })
})
