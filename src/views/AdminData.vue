<script setup>
import { ref } from "vue"
import { ELECTION_TYPES, STATUSES, addElection, listElections, setElectionStatus } from "../logic/elections.js"
import { addPollingPlace } from "../logic/pollingPlaces.js"
import { addEarlyVotingPlace } from "../logic/earlyVoting.js"
import { addCandidate, setGazette, setResult } from "../logic/candidates.js"

const errorMessage = ref("")
function runSafely(fn) {
  errorMessage.value = ""
  try {
    fn()
  } catch (e) {
    errorMessage.value = e.message
  }
}

// --- 選挙 ---
const elections = ref(listElections())
function reloadElections() {
  elections.value = listElections()
}
const electionForm = ref({
  name: "",
  electionType: ELECTION_TYPES[0],
  prefecture: "",
  city: "",
  announcementDate: "",
  voteDate: "",
  sourceUrl: "",
})
function submitElection() {
  runSafely(() => {
    addElection({
      name: electionForm.value.name,
      electionType: electionForm.value.electionType,
      prefecture: electionForm.value.prefecture || null,
      city: electionForm.value.city || null,
      announcementDate: electionForm.value.announcementDate,
      voteDate: electionForm.value.voteDate,
      sourceUrl: electionForm.value.sourceUrl,
    })
    electionForm.value = {
      name: "",
      electionType: ELECTION_TYPES[0],
      prefecture: "",
      city: "",
      announcementDate: "",
      voteDate: "",
      sourceUrl: "",
    }
    reloadElections()
  })
}
function changeStatus(electionId, status) {
  runSafely(() => {
    setElectionStatus(electionId, status)
    reloadElections()
  })
}

// --- 投票所 ---
const pollingPlaceForm = ref({ prefecture: "", city: "", name: "", address: "", openTime: "07:00", closeTime: "20:00" })
const pollingPlaceMessage = ref("")
function submitPollingPlace() {
  runSafely(() => {
    addPollingPlace(pollingPlaceForm.value)
    pollingPlaceMessage.value = `投票所「${pollingPlaceForm.value.name}」を登録しました`
    pollingPlaceForm.value = { prefecture: "", city: "", name: "", address: "", openTime: "07:00", closeTime: "20:00" }
  })
}

// --- 期日前投票所 ---
const earlyVotingForm = ref({
  electionId: "",
  name: "",
  address: "",
  periodStart: "",
  periodEnd: "",
  openTime: "08:30",
  closeTime: "20:00",
})
const earlyVotingMessage = ref("")
function submitEarlyVoting() {
  runSafely(() => {
    addEarlyVotingPlace({ ...earlyVotingForm.value, electionId: Number(earlyVotingForm.value.electionId) })
    earlyVotingMessage.value = `期日前投票所「${earlyVotingForm.value.name}」を登録しました`
    earlyVotingForm.value = {
      electionId: "",
      name: "",
      address: "",
      periodStart: "",
      periodEnd: "",
      openTime: "08:30",
      closeTime: "20:00",
    }
  })
}

// --- 候補者 ---
const candidateForm = ref({ electionId: "", name: "", party: "", profile: "", sourceUrl: "" })
const candidateMessage = ref("")
function submitCandidate() {
  runSafely(() => {
    addCandidate({
      electionId: Number(candidateForm.value.electionId),
      name: candidateForm.value.name,
      party: candidateForm.value.party || null,
      profile: candidateForm.value.profile || null,
      sourceUrl: candidateForm.value.sourceUrl || null,
    })
    candidateMessage.value = `候補者「${candidateForm.value.name}」を登録しました`
    candidateForm.value = { electionId: "", name: "", party: "", profile: "", sourceUrl: "" }
  })
}

// --- 選挙公報 ---
const gazetteForm = ref({ electionId: "", content: "", sourceUrl: "" })
const gazetteMessage = ref("")
function submitGazette() {
  runSafely(() => {
    setGazette(Number(gazetteForm.value.electionId), gazetteForm.value.content, gazetteForm.value.sourceUrl)
    gazetteMessage.value = "選挙公報を登録しました"
  })
}

// --- 開票結果 ---
const resultForm = ref({ candidateId: "", votes: "", elected: false })
const resultMessage = ref("")
function submitResult() {
  runSafely(() => {
    setResult(Number(resultForm.value.candidateId), Number(resultForm.value.votes), resultForm.value.elected)
    resultMessage.value = "開票結果を登録しました"
    resultForm.value = { candidateId: "", votes: "", elected: false }
  })
}
</script>

