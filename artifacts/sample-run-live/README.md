# Sample run (live — genuine output, not a template)

Unlike [`artifacts/sample-run/`](../sample-run/) (offline mode, deterministic templates), everything
in this folder is real output from `python orchestrator/main.py --auto` with a real
`OPENAI_API_KEY` and a real `dotnet test` execution. See
[plan.md's Evaluation section](../../plan.md#evaluation--how-we-tested-the-tester) for the full
discussion — this README just indexes what's here.

- `test_plan.md` / `test_plan.json`, `generated.feature`, `defect_report.md` / `.json` — the full
  artifact set from one live run: 7 scenarios planned, 2 failed on first run, correctly deduped
  into **one** `RealDefect` (not called flaky) after the rerun check.
- `first-run-contradictory-scenario.feature` — from a *different* live run, kept because it's the
  most interesting finding across both: the Planner proposed a boundary case ("red card after
  betting period closes") that the Generator's fixed step vocabulary couldn't actually express, so
  it silently dropped the precondition and produced two scenarios with identical `Given`/`When`
  steps but contradictory `Then` assertions (compare the last scenario in this file against the
  first — same setup, opposite expected outcome for market `M1`). Both passed the step-vocabulary
  allow-list, because the allow-list checks phrasing, not logic. This is the top item in
  [plan.md's "What I'd build next"](../../plan.md#what-id-build-next).

Two things worth knowing before reading `defect_report.md` at face value:
- Its root cause ("Market M3 suspension timing issue") is a *plausible misdiagnosis* — the real
  cause is the planted eligibility-order bug, not latency. Triage only sees a timeout-shaped
  assertion message and has no way to tell "too slow" from "never happens" from that text alone.
- Its `severity`/`priority` values (`High`/`Critical`) deviate from the vocabulary the prompt asked
  for (`S1-S4`/`P0-P3`) — `output_type` enforces JSON shape, not string content within it.

Both are documented as known, evidenced gaps rather than silently accepted — see plan.md.
