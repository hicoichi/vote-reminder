import { beforeEach, describe, expect, it } from "vitest"
import {
  addPollingPlace,
  deletePollingPlace,
  getPollingPlaceForRegion,
  listPollingPlaces,
  updatePollingPlace,
} from "../pollingPlaces.js"
import { registerRegion } from "../regions.js"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "./testHelpers.js"

describe("pollingPlaces", () => {
  let region

  beforeEach(async () => {
    localStorage.clear()
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    region = await registerRegion("100-0001")
  })

  it("投票所が未登録ならnullを返す", () => {
    expect(getPollingPlaceForRegion(region.id)).toBeNull()
  })

  it("地図・経路つきの投票所情報を取得できる", () => {
    addPollingPlace({
      prefecture: "東京都",
      city: "千代田区",
      name: "千代田区役所投票所",
      address: "東京都千代田区九段南1-2-1",
    })
    const place = getPollingPlaceForRegion(region.id)
    expect(place.name).toBe("千代田区役所投票所")
    expect(place.map_url).toContain("maps/search")
    expect(place.route_url).toContain("maps/dir")
    expect(place.open_time).toBe("07:00")
    expect(place.close_time).toBe("20:00")
  })

  it("投票所を更新できる", () => {
    const place = addPollingPlace({
      prefecture: "東京都",
      city: "千代田区",
      name: "千代田区役所投票所",
      address: "東京都千代田区九段南1-2-1",
    })
    const updated = updatePollingPlace(place.id, {
      prefecture: "東京都",
      city: "千代田区",
      name: "千代田区役所投票所（別館）",
      address: "東京都千代田区九段南1-2-2",
      openTime: "08:00",
      closeTime: "19:00",
    })
    expect(updated.name).toBe("千代田区役所投票所（別館）")
    expect(updated.open_time).toBe("08:00")
  })

  it("投票所を削除できる", () => {
    const place = addPollingPlace({
      prefecture: "東京都",
      city: "千代田区",
      name: "千代田区役所投票所",
      address: "東京都千代田区九段南1-2-1",
    })
    deletePollingPlace(place.id)
    expect(listPollingPlaces()).toEqual([])
  })
})
