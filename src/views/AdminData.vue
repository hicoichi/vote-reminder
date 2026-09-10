<script setup>
import { computed, ref, watch } from "vue"
import { ELECTION_TYPES, STATUSES, addElection, deleteElection, listElections, setElectionStatus, updateElection } from "../logic/elections.js"
import {
  addPollingPlace,
  deletePollingPlace,
  listPollingPlaces,
  updatePollingPlace,
} from "../logic/pollingPlaces.js"
import {
  addEarlyVotingPlace,
  deleteEarlyVotingPlace,
  listEarlyVotingPlaces,
  updateEarlyVotingPlace,
} from "../logic/earlyVoting.js"
import { addCandidate, getGazette, getResults, listCandidates, setGazette, setResult } from "../logic/candidates.js"

const errorMessage = ref("")
function runSafely(fn) {
  errorMessage.value = ""
  try {
    fn()
  } catch (e) {
    errorMessage.value = e.message
  }
}

function electionName(electionId) {
  return elections.value.find((e) => e.id === electionId)?.name ?? `（削除済み id=${electionId}）`
}

// --- 選挙 ---
const elections = ref(listElections())
function reloadElections() {
  elections.value = listElections()
}
const emptyElectionForm = () => ({
  name: "",
  electionType: ELECTION_TYPES[0],
  prefecture: "",
  city: "",
  announcementDate: "",
  voteDate: "",
  sourceUrl: "",
})
const electionForm = ref(emptyElectionForm())
const editingElectionId = ref(null)
function editElection(e) {
  editingElectionId.value = e.id
  electionForm.value = {
    name: e.name,
    electionType: e.election_type,
    prefecture: e.prefecture ?? "",
    city: e.city ?? "",
    announcementDate: e.announcement_date,
    voteDate: e.vote_date,
    sourceUrl: e.source_url,
  }
}
function cancelEditElection() {
  editingElectionId.value = null
  electionForm.value = emptyElectionForm()
}
function submitElection() {
  runSafely(() => {
    if (editingElectionId.value) {
      updateElection(editingElectionId.value, {
        name: electionForm.value.name,
        electionType: electionForm.value.electionType,
        prefecture: electionForm.value.prefecture || null,
        city: electionForm.value.city || null,
        announcementDate: electionForm.value.announcementDate,
        voteDate: electionForm.value.voteDate,
        sourceUrl: electionForm.value.sourceUrl,
      })
    } else {
      addElection({
        name: electionForm.value.name,
        electionType: electionForm.value.electionType,
        prefecture: electionForm.value.prefecture || null,
        city: electionForm.value.city || null,
        announcementDate: electionForm.value.announcementDate,
        voteDate: electionForm.value.voteDate,
        sourceUrl: electionForm.value.sourceUrl,
      })
    }
    editingElectionId.value = null
    electionForm.value = emptyElectionForm()
    reloadElections()
  })
}
function changeStatus(electionId, status) {
  runSafely(() => {
    setElectionStatus(electionId, status)
    reloadElections()
  })
}
function removeElection(electionId) {
  if (!window.confirm("この選挙を削除しますか？紐づく期日前投票所・候補者情報などは参照できなくなります。")) return
  runSafely(() => {
    deleteElection(electionId)
    if (editingElectionId.value === electionId) cancelEditElection()
    reloadElections()
  })
}

// --- 投票所 ---
const pollingPlaces = ref(listPollingPlaces())
function reloadPollingPlaces() {
  pollingPlaces.value = listPollingPlaces()
}
const emptyPollingPlaceForm = () => ({
  prefecture: "",
  city: "",
  name: "",
  address: "",
  openTime: "07:00",
  closeTime: "20:00",
})
const pollingPlaceForm = ref(emptyPollingPlaceForm())
const editingPollingPlaceId = ref(null)
function editPollingPlace(p) {
  editingPollingPlaceId.value = p.id
  pollingPlaceForm.value = {
    prefecture: p.prefecture,
    city: p.city,
    name: p.name,
    address: p.address,
    openTime: p.open_time,
    closeTime: p.close_time,
  }
}
function cancelEditPollingPlace() {
  editingPollingPlaceId.value = null
  pollingPlaceForm.value = emptyPollingPlaceForm()
}
function submitPollingPlace() {
  runSafely(() => {
    if (editingPollingPlaceId.value) {
      updatePollingPlace(editingPollingPlaceId.value, pollingPlaceForm.value)
    } else {
      addPollingPlace(pollingPlaceForm.value)
    }
    editingPollingPlaceId.value = null
    pollingPlaceForm.value = emptyPollingPlaceForm()
    reloadPollingPlaces()
  })
}
function removePollingPlace(placeId) {
  if (!window.confirm("この投票所を削除しますか？")) return
  runSafely(() => {
    deletePollingPlace(placeId)
    if (editingPollingPlaceId.value === placeId) cancelEditPollingPlace()
    reloadPollingPlaces()
  })
}

