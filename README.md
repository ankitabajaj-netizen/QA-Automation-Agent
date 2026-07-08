# QE Agents Demo — Red Card Suspends Betting Markets

A basic agentic QE pipeline (Test Planning → Test Generation → Test Execution → Defect Triaging)
built for one concrete story: when a soccer player is sent off, all open betting markets related
to them must be suspended. See [plan.md](plan.md) for the full design doc and rationale.

This is a **hybrid** project: the agents (Planning, Generation, Triage) are Python, using the real
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python). The system under test and the
executable test suite are C#/Reqnroll, as required. The Python Executor agent drives the C# suite
as a subprocess (`dotnet test`) — the same way a CI pipeline would.

## Layout

```
orchestrator/                 Python - the agents + pipeline (uses the real OpenAI Agents SDK)
  qe_agents/
    planner_agent.py            Agent(output_type=TestPlan)
    generator_agent.py          Agent() -> raw Gherkin text, allow-list checked before use
    executor_agent.py           no Agent - subprocess("dotnet test") + TRX parsing + rerun
    triage_agent.py             Agent(output_type=DefectReport)
  main.py                      pipeline entry point (human-in-the-loop gate, artifact writer)
  story/story.md               the input artifact (includes a live prompt-injection test case)
src/BettingPlatform/          C# - the "system under test": a tiny in-process fake with a planted bug
tests/QEAgents.Tests/         C# - Reqnroll (Gherkin) feature file + step definitions
artifacts/sample-run/         illustrative output of a run (see its own README)
plan.md                       design doc (architecture, tradeoffs, evaluation, what's next)
```

## Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) — runs the Reqnroll suite and the SUT.
- Python 3.10+.
- Optional: an OpenAI API key (`OPENAI_API_KEY` env var), for live Agents SDK calls. Without one,
  every agent runs in a fully deterministic **offline mode** using canned templates/heuristics —
  the whole pipeline still runs end to end, no credentials required.

## Run it

```bash
git clone <this-repo>
cd "QA Automation Agent"

pip install -r orchestrator/requirements.txt

# offline mode (no API key needed) - deterministic, reproducible
python orchestrator/main.py --auto

# live mode - actually calls OpenAI (via the Agents SDK) for Planning, Generation, and Triage
export OPENAI_API_KEY=sk-...
python orchestrator/main.py
# (omit --auto to hit the human-in-the-loop gate after the test plan is printed)
```

Each run writes to `artifacts/run-<timestamp>/`: `test_plan.md`/`.json`, `generated.feature`,
the raw TRX result files, and `defect_report.md`/`.json`. It also overwrites
`tests/QEAgents.Tests/Features/RedCardSuspendsMarkets.feature` with whatever the Generator agent
produced for that run.

To just run the generated test suite directly (skip the agent pipeline):

```bash
dotnet test tests/QEAgents.Tests
```

Expect roughly 4 of 6 scenarios to pass on a given run: one fails consistently (a planted
eligibility bug in `MarketSuspensionService`), one fails intermittently (a planted timing race,
about 1-in-3 runs) — see [plan.md](plan.md#system-under-test) for why, and
[artifacts/sample-run/](artifacts/sample-run/) for what the full pipeline's output looks like.

## A note on verification

This environment had Python and internet access but no .NET SDK and no `OPENAI_API_KEY`. What that
means concretely:
- The real `openai-agents` package was installed and the code was written and run against it
  directly (not from a remembered API shape) — `Agent`/`Runner`/`output_type` construction was
  verified to work as written.
- The full **offline** pipeline (Planner → Generator → Triage, in-process) was actually executed
  here and produces the expected output — 6 scenarios, 4 open questions, a feature file, and
  correct `RealDefect`/`Flaky` classifications on a synthetic execution summary.
- `python orchestrator/main.py --auto` was run for real. It completed Planning and Generation and
  failed cleanly at the `dotnet test` subprocess call with `FileNotFoundError` (no .NET SDK here) —
  confirming the pipeline is correct up to the one boundary this sandbox can't cross.
- **Not verified:** a live call to `gpt-4o-mini` (needs a real API key) and the actual `dotnet test`
  run against the Reqnroll suite (needs the .NET SDK). Both are the first things to check on a
  machine that has both — see [plan.md's Evaluation section](plan.md#evaluation--how-we-tested-the-tester)
  for exactly what "verified" vs. "unverified" means here.
