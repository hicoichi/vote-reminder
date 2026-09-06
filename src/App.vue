<script setup>
</script>

<template>
  <div id="app-shell" style="max-width: 900px; margin: 0 auto; padding: 16px;">
    <header style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px;">
      <h1 style="font-size: 1.4em; margin: 0;">vote-reminder</h1>
      <nav style="display: flex; gap: 12px;">
        <router-link to="/">地域選択</router-link>
        <router-link to="/admin">選挙データ管理</router-link>
      </nav>
    </header>
    <router-view />
  </div>
</template>
