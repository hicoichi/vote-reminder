import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import { getEffectiveSetting, getElectionSetting, getSetting, setElectionSetting, setSetting } from "../notifications.js"
import { registerRegion } from "../regions.js"
import { isoDateAfterDays, mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("notifications", () => {
  let region

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
  })

  it("デフォルト設定は有効・7/1/0日前", () => {
    const setting = getSetting(region.id)
    expect(setting).toEqual({ enabled: true, days_before: [7, 1, 0] })
  })

  it("設定を変更できる", () => {
    setSetting(region.id, { enabled: false, daysBefore: [3] })
    expect(getSetting(region.id)).toEqual({ enabled: false, days_before: [3] })
  })

  it("選挙ごとの個別設定がなければnullを返す", () => {
    const election = addElection({
      name: "テスト選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: isoDateAfterDays(0),
      voteDate: isoDateAfterDays(10),
      sourceUrl: "https://example.jp/election",
    })
    expect(getElectionSetting(region.id, election.id)).toBeNull()
  })

  it("選挙ごとに個別設定を保存・取得できる", () => {
    const election = addElection({
      name: "テスト選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: isoDateAfterDays(0),
      voteDate: isoDateAfterDays(10),
      sourceUrl: "https://example.jp/election",
    })
    setElectionSetting(region.id, election.id, { enabled: false, daysBefore: [14, 3] })
    expect(getElectionSetting(region.id, election.id)).toEqual({ enabled: false, days_before: [14, 3] })
  })

  it("個別設定がある場合はそれを優先し、なければ共通設定を適用する", () => {
    const election = addElection({
      name: "テスト選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: isoDateAfterDays(0),
      voteDate: isoDateAfterDays(10),
      sourceUrl: "https://example.jp/election",
    })
    setSetting(region.id, { enabled: true, daysBefore: [7, 1, 0] })
    expect(getEffectiveSetting(region.id, election.id)).toEqual({ enabled: true, days_before: [7, 1, 0] })

    setElectionSetting(region.id, election.id, { enabled: false, daysBefore: [14] })
    expect(getEffectiveSetting(region.id, election.id)).toEqual({ enabled: false, days_before: [14] })
  })
})
