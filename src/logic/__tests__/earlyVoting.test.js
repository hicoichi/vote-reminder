import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import {
  addEarlyVotingPlace,
  deleteEarlyVotingPlace,
  listEarlyVotingPlaces,
  listEarlyVotingPlacesForRegion,
  updateEarlyVotingPlace,
} from "../earlyVoting.js"
import { registerRegion } from "../regions.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("earlyVoting", () => {
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

  it("関係する選挙の期日前投票所を一覧できる", () => {
    addEarlyVotingPlace({
      electionId: election.id,
      name: "千代田区役所",
      address: "東京都千代田区九段南1-2-1",
      periodStart: "2026-10-05",
      periodEnd: "2026-10-14",
    })
    const places = listEarlyVotingPlacesForRegion(region.id, election.id)
    expect(places).toHaveLength(1)
    expect(places[0].period_start).toBe("2026-10-05")
    expect(places[0].open_time).toBe("08:30")
  })

  it("地域に関係しない選挙は拒否される", () => {
    const other = addElection({
      name: "他地域の選挙",
      electionType: "市区町村長選挙",
      prefecture: "大阪府",
      city: "大阪市",
      announcementDate: "2026-10-01",
      voteDate: "2026-10-15",
      sourceUrl: "https://example.jp/other",
    })
    expect(() => listEarlyVotingPlacesForRegion(region.id, other.id)).toThrow()
  })

  it("期日前投票所を更新できる", () => {
    const place = addEarlyVotingPlace({
      electionId: election.id,
      name: "千代田区役所",
      address: "東京都千代田区九段南1-2-1",
      periodStart: "2026-10-05",
      periodEnd: "2026-10-14",
    })
    const updated = updateEarlyVotingPlace(place.id, {
      electionId: election.id,
      name: "千代田区役所（別館）",
      address: "東京都千代田区九段南1-2-2",
      periodStart: "2026-10-06",
      periodEnd: "2026-10-14",
      openTime: "09:00",
      closeTime: "18:00",
    })
    expect(updated.name).toBe("千代田区役所（別館）")
    expect(updated.period_start).toBe("2026-10-06")
  })

  it("期日前投票所を削除できる", () => {
    const place = addEarlyVotingPlace({
      electionId: election.id,
      name: "千代田区役所",
      address: "東京都千代田区九段南1-2-1",
      periodStart: "2026-10-05",
      periodEnd: "2026-10-14",
    })
    deleteEarlyVotingPlace(place.id)
    expect(listEarlyVotingPlaces()).toEqual([])
  })
})
