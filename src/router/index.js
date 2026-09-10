import { createRouter, createWebHashHistory } from "vue-router"
import Home from "../views/Home.vue"
import RegionDashboard from "../views/RegionDashboard.vue"
import AdminData from "../views/AdminData.vue"
import { listRegions } from "../logic/regions.js"

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", name: "home", component: Home },
    { path: "/region/:id", name: "region-dashboard", component: RegionDashboard, props: true },
    { path: "/admin", name: "admin", component: AdminData },
  ],
})

// 地域登録済みならトップページを概要画面へ転送する（本アプリは地域を1つだけ扱う）。
router.beforeEach((to) => {
  if (to.path === "/") {
    const [region] = listRegions()
    if (region) {
      return `/region/${region.id}`
    }
  }
})

export default router