// --- 期日前投票所 ---
const earlyVotingPlaces = ref(listEarlyVotingPlaces())
function reloadEarlyVotingPlaces() {
  earlyVotingPlaces.value = listEarlyVotingPlaces()
}
const emptyEarlyVotingForm = () => ({
  electionId: "",
  name: "",
  address: "",
  periodStart: "",
  periodEnd: "",
  openTime: "08:30",
  closeTime: "20:00",
})
const earlyVotingForm = ref(emptyEarlyVotingForm())
const editingEarlyVotingId = ref(null)
function editEarlyVotingPlace(p) {
  editingEarlyVotingId.value = p.id
  earlyVotingForm.value = {
    electionId: p.election_id,
    name: p.name,
    address: p.address,
    periodStart: p.period_start,
    periodEnd: p.period_end,
    openTime: p.open_time,
    closeTime: p.close_time,
  }
}
function cancelEditEarlyVotingPlace() {
  editingEarlyVotingId.value = null
  earlyVotingForm.value = emptyEarlyVotingForm()
}
function submitEarlyVoting() {
  runSafely(() => {
    const payload = { ...earlyVotingForm.value, electionId: Number(earlyVotingForm.value.electionId) }
    if (editingEarlyVotingId.value) {
      updateEarlyVotingPlace(editingEarlyVotingId.value, payload)
    } else {
      addEarlyVotingPlace(payload)
    }
    editingEarlyVotingId.value = null
    earlyVotingForm.value = emptyEarlyVotingForm()
    reloadEarlyVotingPlaces()
  })
}
function removeEarlyVotingPlace(placeId) {
  if (!window.confirm("この期日前投票所を削除しますか？")) return
  runSafely(() => {
    deleteEarlyVotingPlace(placeId)
    if (editingEarlyVotingId.value === placeId) cancelEditEarlyVotingPlace()
    reloadEarlyVotingPlaces()
  })
}

// --- 候補者 ---
const candidateForm = ref({ electionId: "", name: "", party: "", profile: "", sourceUrl: "" })
const candidateMessage = ref("")
const candidatesForSelectedElection = computed(() =>
  candidateForm.value.electionId ? listCandidates(Number(candidateForm.value.electionId)) : []
)
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
    candidateForm.value = { ...candidateForm.value, name: "", party: "", profile: "", sourceUrl: "" }
  })
}

// --- 選挙公報 ---
const gazetteForm = ref({ electionId: "", content: "", sourceUrl: "" })
const gazetteMessage = ref("")
watch(
  () => gazetteForm.value.electionId,
  (electionId) => {
    const existing = electionId ? getGazette(Number(electionId)) : null
    gazetteForm.value = {
      electionId,
      content: existing?.content ?? "",
      sourceUrl: existing?.source_url ?? "",
    }
  }
)
function submitGazette() {
  runSafely(() => {
    setGazette(Number(gazetteForm.value.electionId), gazetteForm.value.content, gazetteForm.value.sourceUrl)
    gazetteMessage.value = "選挙公報を登録しました"
  })
}

// --- 開票結果 ---
const resultForm = ref({ electionId: "", candidateId: "", votes: "", elected: false })
const resultMessage = ref("")
const candidatesForResultElection = computed(() =>
  resultForm.value.electionId ? listCandidates(Number(resultForm.value.electionId)) : []
)
const resultsForSelectedElection = computed(() =>
  resultForm.value.electionId ? getResults(Number(resultForm.value.electionId)) : []
)
watch(
  () => resultForm.value.electionId,
  () => {
    resultForm.value = { ...resultForm.value, candidateId: "", votes: "", elected: false }
  }
)
function submitResult() {
  runSafely(() => {
    setResult(Number(resultForm.value.candidateId), Number(resultForm.value.votes), resultForm.value.elected)
    resultMessage.value = "開票結果を登録しました"
    resultForm.value = { ...resultForm.value, candidateId: "", votes: "", elected: false }
  })
}
</script>

