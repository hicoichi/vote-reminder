<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { registerRegion, listRegions, deleteRegion } from "../logic/regions.js"

const router = useRouter()
const zipcode = ref("")
const errorMessage = ref("")
const submitting = ref(false)
const regions = ref(listRegions())

async function onRegister() {
  errorMessage.value = ""
  submitting.value = true
  try {
    const region = await registerRegion(zipcode.value)
    zipcode.value = ""
    regions.value = listRegions()
    router.push(`/region/${region.id}`)
  } catch (e) {
    errorMessage.value = e.message
  } finally {
    submitting.value = false
  }
}

function onDelete(regionId) {
  deleteRegion(regionId)
  regions.value = listRegions()
}
</script>

<template>
  <section>
    <h2>地域を登録する</h2>
    <p>郵便番号を登録すると、自分に関係する選挙が自動で判定されます。</p>
    <form @submit.prevent="onRegister" style="display: flex; gap: 8px; align-items: flex-end;">
      <div class="field" style="margin-bottom: 0;">
        <label for="zipcode">郵便番号</label>
        <input id="zipcode" v-model="zipcode" placeholder="100-0001" required />
      </div>
      <button type="submit" :disabled="submitting">{{ submitting ? "登録中…" : "登録する" }}</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </section>

  <section>
    <h2>登録済みの地域</h2>
    <p v-if="regions.length === 0">まだ地域が登録されていません。</p>
    <table v-else>
      <thead>
        <tr>
          <th>郵便番号</th>
          <th>住所</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="region in regions" :key="region.id">
          <td>{{ region.zipcode }}</td>
          <td>{{ region.prefecture }}{{ region.city }}{{ region.town }}</td>
          <td style="display: flex; gap: 8px;">
            <router-link :to="`/region/${region.id}`">確認する</router-link>
            <button type="button" class="secondary" @click="onDelete(region.id)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
