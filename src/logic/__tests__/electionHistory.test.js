import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import { listPastElections, listVotingHistory } from "../electionHistory.js"
import { registerRegion } from "../regions.js"
import { markVoted } from "../voteRecords.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("electionHistory", () => {
  let region

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
  })

  it("実施予定の選挙は過去の選挙一覧から除外される", () => {
    const past = addElection({
      name: "過去の選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: "2020-10-01",
      voteDate: "2020-10-15",
      sourceUrl: "https://example.jp/past",
    })
    addElection({
      name: "未来の選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: "2099-01-01",
      voteDate: "2099-01-15",
      sourceUrl: "https://example.jp/future",
    })
    const result = listPastElections(region.id)
    expect(result.map((e) => e.id)).toEqual([past.id])
  })

  it("投票履歴には投票記録の選挙が反映される", () => {
    const election = addElection({
      name: "過去の選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: "2020-10-01",
      voteDate: "2020-10-15",
      sourceUrl: "https://example.jp/past",
    })
    markVoted(region.id, election.id)
    const result = listVotingHistory(region.id)
    expect(result.map((e) => e.id)).toEqual([election.id])
  })
})
