import { beforeEach, describe, expect, it } from "vitest"
import { getSetting, setSetting } from "../notifications.js"
import { registerRegion } from "../regions.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

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
})
