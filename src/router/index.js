import { createRouter, createWebHashHistory } from "vue-router"
import Home from "../views/Home.vue"
import RegionDashboard from "../views/RegionDashboard.vue"
import AdminData from "../views/AdminData.vue"

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", name: "home", component: Home },
    { path: "/region/:id", name: "region-dashboard", component: RegionDashboard, props: true },
    { path: "/admin", name: "admin", component: AdminData },
  ],
})

export default router
