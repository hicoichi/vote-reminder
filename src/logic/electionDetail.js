// EPIC-03 選挙情報を表示できる。
import { getElection } from "./elections.js"

// 選挙名・種別・投票日・公示日/告示日・投票時間に加え、投票までの残り日数を返す。
export function getElectionDetail(electionId) {
  const election = { ...getElection(electionId) }
  const voteDate = new Date(election.vote_date)
  const today = new Date(new Date().toISOString().slice(0, 10))
  election.days_until_vote = Math.round((voteDate - today) / (24 * 60 * 60 * 1000))
  return election
}
