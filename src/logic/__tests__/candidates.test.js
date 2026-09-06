import { beforeEach, describe, expect, it } from "vitest"
import { addCandidate, getGazette, getResults, listCandidates, setGazette, setResult } from "../candidates.js"
import { addElection } from "../elections.js"

describe("candidates", () => {
  let election

  beforeEach(() => {
    localStorage.clear()
    election = addElection({
      name: "テスト選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: "2026-10-01",
      voteDate: "2026-10-15",
      sourceUrl: "https://example.jp/election",
    })
  })

  it("候補者を登録して一覧できる", () => {
    addCandidate({
      electionId: election.id,
      name: "候補者A",
      party: "無所属",
      sourceUrl: "https://example.jp/candidate-a",
    })
    const result = listCandidates(election.id)
    expect(result).toHaveLength(1)
    expect(result[0].name).toBe("候補者A")
    expect(result[0].source_url).toBe("https://example.jp/candidate-a")
  })

  it("選挙公報を登録・確認できる", () => {
    expect(getGazette(election.id)).toBeNull()
    setGazette(election.id, "公報の内容", "https://example.jp/gazette")
    expect(getGazette(election.id).content).toBe("公報の内容")
  })

  it("開票結果は得票数の降順に並ぶ", () => {
    const a = addCandidate({ electionId: election.id, name: "A" })
    const b = addCandidate({ electionId: election.id, name: "B" })
    setResult(a.id, 100, false)
    setResult(b.id, 200, true)
    const results = getResults(election.id)
    expect(results.map((r) => r.name)).toEqual(["B", "A"])
    expect(results[0].elected).toBe(true)
  })
})
