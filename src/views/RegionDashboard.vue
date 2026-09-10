<script setup>
import { computed, ref, watch } from "vue"
import { getRegion } from "../logic/regions.js"
import { listElectionsForRegion, nextElectionForRegion } from "../logic/regionElections.js"
import { getElectionDetail } from "../logic/electionDetail.js"
import { DEFAULT_DAYS_BEFORE, getSetting, setSetting } from "../logic/notifications.js"
import { getPollingPlaceForRegion } from "../logic/pollingPlaces.js"
import { listEarlyVotingPlacesForRegion } from "../logic/earlyVoting.js"
import { listVotedElections, markVoted } from "../logic/voteRecords.js"

const props = defineProps({ id: { type: String, required: true } })
const regionId = computed(() => Number(props.id))
const region = ref(null)
const loadError = ref("")

const tabs = [
  { id: "overview", label: "概要" },
  { id: "notifications", label: "通知" },
  { id: "voteRecords", label: "投票記録" },
]
const activeTab = ref("overview")

function reloadRegion() {
  try {
    region.value = getRegion(regionId.value)
    loadError.value = ""
  } catch (e) {
    region.value = null
    loadError.value = e.message
  }
}
watch(regionId, reloadRegion, { immediate: true })
watch(regionId, () => { activeTab.value = "overview" })

const WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]
function formatVoteDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}（${WEEKDAYS[d.getDay()]}）`
}

// --- 対象の選挙（投票記録タブで利用） ---
const selectedElectionId = ref("")
watch(regionId, () => { selectedElectionId.value = "" })

// --- 自分に関係する選挙（投票日順） ---
const electionsForRegion = computed(() => listElectionsForRegion(regionId.value))
const nextElection = computed(() => nextElectionForRegion(regionId.value))
const nextElectionDetail = computed(() => (nextElection.value ? getElectionDetail(nextElection.value.id) : null))
const otherElections = computed(() =>
  electionsForRegion.value.filter((e) => !nextElection.value || e.id !== nextElection.value.id)
)

// --- 通知設定（地域共通） ---
const notifySettingForm = ref({ enabled: true, daysBefore: DEFAULT_DAYS_BEFORE.join(",") })
function loadNotifySetting() {
  const setting = getSetting(regionId.value)
  notifySettingForm.value = { enabled: setting.enabled, daysBefore: setting.days_before.join(",") }
}
watch(regionId, loadNotifySetting, { immediate: true })
function saveNotifySetting() {
  setSetting(regionId.value, {
    enabled: notifySettingForm.value.enabled,
    daysBefore: notifySettingForm.value.daysBefore
      .split(",")
      .filter((v) => v.trim() !== "")
      .map((v) => Number(v)),
  })
  loadNotifySetting()
}

// --- 投票所（当日） ---
const pollingPlace = computed(() => getPollingPlaceForRegion(regionId.value))

// --- 期日前投票所（関係する選挙ごとに集約） ---
const earlyVotingByElection = ref({})
function loadEarlyVotingByElection() {
  const map = {}
  for (const e of electionsForRegion.value) {
    map[e.id] = listEarlyVotingPlacesForRegion(regionId.value, e.id)
  }
  earlyVotingByElection.value = map
}
watch(electionsForRegion, loadEarlyVotingByElection, { immediate: true })

// 選挙の期日前投票期間（複数投票所の最早〜最遅）を返す。登録がなければnull。
function earlyVotingRange(electionId) {
  const places = earlyVotingByElection.value[electionId] || []
  if (places.length === 0) return null
  return {
    start: places.reduce((min, p) => (p.period_start < min ? p.period_start : min), places[0].period_start),
    end: places.reduce((max, p) => (p.period_end > max ? p.period_end : max), places[0].period_end),
  }
}

// --- 期日前投票所の場所一覧の展開表示 ---
const expandedElectionIds = ref(new Set())
function togglePlaces(electionId) {
  const next = new Set(expandedElectionIds.value)
  if (next.has(electionId)) next.delete(electionId)
  else next.add(electionId)
  expandedElectionIds.value = next
}

// --- 投票記録 ---
const votedElections = ref([])
function reloadVotedElections() {
  votedElections.value = listVotedElections(regionId.value)
}
watch(regionId, reloadVotedElections, { immediate: true })
function markVotedNow() {
  if (!selectedElectionId.value) return
  markVoted(regionId.value, Number(selectedElectionId.value))
  reloadVotedElections()
}

</script>

<template>
  <p v-if="loadError" class="error">{{ loadError }}</p>
  <template v-else-if="region">
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </nav>

    <div class="field" v-if="activeTab === 'voteRecords'">
      <label>対象の選挙</label>
      <select v-model="selectedElectionId">
        <option value="">選択してください</option>
        <option v-for="e in electionsForRegion" :key="e.id" :value="e.id">{{ e.name }}</option>
      </select>
    </div>

    <section v-show="activeTab === 'overview'">
      <h2>選挙情報</h2>

      <div v-if="nextElection" class="hero">
        <span class="badge">{{ nextElection.election_type }}</span>
        <h3>{{ nextElection.name }}</h3>
        <div class="hero-dates">
          <div>
            <div class="hero-label">投票日まであと{{ nextElectionDetail.days_until_vote }}日</div>
            <div class="hero-value">{{ formatVoteDate(nextElection.vote_date) }}</div>
          </div>
          <div>
            <div class="hero-label">期日前投票期間</div>
            <template v-if="earlyVotingRange(nextElection.id)">
              <div class="hero-value hero-value--sub">
                {{ earlyVotingRange(nextElection.id).start }}〜{{ earlyVotingRange(nextElection.id).end }}
              </div>
              <button type="button" class="secondary" @click="togglePlaces(nextElection.id)">
                {{ expandedElectionIds.has(nextElection.id) ? "場所を閉じる" : "場所を見る" }}
              </button>
            </template>
            <div v-else class="hero-value hero-value--sub">登録されていません</div>
          </div>
        </div>
        <table v-if="expandedElectionIds.has(nextElection.id)" style="margin-top: 12px;">
          <thead><tr><th>投票所</th><th>期間</th><th>受付時間</th></tr></thead>
          <tbody>
            <tr v-for="p in earlyVotingByElection[nextElection.id]" :key="p.id">
              <td>{{ p.name }}（{{ p.address }}）</td>
              <td>{{ p.period_start }}〜{{ p.period_end }}</td>
              <td>{{ p.open_time }}〜{{ p.close_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else>次回の選挙は登録されていません。</p>

      <template v-if="otherElections.length > 0">
        <h3 style="margin-top: 16px;">その他の関係する選挙</h3>
        <div class="election-list">
          <div v-for="e in otherElections" :key="e.id" class="election-row">
            <div class="election-row-main">
              <div>
                <strong>{{ e.name }}</strong>
                <span class="badge">{{ e.election_type }}</span>
              </div>
              <div class="election-row-dates">
                <span>投票日: {{ e.vote_date }}</span>
                <template v-if="earlyVotingRange(e.id)">
                  <span>期日前: {{ earlyVotingRange(e.id).start }}〜{{ earlyVotingRange(e.id).end }}</span>
                  <button type="button" class="secondary" @click="togglePlaces(e.id)">
                    {{ expandedElectionIds.has(e.id) ? "場所を閉じる" : "場所を見る" }}
                  </button>
                </template>
                <span v-else>期日前投票所は登録されていません</span>
              </div>
            </div>
            <table v-if="expandedElectionIds.has(e.id)" style="margin-top: 8px;">
              <thead><tr><th>投票所</th><th>期間</th><th>受付時間</th></tr></thead>
              <tbody>
                <tr v-for="p in earlyVotingByElection[e.id]" :key="p.id">
                  <td>{{ p.name }}（{{ p.address }}）</td>
                  <td>{{ p.period_start }}〜{{ p.period_end }}</td>
                  <td>{{ p.open_time }}〜{{ p.close_time }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </section>

    <section v-show="activeTab === 'overview'">
      <h2>あなたの投票所（当日）</h2>
      <template v-if="pollingPlace">
        <p>{{ pollingPlace.name }}（{{ pollingPlace.address }}）</p>
        <p>受付時間: {{ pollingPlace.open_time }}〜{{ pollingPlace.close_time }}</p>
        <p>
          <a :href="pollingPlace.map_url" target="_blank" rel="noopener">地図で見る</a> /
          <a :href="pollingPlace.route_url" target="_blank" rel="noopener">経路を調べる</a>
        </p>
      </template>
      <p v-else>この地域の投票所はまだ登録されていません。</p>
    </section>

    <p v-show="activeTab === 'overview'" class="address-line">
      登録地域: {{ region.zipcode }} {{ region.prefecture }}{{ region.city }}{{ region.town }}
    </p>

    <section v-show="activeTab === 'notifications'">
      <h2>投票日の通知</h2>
      <div class="field">
        <label><input type="checkbox" v-model="notifySettingForm.enabled" /> 通知を有効にする</label>
      </div>
      <div class="field">
        <label>通知タイミング（カンマ区切りの残り日数、例: 7,1,0）</label>
        <input v-model="notifySettingForm.daysBefore" />
      </div>
      <button type="button" @click="saveNotifySetting">設定を保存</button>
    </section>

    <section v-show="activeTab === 'voteRecords'">
      <h2>投票済みの記録</h2>
      <button type="button" :disabled="!selectedElectionId" @click="markVotedNow">投票したと記録する</button>
      <table v-if="votedElections.length > 0" style="margin-top: 8px;">
        <thead><tr><th>選挙名</th><th>投票日</th><th>記録日時</th></tr></thead>
        <tbody>
          <tr v-for="e in votedElections" :key="e.id">
            <td>{{ e.name }}</td>
            <td>{{ e.vote_date }}</td>
            <td>{{ e.voted_at }}</td>
          </tr>
        </tbody>
      </table>
    </section>

  </template>
</template>
