<script setup>
import { computed, ref, watch } from "vue"
import { getRegion } from "../logic/regions.js"
import { ELECTION_TYPES } from "../logic/elections.js"
import { listElectionsForRegion, nextElectionForRegion } from "../logic/regionElections.js"
import { getElectionDetail } from "../logic/electionDetail.js"
import {
  ALL_TYPES,
  DEFAULT_DAYS_BEFORE,
  getSetting,
  listNotifications,
  notifyDue,
  setSetting,
} from "../logic/notifications.js"
import { getPollingPlaceForRegion } from "../logic/pollingPlaces.js"
import { listEarlyVotingPlacesForRegion } from "../logic/earlyVoting.js"
import { listVotedElections, markVoted } from "../logic/voteRecords.js"
import { getGazette, getResults, listCandidates } from "../logic/candidates.js"
import { getPastElectionResults, listPastElections, listVotingHistory } from "../logic/electionHistory.js"

const props = defineProps({ id: { type: String, required: true } })
const regionId = computed(() => Number(props.id))
const region = ref(null)
const loadError = ref("")

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

// --- 自分に関係する選挙 ---
const electionTypeFilter = ref("")
const electionsForRegion = computed(() =>
  listElectionsForRegion(regionId.value, electionTypeFilter.value || null)
)
const nextElection = computed(() => nextElectionForRegion(regionId.value))
const selectedDetailId = ref(null)
const selectedDetail = computed(() =>
  selectedDetailId.value ? getElectionDetail(selectedDetailId.value) : null
)

// --- 通知設定・通知履歴 ---
const notifyTypeChoice = ref(ALL_TYPES)
const notifySettingForm = ref({ enabled: true, daysBefore: DEFAULT_DAYS_BEFORE.join(",") })
function loadNotifySetting() {
  const setting = getSetting(regionId.value, notifyTypeChoice.value)
  notifySettingForm.value = { enabled: setting.enabled, daysBefore: setting.days_before.join(",") }
}
watch([regionId, notifyTypeChoice], loadNotifySetting, { immediate: true })
function saveNotifySetting() {
  setSetting(regionId.value, notifyTypeChoice.value, {
    enabled: notifySettingForm.value.enabled,
    daysBefore: notifySettingForm.value.daysBefore
      .split(",")
      .filter((v) => v.trim() !== "")
      .map((v) => Number(v)),
  })
  loadNotifySetting()
}
const notifications = ref([])
function reloadNotifications() {
  notifications.value = listNotifications(regionId.value)
}
watch(regionId, reloadNotifications, { immediate: true })
function runNotifyCheck() {
  notifyDue(regionId.value)
  reloadNotifications()
}

// --- 投票所 ---
const pollingPlace = computed(() => getPollingPlaceForRegion(regionId.value))

// --- 期日前投票 ---
const earlyVotingElectionId = ref("")
const earlyVotingPlaces = ref([])
const earlyVotingError = ref("")
function loadEarlyVotingPlaces() {
  earlyVotingError.value = ""
  if (!earlyVotingElectionId.value) {
    earlyVotingPlaces.value = []
    return
  }
  try {
    earlyVotingPlaces.value = listEarlyVotingPlacesForRegion(
      regionId.value,
      Number(earlyVotingElectionId.value)
    )
  } catch (e) {
    earlyVotingError.value = e.message
    earlyVotingPlaces.value = []
  }
}
watch(earlyVotingElectionId, loadEarlyVotingPlaces)

// --- 投票記録 ---
const voteRecordElectionId = ref("")
const votedElections = ref([])
function reloadVotedElections() {
  votedElections.value = listVotedElections(regionId.value)
}
watch(regionId, reloadVotedElections, { immediate: true })
function markVotedNow() {
  if (!voteRecordElectionId.value) return
  markVoted(regionId.value, Number(voteRecordElectionId.value))
  reloadVotedElections()
}

// --- 候補者・公報・開票結果 ---
const candidateElectionId = ref("")
const candidateList = ref([])
const gazette = ref(null)
const results = ref([])
function loadCandidateInfo() {
  if (!candidateElectionId.value) {
    candidateList.value = []
    gazette.value = null
    results.value = []
    return
  }
  const electionId = Number(candidateElectionId.value)
  candidateList.value = listCandidates(electionId)
  gazette.value = getGazette(electionId)
  results.value = getResults(electionId)
}
watch(candidateElectionId, loadCandidateInfo)

// --- 選挙履歴・投票履歴 ---
const pastElections = ref([])
const votingHistory = ref([])
const pastResultsElectionId = ref(null)
const pastResults = ref([])
function reloadHistory() {
  pastElections.value = listPastElections(regionId.value)
  votingHistory.value = listVotingHistory(regionId.value)
}
watch(regionId, reloadHistory, { immediate: true })
function showPastResults(electionId) {
  pastResultsElectionId.value = electionId
  pastResults.value = getPastElectionResults(electionId)
}
</script>

