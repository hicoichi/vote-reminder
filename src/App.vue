<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import { listRegions } from "./logic/regions.js"

const route = useRoute()
// 画面遷移のたびに再評価し、地域登録済みなら概要画面へ、未登録なら登録画面へ振り分ける。
const overviewLink = computed(() => {
  void route.fullPath
  const [region] = listRegions()
  return region ? `/region/${region.id}` : "/"
})
</script>

<template>
  <div id="app-shell" style="max-width: 900px; margin: 0 auto; padding: 16px;">
    <header style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px;">
      <h1 style="font-size: 1.4em; margin: 0;">vote-reminder</h1>
      <nav style="display: flex; gap: 12px;">
        <router-link :to="overviewLink">概要</router-link>
        <router-link to="/admin">選挙データ管理</router-link>
      </nav>
    </header>
    <router-view />
  </div>
</template>
