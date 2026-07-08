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
NuGet.Config                  scopes this repo's restore to nuget.org only (see note below)
artifacts/sample-run/         illustrative offline-mode output (see its own README)
artifacts/sample-run-live/    genuine output from real live runs - see its own README
plan.md                       design doc (architecture, tradeoffs, evaluation, what's next)
```

## Prerequisites

- [.NET SDK](https://dotnet.microsoft.com/download/dotnet) (the projects target `net10.0`; if
  you're on .NET 8, retarget the two `.csproj` files under `src/`/`tests/` accordingly) — runs the
  Reqnroll suite and the SUT.
- Python 3.10+.
- Optional: an OpenAI API key, for live Agents SDK calls. Without one, every agent runs in a fully
  deterministic **offline mode** using canned templates/heuristics — the whole pipeline still runs
  end to end, no credentials required. To set the key:
  - Simplest: `export OPENAI_API_KEY=sk-...` (or `$env:OPENAI_API_KEY = "sk-..."` in PowerShell)
    before running.
  - Or copy `orchestrator/.env.example` to `orchestrator/.env` and fill in your key — `main.py`
    loads it automatically via `python-dotenv` (a real shell env var always takes precedence).
    `.env` is gitignored; never commit it.

**If `dotnet test`/`dotnet build` fails with `NU1301` errors about an unreachable source:** that's
a machine-wide NuGet config (e.g. a private org feed or a local folder path) that doesn't exist on
your machine. The `NuGet.Config` at the repo root should already scope this project to `nuget.org`
only, regardless of what else is configured globally — if you still see this, check nothing is
overriding it further down the directory tree.

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

In **offline mode**, expect 4 of 6 scenarios to pass: one fails consistently (a planted eligibility
bug in `MarketSuspensionService`), one fails intermittently (a planted timing race, about 1-in-3
runs) — see [plan.md](plan.md#system-under-test) for why, and [artifacts/sample-run/](artifacts/sample-run/)
for the full offline output. **In live mode, the Planner/Generator regenerate scenarios each run**,
so the exact numbers vary — see [artifacts/sample-run-live/](artifacts/sample-run-live/) for real
examples and [plan.md's Evaluation section](plan.md#evaluation--how-we-tested-the-tester) for what
that variation actually surfaced.

### Exact commands verified on this checkout (PowerShell)

The commands above are the general clone-and-run form. These are the literal commands actually
run and confirmed working on this machine, against this existing checkout — useful if you hit any
path/cwd confusion:

```powershell
# .NET side - from the repo root
cd "c:\Projects\QA Automation Agent"
dotnet test tests\QEAgents.Tests

# Python side - run from inside orchestrator\ (main.py locates everything via its own
# file path, so this works the same whether you run it from here or from the repo root
# as `python orchestrator\main.py --auto` - use whichever matches your cwd)
cd "c:\Projects\QA Automation Agent\orchestrator"
python main.py --auto
```

For live mode, either set the key first (`$env:OPENAI_API_KEY = "sk-..."`) or drop it into
`orchestrator\.env` (see Prerequisites above) and drop `--auto` from the second command if you
want the human-in-the-loop pause.

## A note on verification

This was built and verified across two environments: one with Python but no .NET SDK and no API
key (offline-mode verification only), and a follow-up with both a real `OPENAI_API_KEY` and the
.NET SDK, where the pipeline was run live, twice, end to end.

**Verified live** (not just offline): both live runs completed Planning → Generation → Execution →
Triage against a real `dotnet test` run; the prompt-injection payload in `story.md` did not work in
either run (no leaked data, no skipped planning, plausible on-topic scenarios both times); the
rerun-based flaky-vs-real distinction and defect dedup both worked correctly. The live runs also
surfaced two genuine gaps — a scenario-generation case the step-vocabulary allow-list doesn't catch,
and a root-cause narrative that's a plausible misdiagnosis given the available error text — both
written up with real examples in [plan.md's Evaluation section](plan.md#evaluation--how-we-tested-the-tester)
and [artifacts/sample-run-live/](artifacts/sample-run-live/), and now the top items in
[What I'd build next](plan.md#what-id-build-next).
