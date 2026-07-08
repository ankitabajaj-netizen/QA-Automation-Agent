# Test Plan: Red card suspends related betting markets

## Scenarios
| ID | Priority | Type | Title | Rationale |
|----|----------|------|-------|-----------|
| S1 | P0 | Positive | Direct red card suspends the player's primary market | Core happy path required by the story. |
| S2 | P0 | Edge | Red card suspends markets where the player is a secondary eligible selection | Story explicitly calls out multi-selection markets (Anytime Assist Provider, Next Card); highest financial exposure if missed. |
| S3 | P1 | Negative | Markets unrelated to the sent-off player remain open | Guards against over-suspension, which would needlessly cut off healthy trading markets. |
| S4 | P1 | Edge | Second yellow card converting to red also suspends related markets | Story requires second-yellow-to-red to be treated identically to a direct red card. |
| S5 | P2 | Boundary | Duplicate red card event for the same player is idempotent | Upstream match-events feeds are known to redeliver events; must not error or double-process. |
| S6 | P0 | Boundary | Suspension keeps pace with the near-real-time SLA | Trading ops flagged that a market open even a few seconds late is a real financial risk. |

## Open Questions / Ambiguities
- Story says suspension should be 'near-real-time' but gives no numeric SLA - we assumed a 100ms budget for this demo; product/trading ops should confirm the real number.
- If a red card is later overturned by VAR, should already-suspended markets reopen automatically, or does that require a human trading-ops decision? Not covered by this story.
- What happens to bets already placed and pending settlement at the moment of the red card - are they voided, honored, or held pending review? Not specified.
- Does suspension apply only to this match's markets, or should it also touch live 'tournament outright' markets referencing the same player? Not specified.

## Entry Criteria
- Match-events feed integration contract is stable (red card / second-yellow-red event schema agreed).
- Market eligibility data (which players a market is keyed to) is available to the suspension service.

## Exit Criteria
- All P0 scenarios pass consistently across 3 consecutive runs.
- No open P0/P1 defects from the triage stage.
- Open questions above have documented answers or an accepted-risk sign-off from product/trading ops.
