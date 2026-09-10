import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import { listElectionsForRegion, nextElectionForRegion } from "../regionElections.js"
import { registerRegion } from "../regions.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

function addTestElection(overrides = {}) {
  return addElection({
    name: "テスト選挙",
    electionType: "衆議院議員選挙",
    prefecture: null,
    city: null,
    announcementDate: "2026-10-01",
    voteDate: "2026-10-15",
    sourceUrl: "https://example.jp/election",
    ...overrides,
  })
}

describe("regionElections", () => {
  let region

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
  })

  it("全国規模の選挙はどの地域にも該当する", () => {
    const election = addTestElection()
    const result = listElectionsForRegion(region.id)
    expect(result.map((e) => e.id)).toEqual([election.id])
  })

  it("都道府県レベルの選挙は都道府県の一致が必要", () => {
    addTestElection({ electionType: "都道府県知事選挙", prefecture: "大阪府", city: null })
    expect(listElectionsForRegion(region.id)).toEqual([])
  })

  it("市区町村レベルの選挙は市区町村の一致が必要", () => {
    const election = addTestElection({ electionType: "市区町村長選挙", prefecture: "東京都", city: "千代田区" })
    const result = listElectionsForRegion(region.id)
    expect(result.map((e) => e.id)).toEqual([election.id])
  })

  it("選挙種別で絞り込める", () => {
    addTestElection({ electionType: "衆議院議員選挙" })
    addTestElection({ electionType: "参議院議員選挙", voteDate: "2026-11-01" })
    const result = listElectionsForRegion(region.id, "参議院議員選挙")
    expect(result).toHaveLength(1)
    expect(result[0].election_type).toBe("参議院議員選挙")
  })

  it("直近の次回選挙を選ぶ", () => {
    addTestElection({ voteDate: "2099-01-01" })
    const nearer = addTestElection({ voteDate: "2098-06-01" })
    const result = nextElectionForRegion(region.id)
    expect(result.id).toBe(nearer.id)
  })

  it("投票日を過ぎた選挙は一覧から除外される", () => {
    addTestElection({ voteDate: "2020-01-01" })
    expect(listElectionsForRegion(region.id)).toEqual([])
  })
})
