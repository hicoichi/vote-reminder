import { beforeEach, describe, expect, it } from "vitest"
import { deleteRegion, getRegion, registerRegion, updateRegion } from "../regions.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("regions", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("地域を登録して取得できる", async () => {
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    const region = await registerRegion("100-0001")
    expect(region.prefecture).toBe("東京都")
    expect(region.city).toBe("千代田区")
    expect(getRegion(region.id)).toEqual(region)
  })

  it("地域の郵便番号を変更できる", async () => {
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    const region = await registerRegion("1000001")
    const updated = await updateRegion(region.id, "100-0001")
    expect(updated.zipcode).toBe("1000001")
  })

  it("地域を削除できる", async () => {
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    const region = await registerRegion("1000001")
    deleteRegion(region.id)
    expect(() => getRegion(region.id)).toThrow()
  })

  it("郵便番号の形式が不正な場合はエラーになる", async () => {
    await expect(registerRegion("abc")).rejects.toThrow()
  })
})
