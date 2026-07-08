# Defect Report

Execution: 4/6 passed on first run.

## Betting markets not suspended for secondary player selections
- **Classification:** RealDefect
- **Severity/Priority:** S1 / P0
- **Likely root cause:** Failure text references 'EligiblePlayerIds'; `MarketSuspensionService.HandleRedCardAsync` only checks `EligiblePlayerIds[0]` before suspending a market, so a market stays open whenever the carded player is eligible but not listed first.
- **Suggested owner:** Trading Platform Team (market eligibility logic)
- **Affected scenarios:** Red card suspends markets where the player is a secondary eligible selection
- **Dedup key:** Market M# was expected to be Suspended but was Open.
- **Recommendation:** A live bet could still be placed on a market the red-carded player is eligible for. Fix the eligibility check to scan all of `EligiblePlayerIds`, not just the first entry, before the next release.

## Flaky: Suspension keeps pace with the near-real-time SLA
- **Classification:** Flaky
- **Severity/Priority:** S3 / P2
- **Likely root cause:** Failure text references 'suspended within'; the assertion polls for a 100ms budget while the platform's simulated propagation delay is uniformly random between 0-150ms, so the check loses the race in roughly one run in three regardless of code correctness. Rerun with identical code passed.
- **Suggested owner:** QE Team (test design) / Platform Reliability Team (confirm real SLA)
- **Affected scenarios:** Suspension keeps pace with the near-real-time SLA
- **Dedup key:** flaky-timing-Market M# was not suspended within #ms (still Open).
- **Recommendation:** Do not file as a product bug. Either loosen the assertion to match a trading-ops-confirmed SLA, or move latency validation out of the functional suite into a dedicated percentile/load test that tolerates the platform's real distribution of propagation times.

---
*Illustrative output — see [artifacts/sample-run/README.md](README.md) for how this was produced
and how to regenerate it for real.*