<template>
  <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

  <section>
    <h2>選挙情報の登録（管理用）</h2>
    <form @submit.prevent="submitElection">
      <div class="field"><label>選挙名</label><input v-model="electionForm.name" required /></div>
      <div class="field">
        <label>種別</label>
        <select v-model="electionForm.electionType">
          <option v-for="t in ELECTION_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="field"><label>都道府県（対象を都道府県単位に絞る場合）</label><input v-model="electionForm.prefecture" /></div>
      <div class="field"><label>市区町村（対象を市区町村単位に絞る場合）</label><input v-model="electionForm.city" /></div>
      <div class="field"><label>公示日・告示日</label><input type="date" v-model="electionForm.announcementDate" required /></div>
      <div class="field"><label>投票日</label><input type="date" v-model="electionForm.voteDate" required /></div>
      <div class="field"><label>出典URL</label><input v-model="electionForm.sourceUrl" required /></div>
      <button type="submit">登録する</button>
    </form>

    <h3 style="margin-top: 16px;">登録済みの選挙</h3>
    <table v-if="elections.length > 0">
      <thead><tr><th>選挙名</th><th>種別</th><th>投票日</th><th>ステータス</th><th></th></tr></thead>
      <tbody>
        <tr v-for="e in elections" :key="e.id">
          <td>{{ e.name }}</td>
          <td>{{ e.election_type }}</td>
          <td>{{ e.vote_date }}</td>
          <td>{{ e.status }}</td>
          <td>
            <select :value="e.status" @change="changeStatus(e.id, $event.target.value)">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>選挙情報はまだ登録されていません。</p>
  </section>

  <section>
    <h2>投票所の登録（管理用）</h2>
    <form @submit.prevent="submitPollingPlace">
      <div class="field"><label>都道府県</label><input v-model="pollingPlaceForm.prefecture" required /></div>
      <div class="field"><label>市区町村</label><input v-model="pollingPlaceForm.city" required /></div>
      <div class="field"><label>投票所名</label><input v-model="pollingPlaceForm.name" required /></div>
      <div class="field"><label>住所</label><input v-model="pollingPlaceForm.address" required /></div>
      <div class="field"><label>開設時間</label><input v-model="pollingPlaceForm.openTime" /></div>
      <div class="field"><label>閉鎖時間</label><input v-model="pollingPlaceForm.closeTime" /></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="pollingPlaceMessage">{{ pollingPlaceMessage }}</p>
  </section>

  <section>
    <h2>期日前投票所の登録（管理用）</h2>
    <form @submit.prevent="submitEarlyVoting">
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="earlyVotingForm.electionId" required>
          <option value="" disabled>選択してください</option>
          <option v-for="e in elections" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <div class="field"><label>投票所名</label><input v-model="earlyVotingForm.name" required /></div>
      <div class="field"><label>住所</label><input v-model="earlyVotingForm.address" required /></div>
      <div class="field"><label>期間開始</label><input type="date" v-model="earlyVotingForm.periodStart" required /></div>
      <div class="field"><label>期間終了</label><input type="date" v-model="earlyVotingForm.periodEnd" required /></div>
      <div class="field"><label>受付開始時間</label><input v-model="earlyVotingForm.openTime" /></div>
      <div class="field"><label>受付終了時間</label><input v-model="earlyVotingForm.closeTime" /></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="earlyVotingMessage">{{ earlyVotingMessage }}</p>
  </section>

  <section>
    <h2>候補者の登録（管理用）</h2>
    <form @submit.prevent="submitCandidate">
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="candidateForm.electionId" required>
          <option value="" disabled>選択してください</option>
          <option v-for="e in elections" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <div class="field"><label>候補者名</label><input v-model="candidateForm.name" required /></div>
      <div class="field"><label>政党</label><input v-model="candidateForm.party" /></div>
      <div class="field"><label>プロフィール</label><textarea v-model="candidateForm.profile"></textarea></div>
      <div class="field"><label>出典URL</label><input v-model="candidateForm.sourceUrl" /></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="candidateMessage">{{ candidateMessage }}</p>
  </section>

  <section>
    <h2>選挙公報の登録（管理用）</h2>
    <form @submit.prevent="submitGazette">
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="gazetteForm.electionId" required>
          <option value="" disabled>選択してください</option>
          <option v-for="e in elections" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <div class="field"><label>内容</label><textarea v-model="gazetteForm.content" required></textarea></div>
      <div class="field"><label>出典URL</label><input v-model="gazetteForm.sourceUrl" required /></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="gazetteMessage">{{ gazetteMessage }}</p>
  </section>

  <section>
    <h2>開票結果の登録（管理用）</h2>
    <form @submit.prevent="submitResult">
      <div class="field"><label>候補者ID</label><input type="number" v-model="resultForm.candidateId" required /></div>
      <div class="field"><label>得票数</label><input type="number" v-model="resultForm.votes" required /></div>
      <div class="field"><label><input type="checkbox" v-model="resultForm.elected" /> 当選</label></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="resultMessage">{{ resultMessage }}</p>
  </section>
</template>
