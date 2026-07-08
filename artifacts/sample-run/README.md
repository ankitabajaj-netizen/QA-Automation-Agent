# Sample run (illustrative)

This folder shows what `python orchestrator/main.py --auto` produces in **offline mode** (no
`OPENAI_API_KEY` set).

- `test_plan.md` / `test_plan.json` — exactly what `planner_agent._offline_plan()` emits (a static
  template) and what actually printed when the pipeline was run in this environment.
- `generated.feature` — exactly what `generator_agent.OFFLINE_FEATURE` emits, and byte-identical to
  the working copy the pipeline overwrote at
  [`tests/QEAgents.Tests/Features/RedCardSuspendsMarkets.feature`](../../tests/QEAgents.Tests/Features/RedCardSuspendsMarkets.feature).
- `defect_report.md` — **this one is a reasoned projection for the `dotnet test` step specifically**,
  not a template. This sandbox has no .NET SDK, so the real `dotnet test` run against
  `MarketSuspensionService` couldn't happen here (`main.py --auto` gets exactly this far before
  failing on the missing `dotnet` binary). What *was* verified directly: feeding
  `triage_agent.run(...)` a synthetic `ExecutionSummary` shaped like what this scenario would
  produce (one consistent failure, one rerun-passes failure) correctly yields the `RealDefect`
  (S1/P0) and `Flaky` (S3/P2) classifications shown here. Run it yourself with a .NET SDK installed
  to get the real numbers - see
  [Evaluation](../../plan.md#evaluation--how-we-tested-the-tester) for the full verification story.
