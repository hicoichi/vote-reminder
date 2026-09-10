<script setup>
import { computed, ref, watch } from "vue"
import { getRegion } from "../logic/regions.js"
import { listElectionsForRegion, nextElectionForRegion } from "../logic/regionElections.js"
import { getElectionDetail } from "../logic/electionDetail.js"
import {
  DEFAULT_DAYS_BEFORE,
  getEffectiveSetting,
  getSetting,
  setElectionSetting,
  setSetting,
} from "../logic/notifications.js"
import { getPollingPlaceForRegion } from "../logic/pollingPlaces.js"
import { listEarlyVotingPlacesForRegion } from "../logic/earlyVoting.js"
import { listVotedElections, markVoted } from "../logic/voteRecords.js"

const props = defineProps({ id: { type: String, required: true } })
const regionId = computed(() => Number(props.id))
const region = ref(null)
const loadError = ref("")

const tabs = [
  { id: "overview", label: "概要" },
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

// --- 自分に関係する選挙（投票日順） ---
const electionsForRegion = computed(() => listElectionsForRegion(regionId.value))
const nextElection = computed(() => nextElectionForRegion(regionId.value))
const nextElectionDetail = computed(() => (nextElection.value ? getElectionDetail(nextElection.value.id) : null))
const otherElections = computed(() =>
  electionsForRegion.value.filter((e) => !nextElection.value || e.id !== nextElection.value.id)
)

function parseDaysBeforeInput(value) {
  return value
    .split(",")
    .filter((v) => v.trim() !== "")
    .map((v) => Number(v))
}

// --- 通知設定（共通、歯車アイコンから開く） ---
const commonDialog = ref(null)
const commonSettingForm = ref({ enabled: true, daysBefore: DEFAULT_DAYS_BEFORE.join(",") })
function openCommonModal() {
  const setting = getSetting(regionId.value)
  commonSettingForm.value = { enabled: setting.enabled, daysBefore: setting.days_before.join(",") }
  commonDialog.value?.showModal()
}
function closeCommonModal() {
  commonDialog.value?.close()
}
function handleCommonDialogClick(event) {
  if (event.target === event.currentTarget) closeCommonModal()
}
function saveCommonSetting() {
  setSetting(regionId.value, {
    enabled: commonSettingForm.value.enabled,
    daysBefore: parseDaysBeforeInput(commonSettingForm.value.daysBefore),
  })
  closeCommonModal()
}

// --- 通知設定（選挙ごとの個別設定） ---
const notifyDialog = ref(null)
const notifyElectionId = ref(null)
const notifyElection = computed(() =>
  notifyElectionId.value ? electionsForRegion.value.find((e) => e.id === notifyElectionId.value) ?? null : null
)
const notifyElectionForm = ref({ enabled: true, daysBefore: "" })
function openNotifyModal(electionId) {
  notifyElectionId.value = electionId
  const effective = getEffectiveSetting(regionId.value, electionId)
  notifyElectionForm.value = { enabled: effective.enabled, daysBefore: effective.days_before.join(",") }
  notifyDialog.value?.showModal()
}
function closeNotifyModal() {
  notifyDialog.value?.close()
}
function handleNotifyDialogClick(event) {
  if (event.target === event.currentTarget) closeNotifyModal()
}
const notifyFormDiffersFromCommon = computed(() => {
  const common = getSetting(regionId.value)
  const formDaysBefore = parseDaysBeforeInput(notifyElectionForm.value.daysBefore)
  return (
    notifyElectionForm.value.enabled !== common.enabled ||
    formDaysBefore.length !== common.days_before.length ||
    formDaysBefore.some((d, i) => d !== common.days_before[i])
  )
})
function resetNotifyFormToCommon() {
  const common = getSetting(regionId.value)
  notifyElectionForm.value = { enabled: common.enabled, daysBefore: common.days_before.join(",") }
}
function saveNotifyElectionSetting() {
  if (!notifyElectionId.value) return
  setElectionSetting(regionId.value, notifyElectionId.value, {
    enabled: notifyElectionForm.value.enabled,
    daysBefore: parseDaysBeforeInput(notifyElectionForm.value.daysBefore),
  })
  closeNotifyModal()
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

function daysUntilVote(electionId) {
  return getElectionDetail(electionId).days_until_vote
}

// 今日が期日前投票期間中かどうか。
function isEarlyVotingActive(electionId) {
  const range = earlyVotingRange(electionId)
  if (!range) return false
  const todayStr = new Date().toISOString().slice(0, 10)
  return range.start <= todayStr && todayStr <= range.end
}

// タイムラインバー用に、期日前投票期間・今日の位置を0〜100%で返す。
function timelineStats(electionId, voteDateStr) {
  const range = earlyVotingRange(electionId)
  if (!range) return null
  const start = new Date(range.start)
  const end = new Date(range.end)
  const voteDate = new Date(voteDateStr)
  const today = new Date(new Date().toISOString().slice(0, 10))
  const domainStart = today < start ? today : start
  const totalMs = voteDate - domainStart
  const pct = (d) => (totalMs <= 0 ? 0 : Math.min(100, Math.max(0, ((d - domainStart) / totalMs) * 100)))
  return {
    earlyLeft: pct(start),
    earlyWidth: Math.max(0, pct(end) - pct(start)),
    todayLeft: pct(today),
  }
}
const nextTimelineStats = computed(() =>
  nextElection.value ? timelineStats(nextElection.value.id, nextElection.value.vote_date) : null
)

// --- 期日前投票所の場所一覧モーダル ---
const placesDialog = ref(null)
const modalElectionId = ref(null)
const modalElection = computed(() =>
  modalElectionId.value ? electionsForRegion.value.find((e) => e.id === modalElectionId.value) ?? null : null
)
function openPlacesModal(electionId) {
  modalElectionId.value = electionId
  placesDialog.value?.showModal()
}
function closePlacesModal() {
  placesDialog.value?.close()
}
function handleDialogClick(event) {
  if (event.target === event.currentTarget) closePlacesModal()
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
      <button type="button" class="gear-btn" aria-label="共通の通知設定" @click="openCommonModal">⚙</button>
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

      <div v-if="nextElection" class="hero" :class="{ 'is-active': isEarlyVotingActive(nextElection.id) }">
        <span class="badge">{{ nextElection.election_type }}</span>
        <h3>{{ nextElection.name }}</h3>
        <div v-if="isEarlyVotingActive(nextElection.id)" class="hero-headline">今すぐ投票できます</div>
        <div class="hero-dates">
          <div>
            <div class="hero-label">投票終了まであと</div>
            <div class="hero-value">{{ nextElectionDetail.days_until_vote }}<span class="unit">日</span></div>
          </div>
          <div>
            <div class="hero-label">
              期日前投票期間
              <span v-if="isEarlyVotingActive(nextElection.id)" class="now-badge">受付中</span>
            </div>
            <template v-if="earlyVotingRange(nextElection.id)">
              <div class="hero-value--sub">
                {{ earlyVotingRange(nextElection.id).start }}〜{{ earlyVotingRange(nextElection.id).end }}
              </div>
              <button type="button" class="secondary" @click="openPlacesModal(nextElection.id)">場所を見る</button>
            </template>
            <div v-else class="hero-value--sub">登録されていません</div>
          </div>
        </div>
        <div v-if="nextTimelineStats" class="timeline">
          <div class="timeline-track">
            <div
              class="timeline-early"
              :style="{ left: nextTimelineStats.earlyLeft + '%', width: nextTimelineStats.earlyWidth + '%' }"
            ></div>
            <div class="timeline-dot" :style="{ left: nextTimelineStats.todayLeft + '%' }"></div>
          </div>
          <div class="timeline-labels">
            <span>期日前 {{ earlyVotingRange(nextElection.id).start }}</span>
            <span>投票日 {{ nextElection.vote_date }}</span>
          </div>
        </div>
        <div class="hero-actions">
          <button type="button" class="secondary" @click="openNotifyModal(nextElection.id)">通知設定</button>
        </div>
      </div>
      <p v-else>次回の選挙は登録されていません。</p>

      <template v-if="otherElections.length > 0">
        <h3 style="margin-top: 16px;">その他の関係する選挙</h3>
        <div class="election-list">
          <div
            v-for="e in otherElections"
            :key="e.id"
            class="election-row"
            :class="{ 'is-active': isEarlyVotingActive(e.id) }"
          >
            <div class="election-row-main">
              <div>
                <strong>{{ e.name }}</strong>
                <span class="badge">{{ e.election_type }}</span>
              </div>
              <div class="election-row-dates">
                <span class="days-left">あと{{ daysUntilVote(e.id) }}日</span>
                <template v-if="earlyVotingRange(e.id)">
                  <span>
                    期日前: {{ earlyVotingRange(e.id).start }}〜{{ earlyVotingRange(e.id).end }}
                    <span v-if="isEarlyVotingActive(e.id)" class="now-badge">受付中</span>
                  </span>
                  <button type="button" class="secondary" @click="openPlacesModal(e.id)">場所を見る</button>
                </template>
                <span v-else>期日前投票所は登録されていません</span>
                <button type="button" class="secondary" @click="openNotifyModal(e.id)">通知設定</button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </section>

    <dialog ref="placesDialog" class="places-dialog" @click="handleDialogClick" @close="modalElectionId = null">
      <div class="modal-body">
        <div class="modal-head">
          <h3>期日前投票所<template v-if="modalElection">（{{ modalElection.name }}）</template></h3>
          <button type="button" class="modal-close" @click="closePlacesModal">×</button>
        </div>
        <table v-if="modalElection && (earlyVotingByElection[modalElection.id]?.length ?? 0) > 0">
          <thead><tr><th>投票所</th><th>期間</th><th>受付時間</th></tr></thead>
          <tbody>
            <tr v-for="p in earlyVotingByElection[modalElection.id]" :key="p.id">
              <td>{{ p.name }}（{{ p.address }}）</td>
              <td>{{ p.period_start }}〜{{ p.period_end }}</td>
              <td>{{ p.open_time }}〜{{ p.close_time }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>期日前投票所は登録されていません。</p>
      </div>
    </dialog>

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

    <dialog ref="commonDialog" class="places-dialog" @click="handleCommonDialogClick">
      <div class="modal-body">
        <div class="modal-head">
          <h3>共通の通知設定</h3>
          <button type="button" class="modal-close" @click="closeCommonModal">×</button>
        </div>
        <div class="field">
          <label><input type="checkbox" v-model="commonSettingForm.enabled" /> 通知を有効にする</label>
        </div>
        <div class="field">
          <label>通知タイミング（カンマ区切りの残り日数、例: 7,1,0）</label>
          <input v-model="commonSettingForm.daysBefore" />
        </div>
        <button type="button" @click="saveCommonSetting">保存</button>
      </div>
    </dialog>

    <dialog ref="notifyDialog" class="places-dialog" @click="handleNotifyDialogClick" @close="notifyElectionId = null">
      <div class="modal-body">
        <div class="modal-head">
          <h3>通知設定<template v-if="notifyElection">（{{ notifyElection.name }}）</template></h3>
          <button type="button" class="modal-close" @click="closeNotifyModal">×</button>
        </div>
        <div class="field">
          <label><input type="checkbox" v-model="notifyElectionForm.enabled" /> 通知を有効にする</label>
        </div>
        <div class="field">
          <label>通知タイミング（カンマ区切りの残り日数、例: 7,1,0）</label>
          <input v-model="notifyElectionForm.daysBefore" />
        </div>
        <div class="modal-actions">
          <button type="button" @click="saveNotifyElectionSetting">保存</button>
          <button v-if="notifyFormDiffersFromCommon" type="button" class="secondary" @click="resetNotifyFormToCommon">
            共通設定に戻す
          </button>
        </div>
      </div>
    </dialog>

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
