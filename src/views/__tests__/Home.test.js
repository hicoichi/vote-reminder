// 実ブラウザでの起動確認が困難な実行環境のため、Vueコンポーネントの結合動作を
// jsdom上で検証する（郵便番号入力→登録→概要画面への遷移までの一連の流れ）。
import { mount, flushPromises } from "@vue/test-utils"
import { beforeEach, describe, expect, it } from "vitest"
import { createMemoryHistory, createRouter } from "vue-router"
import Home from "../Home.vue"
import RegionDashboard from "../RegionDashboard.vue"
import { mockZipcloudResponse, ZIPCLOUD_RESPONSE } from "../../logic/__tests__/testHelpers.js"

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: Home },
      { path: "/region/:id", component: RegionDashboard, props: true },
    ],
  })
}

describe("Home.vue", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("郵便番号を登録すると概要画面へ遷移する", async () => {
    mockZipcloudResponse(ZIPCLOUD_RESPONSE)
    const router = createTestRouter()
    router.push("/")
    await router.isReady()
    const wrapper = mount(Home, { global: { plugins: [router] } })

    await wrapper.find("#zipcode").setValue("100-0001")
    await wrapper.find("form").trigger("submit.prevent")
    await flushPromises()

    expect(router.currentRoute.value.path).toBe("/region/1")
  })
})
