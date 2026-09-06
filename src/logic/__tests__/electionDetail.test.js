import { beforeEach, describe, expect, it } from "vitest"
import { addElection } from "../elections.js"
import { getElectionDetail } from "../electionDetail.js"
import { isoDateAfterDays } from "./testHelpers.js"

describe("electionDetail", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("投票日までの残り日数を計算する", () => {
    const election = addElection({
      name: "テスト選挙",
      electionType: "衆議院議員選挙",
      prefecture: null,
      city: null,
      announcementDate: isoDateAfterDays(0),
      voteDate: isoDateAfterDays(10),
      sourceUrl: "https://example.jp/election",
    })
    const detail = getElectionDetail(election.id)
    expect(detail.days_until_vote).toBe(10)
    expect(detail.name).toBe("テスト選挙")
    expect(detail.vote_start_time).toBe("07:00")
    expect(detail.vote_end_time).toBe("20:00")
  })
})
