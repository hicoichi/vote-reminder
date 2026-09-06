import { beforeEach, describe, expect, it } from "vitest"
import { addElection, getElection } from "../elections.js"
import { ALL_TYPES, getSetting, notifyDue, setSetting } from "../notifications.js"
import { registerRegion } from "../regions.js"
import { isoDateAfterDays, mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

function addTestElection(daysUntilVote, overrides = {}) {
  return addElection({
    name: "テスト選挙",
    electionType: "衆議院議員選挙",
    prefecture: null,
    city: null,
    announcementDate: isoDateAfterDays(0),
    voteDate: isoDateAfterDays(daysUntilVote),
    sourceUrl: "https://example.jp/election",
    ...overrides,
  })
}

describe("notifications", () => {
  let region

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
  })

  it("デフォルト設定は有効・7/1/0日前", () => {
    const setting = getSetting(region.id, "衆議院議員選挙")
    expect(setting).toEqual({ enabled: true, days_before: [7, 1, 0] })
  })

  it("7日前に通知を作成する", () => {
    const election = addTestElection(7)
    const created = notifyDue(region.id)
    expect(created).toHaveLength(1)
    expect(created[0].election_id).toBe(election.id)
    expect(created[0].notify_type).toBe("d7")
  })

  it("同じ通知は重複作成しない", () => {
    addTestElection(7)
    notifyDue(region.id)
    const second = notifyDue(region.id)
    expect(second).toEqual([])
  })

  it("設定されていないタイミングはスキップする", () => {
    addTestElection(3)
    expect(notifyDue(region.id)).toEqual([])
  })

  it("通知を無効化すると通知されない", () => {
    addTestElection(0)
    setSetting(region.id, ALL_TYPES, { enabled: false })
    expect(notifyDue(region.id)).toEqual([])
  })

  it("選挙種別ごとに通知タイミングを変更できる", () => {
    addTestElection(3, { electionType: "参議院議員選挙" })
    setSetting(region.id, "参議院議員選挙", { daysBefore: [3] })
    expect(notifyDue(region.id)).toHaveLength(1)
  })

  it("過去の選挙は終了扱いになり通知対象から除外される", () => {
    const election = addTestElection(-1)
    notifyDue(region.id)
    expect(getElection(election.id).status).toBe("finished")
  })
})