<template>
  <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

  <section>
    <h2>選挙情報の{{ editingElectionId ? "編集" : "登録" }}（管理用）</h2>
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
      <div class="modal-actions">
        <button type="submit">{{ editingElectionId ? "更新する" : "登録する" }}</button>
        <button v-if="editingElectionId" type="button" class="secondary" @click="cancelEditElection">キャンセル</button>
      </div>
    </form>

    <h3 style="margin-top: 16px;">登録済みの選挙</h3>
    <table v-if="elections.length > 0">
      <thead><tr><th>選挙名</th><th>種別</th><th>投票日</th><th>ステータス</th><th></th><th></th></tr></thead>
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
          <td style="display: flex; gap: 8px;">
            <button type="button" class="secondary" @click="editElection(e)">編集</button>
            <button type="button" class="secondary" @click="removeElection(e.id)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>選挙情報はまだ登録されていません。</p>
  </section>

  <section>
    <h2>投票所の{{ editingPollingPlaceId ? "編集" : "登録" }}（管理用）</h2>
    <form @submit.prevent="submitPollingPlace">
      <div class="field"><label>都道府県</label><input v-model="pollingPlaceForm.prefecture" required /></div>
      <div class="field"><label>市区町村</label><input v-model="pollingPlaceForm.city" required /></div>
      <div class="field"><label>投票所名</label><input v-model="pollingPlaceForm.name" required /></div>
      <div class="field"><label>住所</label><input v-model="pollingPlaceForm.address" required /></div>
      <div class="field"><label>開設時間</label><input v-model="pollingPlaceForm.openTime" /></div>
      <div class="field"><label>閉鎖時間</label><input v-model="pollingPlaceForm.closeTime" /></div>
      <div class="modal-actions">
        <button type="submit">{{ editingPollingPlaceId ? "更新する" : "登録する" }}</button>
        <button v-if="editingPollingPlaceId" type="button" class="secondary" @click="cancelEditPollingPlace">
          キャンセル
        </button>
      </div>
    </form>

    <h3 style="margin-top: 16px;">登録済みの投票所</h3>
    <table v-if="pollingPlaces.length > 0">
      <thead><tr><th>都道府県</th><th>市区町村</th><th>投票所名</th><th>住所</th><th></th></tr></thead>
      <tbody>
        <tr v-for="p in pollingPlaces" :key="p.id">
          <td>{{ p.prefecture }}</td>
          <td>{{ p.city }}</td>
          <td>{{ p.name }}</td>
          <td>{{ p.address }}</td>
          <td style="display: flex; gap: 8px;">
            <button type="button" class="secondary" @click="editPollingPlace(p)">編集</button>
            <button type="button" class="secondary" @click="removePollingPlace(p.id)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>投票所はまだ登録されていません。</p>
  </section>

  <section>
    <h2>期日前投票所の{{ editingEarlyVotingId ? "編集" : "登録" }}（管理用）</h2>
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
      <div class="modal-actions">
        <button type="submit">{{ editingEarlyVotingId ? "更新する" : "登録する" }}</button>
        <button v-if="editingEarlyVotingId" type="button" class="secondary" @click="cancelEditEarlyVotingPlace">
          キャンセル
        </button>
      </div>
    </form>

    <h3 style="margin-top: 16px;">登録済みの期日前投票所</h3>
    <table v-if="earlyVotingPlaces.length > 0">
      <thead><tr><th>対象の選挙</th><th>投票所名</th><th>期間</th><th></th></tr></thead>
      <tbody>
        <tr v-for="p in earlyVotingPlaces" :key="p.id">
          <td>{{ electionName(p.election_id) }}</td>
          <td>{{ p.name }}（{{ p.address }}）</td>
          <td>{{ p.period_start }}〜{{ p.period_end }}</td>
          <td style="display: flex; gap: 8px;">
            <button type="button" class="secondary" @click="editEarlyVotingPlace(p)">編集</button>
            <button type="button" class="secondary" @click="removeEarlyVotingPlace(p.id)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>期日前投票所はまだ登録されていません。</p>
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

    <template v-if="candidateForm.electionId">
      <h3 style="margin-top: 16px;">登録済みの候補者</h3>
      <table v-if="candidatesForSelectedElection.length > 0">
        <thead><tr><th>候補者名</th><th>政党</th></tr></thead>
        <tbody>
          <tr v-for="c in candidatesForSelectedElection" :key="c.id">
            <td>{{ c.name }}</td>
            <td>{{ c.party || "-" }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>この選挙の候補者はまだ登録されていません。</p>
    </template>
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
    <p style="opacity: 0.7; font-size: 0.85em;" v-if="gazetteForm.electionId && gazetteForm.content">
      この選挙にはすでに選挙公報が登録されています。内容を書き換えて登録すると上書きされます。
    </p>
  </section>

  <section>
    <h2>開票結果の登録（管理用）</h2>
    <form @submit.prevent="submitResult">
      <div class="field">
        <label>対象の選挙</label>
        <select v-model="resultForm.electionId" required>
          <option value="" disabled>選択してください</option>
          <option v-for="e in elections" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>候補者</label>
        <select v-model="resultForm.candidateId" required :disabled="!resultForm.electionId">
          <option value="" disabled>選択してください</option>
          <option v-for="c in candidatesForResultElection" :key="c.id" :value="c.id">
            {{ c.name }}{{ c.party ? `（${c.party}）` : "" }}
          </option>
        </select>
        <p v-if="resultForm.electionId && candidatesForResultElection.length === 0" style="font-size: 0.85em; opacity: 0.7;">
          この選挙の候補者がまだ登録されていません。先に候補者を登録してください。
        </p>
      </div>
      <div class="field"><label>得票数</label><input type="number" v-model="resultForm.votes" required /></div>
      <div class="field"><label><input type="checkbox" v-model="resultForm.elected" /> 当選</label></div>
      <button type="submit">登録する</button>
    </form>
    <p v-if="resultMessage">{{ resultMessage }}</p>

    <template v-if="resultForm.electionId && resultsForSelectedElection.length > 0">
      <h3 style="margin-top: 16px;">この選挙の開票結果</h3>
      <table>
        <thead><tr><th>候補者名</th><th>政党</th><th>得票数</th><th>当選</th></tr></thead>
        <tbody>
          <tr v-for="r in resultsForSelectedElection" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.party || "-" }}</td>
            <td>{{ r.votes ?? "-" }}</td>
            <td>{{ r.elected ? "当選" : "" }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>
