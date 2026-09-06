// EPIC-05 投票所を確認できる。
import { loadState, saveState, nextId } from "./db.js"
import { getRegion } from "./regions.js"

export function addPollingPlace({ prefecture, city, name, address, openTime = "07:00", closeTime = "20:00" }) {
  const state = loadState()
  const place = {
    id: nextId(state, "polling_places"),
    prefecture,
    city,
    name,
    address,
    open_time: openTime,
    close_time: closeTime,
  }
  state.polling_places.push(place)
  saveState(state)
  return place
}

// 登録地域（自治体）に対応する投票所を確認する。住所・地図・経路・投票時間を含む。
export function getPollingPlaceForRegion(regionId) {
  const state = loadState()
  const region = getRegion(regionId, state)
  const row = state.polling_places.find((p) => p.prefecture === region.prefecture && p.city === region.city)
  if (!row) return null
  const place = { ...row }
  place.map_url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.address)}`
  place.route_url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(place.address)}`
  return place
}