<template>
  <p v-if="loadError" class="error">{{ loadError }}</p>
  <template v-else-if="region">
    <section>
      <h2>登録地域</h2>
      <p>{{ region.zipcode }} / {{ region.prefecture }}{{ region.city }}{{ region.town }}</p>
    </section>

    <section>
      <h2>次回の選挙</h2>
      <p v-if="nextElection">
        {{ nextElection.name }}（{{ nextElection.election_type }}） 投票日: {{ nextElection.vote_date }}
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
      <div v-if="selectedDetail" style="margin-top: 8px;">
        <strong>{{ selectedDetail.name }}</strong>
        ／公示・告示日: {{ selectedDetail.announcement_date }}
        ／投票時間: {{ selectedDetail.vote_start_time }}〜{{ selectedDetail.vote_end_time }}
        ／投票日まであと{{ selectedDetail.days_until_vote }}日
      </div>
    </section>

    <section>
      <h2>投票日の通知</h2>
      <div class="field">
        <label>設定対象の選挙種別</label>
        <select v-model="notifyTypeChoice">
          <option :value="ALL_TYPES">すべての選挙（共通設定）</option>
          <option v-for="t in ELECTION_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="field">
        <label><input type="checkbox" v-model="notifySettingForm.enabled" /> 通知を有効にする</label>
      </div>
      <div class="field">
        <label>通知タイミング（カンマ区切りの残り日数、例: 7,1,0）</label>
        <input v-model="notifySettingForm.daysBefore" />
      </div>
      <button type="button" @click="saveNotifySetting">設定を保存</button>

      <h3 style="margin-top: 16px;">通知履歴</h3>
      <button type="button" class="secondary" @click="runNotifyCheck">通知タイミングを確認する</button>
      <table v-if="notifications.length > 0" style="margin-top: 8px;">
        <thead><tr><th>送信日時</th><th>内容</th></tr></thead>
        <tbody>
          <tr v-for="n in notifications" :key="n.id">
            <td>{{ n.sent_at }}</td>
            <td>{{ n.message }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>通知履歴はありません。</p>
    </section>

    <section>
      <h2>投票所</h2>
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

    <section>
      <h2>期日前投票</h2>
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="earlyVotingElectionId">
          <option value="">選択してください</option>
          <option v-for="e in electionsForRegion" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
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
      <p v-else-if="earlyVotingElectionId">期日前投票所は登録されていません。</p>
    </section>

    <section>
      <h2>投票済みの記録</h2>
      <div class="field">
        <label>投票した選挙</label>
        <select v-model="voteRecordElectionId">
          <option value="">選択してください</option>
          <option v-for="e in electionsForRegion" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <button type="button" :disabled="!voteRecordElectionId" @click="markVotedNow">投票したと記録する</button>
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

    <section>
      <h2>候補者・選挙公報・開票結果</h2>
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="candidateElectionId">
          <option value="">選択してください</option>
          <option v-for="e in electionsForRegion" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <template v-if="candidateElectionId">
        <h3>候補者</h3>
        <ul v-if="candidateList.length > 0">
          <li v-for="c in candidateList" :key="c.id">
            {{ c.name }}<template v-if="c.party">（{{ c.party }}）</template>
          </li>
        </ul>
        <p v-else>候補者情報は登録されていません。</p>

        <h3>選挙公報</h3>
        <p v-if="gazette">{{ gazette.content }}</p>
        <p v-else>選挙公報は登録されていません。</p>

        <h3>開票結果</h3>
        <table v-if="results.some((r) => r.votes !== null)">
          <thead><tr><th>候補者</th><th>得票数</th><th>当選</th></tr></thead>
          <tbody>
            <tr v-for="r in results" :key="r.id">
              <td>{{ r.name }}</td>
              <td>{{ r.votes ?? "-" }}</td>
              <td>{{ r.elected ? "当選" : "" }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>開票結果はまだ登録されていません。</p>
      </template>
    </section>

    <section>
      <h2>選挙履歴・投票履歴</h2>
      <h3>過去の選挙</h3>
      <table v-if="pastElections.length > 0">
        <thead><tr><th>選挙名</th><th>投票日</th><th></th></tr></thead>
        <tbody>
          <tr v-for="e in pastElections" :key="e.id">
            <td>{{ e.name }}</td>
            <td>{{ e.vote_date }}</td>
            <td><button type="button" class="secondary" @click="showPastResults(e.id)">開票結果</button></td>
          </tr>
        </tbody>
      </table>
      <p v-else>過去の選挙はありません。</p>
      <table v-if="pastResultsElectionId && pastResults.length > 0" style="margin-top: 8px;">
        <thead><tr><th>候補者</th><th>得票数</th><th>当選</th></tr></thead>
        <tbody>
          <tr v-for="r in pastResults" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.votes ?? "-" }}</td>
            <td>{{ r.elected ? "当選" : "" }}</td>
          </tr>
        </tbody>
      </table>

      <h3 style="margin-top: 16px;">投票履歴</h3>
      <table v-if="votingHistory.length > 0">
        <thead><tr><th>選挙名</th><th>投票日</th><th>記録日時</th></tr></thead>
        <tbody>
          <tr v-for="e in votingHistory" :key="e.id">
            <td>{{ e.name }}</td>
            <td>{{ e.vote_date }}</td>
            <td>{{ e.voted_at }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>投票履歴はありません。</p>
    </section>
  </template>
</template>
