// EPIC-01 地域を登録できる。
import { loadState, saveState, nextId, nowIso } from "./db.js"

const ZIPCLOUD_URL = "https://zipcloud.ibsnet.co.jp/api/search"

function normalizeZipcode(zipcode) {
  const digits = zipcode.replace(/-/g, "").trim()
  if (!/^\d{7}$/.test(digits)) {
    throw new Error(`郵便番号の形式が不正です: ${zipcode}`)
  }
  return digits
}

// zipcloud APIはCORSに対応していないため、JSONPで呼び出す。
function requestJsonp(url) {
  return new Promise((resolve, reject) => {
    const callbackName = `__zipcloudCallback${Date.now()}${Math.floor(Math.random() * 1e6)}`
    const script = document.createElement("script")
    const cleanup = () => {
      delete window[callbackName]
      script.remove()
    }
    window[callbackName] = (body) => {
      cleanup()
      resolve(body)
    }
    script.onerror = () => {
      cleanup()
      reject(new Error("郵便番号検索APIの呼び出しに失敗しました"))
    }
    script.src = `${url}${url.includes("?") ? "&" : "?"}callback=${callbackName}`
    document.head.appendChild(script)
  })
}

export async function lookupMunicipality(zipcode) {
  const digits = normalizeZipcode(zipcode)
  const body = await requestJsonp(`${ZIPCLOUD_URL}?zipcode=${digits}`)
  const results = body.results
  if (!results || results.length === 0) {
    throw new Error(`郵便番号に該当する住所が見つかりません: ${zipcode}`)
  }
  const top = results[0]
  return {
    prefecture: top.address1,
    city: top.address2,
    town: top.address3,
  }
}

export async function registerRegion(zipcode) {
  const municipality = await lookupMunicipality(zipcode)
  const state = loadState()
  const now = nowIso()
  const region = {
    id: nextId(state, "regions"),
    zipcode: normalizeZipcode(zipcode),
    prefecture: municipality.prefecture,
    city: municipality.city,
    town: municipality.town,
    created_at: now,
    updated_at: now,
  }
  state.regions.push(region)
  saveState(state)
  return region
}

export function getRegion(regionId, state = loadState()) {
  const region = state.regions.find((r) => r.id === regionId)
  if (!region) {
    throw new Error(`地域が見つかりません: id=${regionId}`)
  }
  return region
}

export async function updateRegion(regionId, zipcode) {
  const state = loadState()
  const region = getRegion(regionId, state)
  const municipality = await lookupMunicipality(zipcode)
  const now = nowIso()
  region.zipcode = normalizeZipcode(zipcode)
  region.prefecture = municipality.prefecture
  region.city = municipality.city
  region.town = municipality.town
  region.updated_at = now
  saveState(state)
  return region
}

export function deleteRegion(regionId) {
  const state = loadState()
  getRegion(regionId, state) // 存在確認
  state.regions = state.regions.filter((r) => r.id !== regionId)
  saveState(state)
}

export function listRegions() {
  return loadState().regions
}
