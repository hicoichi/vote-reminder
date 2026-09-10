<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { registerRegion } from "../logic/regions.js"

const router = useRouter()
const zipcode = ref("")
const errorMessage = ref("")
const submitting = ref(false)

async function onRegister() {
  errorMessage.value = ""
  submitting.value = true
  try {
    const region = await registerRegion(zipcode.value)
    router.push(`/region/${region.id}`)
  } catch (e) {
    errorMessage.value = e.message
  } finally {
    submitting.value = false
  }
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
</template>
