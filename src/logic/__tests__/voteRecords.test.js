import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import { registerRegion } from "../regions.js"
import { listVotedElections, markVoted } from "../voteRecords.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("voteRecords", () => {
  let region
  let election

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
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

  it("投票済みを記録して一覧に表示される", () => {
    markVoted(region.id, election.id)
    const voted = listVotedElections(region.id)
    expect(voted).toHaveLength(1)
    expect(voted[0].id).toBe(election.id)
  })

  it("投票記録は冪等である", () => {
    markVoted(region.id, election.id)
    markVoted(region.id, election.id)
    expect(listVotedElections(region.id)).toHaveLength(1)
  })

  it("記録がなければ空配列を返す", () => {
    expect(listVotedElections(region.id)).toEqual([])
  })
})
