// テスト専用ヘルパー。zipcloud APIへのJSONP呼び出しをjsdom上でスタブする。
import { vi } from "vitest"

export function mockZipcloudResponse(response) {
  const originalCreateElement = document.createElement.bind(document)
  vi.spyOn(document, "createElement").mockImplementation((tag) => {
    const el = originalCreateElement(tag)
    if (tag === "script") {
      Object.defineProperty(el, "src", {
        set(value) {
          const match = value.match(/callback=([^&]+)/)
          const callbackName = match[1]
          Promise.resolve().then(() => window[callbackName]?.(response))
        },
      })
    }
    return el
  })
}

export const ZIPCLOUD_RESPONSE = {
  results: [{ address1: "東京都", address2: "千代田区", address3: "千代田" }],
}

export function isoDateAfterDays(days) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}
