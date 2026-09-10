<script setup>
import { computed, ref, watch } from "vue"
import { getRegion } from "../logic/regions.js"
import { ELECTION_TYPES } from "../logic/elections.js"
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

// --- 対象の選挙（投票記録タブで利用） ---
const selectedElectionId = ref("")
watch(regionId, () => { selectedElectionId.value = "" })

// --- 自分に関係する選挙 ---
const electionTypeFilter = ref("")
const electionsForRegion = computed(() =>
  listElectionsForRegion(regionId.value, electionTypeFilter.value || null)
)
const allElectionsForRegion = computed(() => listElectionsForRegion(regionId.value, null))
const nextElection = computed(() => nextElectionForRegion(regionId.value))

// 選挙一覧で選択中の選挙（デフォルトは次回の選挙）。詳細情報と期日前投票所の表示に使う。
const selectedDetailId = ref(null)
watch(regionId, () => {
  selectedDetailId.value = region.value ? (nextElectionForRegion(regionId.value)?.id ?? null) : null
}, { immediate: true })
const selectedDetail = computed(() =>
  selectedDetailId.value ? getElectionDetail(selectedDetailId.value) : null
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

// --- 期日前投票（選択中の選挙に対応する投票所） ---
const earlyVotingPlaces = ref([])
const earlyVotingError = ref("")
function loadEarlyVotingPlaces() {
  earlyVotingError.value = ""
  if (!selectedDetailId.value) {
    earlyVotingPlaces.value = []
    return
  }
  try {
    earlyVotingPlaces.value = listEarlyVotingPlacesForRegion(regionId.value, selectedDetailId.value)
  } catch (e) {
    earlyVotingError.value = e.message
    earlyVotingPlaces.value = []
  }
}
watch(selectedDetailId, loadEarlyVotingPlaces, { immediate: true })

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
        <option v-for="e in allElectionsForRegion" :key="e.id" :value="e.id">{{ e.name }}</option>
      </select>
    </div>

    <section v-show="activeTab === 'overview'">
      <h2>登録地域</h2>
      <h3>住所</h3>
      <p>{{ region.zipcode }} / {{ region.prefecture }}{{ region.city }}{{ region.town }}</p>

      <h3 style="margin-top: 12px;">投票所（当日）</h3>
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

    <section v-show="activeTab === 'overview'">
      <h2>選挙情報</h2>
      <p v-if="nextElection">
        次回の選挙: {{ nextElection.name }}（{{ nextElection.election_type }}） 投票日: {{ nextElection.vote_date }}
      </p>
      <p v-else>次回の選挙は登録されていません。</p>

      <h3>関係する選挙一覧</h3>
      <div class="field">
        <label>種別で絞り込み</label>
        <select v-model="electionTypeFilter">
          <option value="">すべて</option>
          <option v-for="t in ELECTION_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <table v-if="electionsForRegion.length > 0">
        <thead>
          <tr><th>選挙名</th><th>種別</th><th>投票日</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="e in electionsForRegion" :key="e.id">
            <td>{{ e.name }}</td>
            <td>{{ e.election_type }}</td>
            <td>{{ e.vote_date }}</td>
            <td><button type="button" class="secondary" @click="selectedDetailId = e.id">詳細</button></td>
          </tr>
        </tbody>
      </table>
      <p v-else>実施予定の選挙はありません。</p>

      <div v-if="selectedDetail" class="field" style="margin-top: 12px;">
        <h3>{{ selectedDetail.name }}</h3>
        <p>
          公示・告示日: {{ selectedDetail.announcement_date }}
          ／投票時間: {{ selectedDetail.vote_start_time }}〜{{ selectedDetail.vote_end_time }}
          ／投票日まであと{{ selectedDetail.days_until_vote }}日
        </p>

        <h4>期日前投票所</h4>
        <p v-if="earlyVotingError" class="error">{{ earlyVotingError }}</p>
        <table v-else-if="earlyVotingPlaces.length > 0">
          <thead><tr><th>投票所</th><th>期間</th><th>受付時間</th></tr></thead>
          <tbody>
            <tr v-for="p in earlyVotingPlaces" :key="p.id">
              <td>{{ p.name }}（{{ p.address }}）</td>
              <td>{{ p.period_start }}〜{{ p.period_end }}</td>
              <td>{{ p.open_time }}〜{{ p.close_time }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>期日前投票所は登録されていません。</p>
      </div>
    </section>

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
