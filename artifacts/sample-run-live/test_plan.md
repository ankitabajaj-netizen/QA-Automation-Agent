# Test Plan: Suspend Betting Markets on Red Card

## Scenarios
| ID | Priority | Type | Title | Rationale |
|----|----------|------|-------|-----------|
| P0-1 | P0 | Functional | Suspend markets upon direct red card | Ensures no further bets can be placed on markets post-red card, preventing financial loss. |
| P0-2 | P0 | Functional | Suspend markets upon second yellow card resulting in red card | Ensures second yellow cards leading to red cards are handled the same way to avoid market exposure. |
| P1-1 | P1 | Performance | Check suspension timing after red card event | Verifies that markets are suspended within seconds of red card event to mitigate financial risks. |
| P1-2 | P1 | Functional | No suspension of unrelated markets | Ensures that only markets related to the player are suspended, preserving valid betting opportunities. |
| P2-1 | P2 | Functional | Verify suspension for combined markets with multiple players | Ensures that markets with the player as one of many selections are appropriately suspended. |
| Negative-1 | P1 | Negative | No suspension if red card received after match termination | Validates that no suspension occurs if a red card is issued post-match. |
| Boundary-1 | P2 | Boundary | Testing suspension just before and after the red card incident | Verifies exact timing of trade suspension to ensure adherence to near-real-time expectations. |

## Open Questions / Ambiguities
- What exact time frame is considered 'near-real-time' for suspending markets after a red card?
- How will the system identify related markets if multiple players are involved and there are numerous betting markets?
- Is there a specific obligation to inform users when markets are suspended, or is this strictly a backend process?

## Entry Criteria
- Red card event is received from upstream match events feed.
- Markets related to the player are currently open.

## Exit Criteria
- All relevant markets must be suspended immediately upon red card receipt.
- Verify that the system logs the suspension action for auditing purposes.