# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A QE Agents demo: an agentic pipeline (Test Planning → Test Generation → Test Execution → Defect
Triaging) for one story — a soccer wagering platform must suspend all betting markets related to a
player the moment that player receives a red card. Full design rationale is in `plan.md`; this file
is only the operational summary for working in the code.

**Hybrid architecture, intentionally:** the four agents are Python (`orchestrator/`), using the real
`openai-agents` SDK. The system under test and the executable test suite are C# (`src/`, `tests/`),
using Reqnroll. The seam is `orchestrator/qe_agents/executor_agent.py`, which shells out to
`dotnet test` — there is no LLM call in that stage at all, by design (see plan.md).

## Commands

```bash
# install Python deps
pip install -r orchestrator/requirements.txt

# run the full agent pipeline, offline mode (no API key needed, deterministic)
cd orchestrator && python main.py --auto

# run live (set the key first, either way):
#   $env:OPENAI_API_KEY = "sk-..."          (PowerShell)
#   or copy orchestrator/.env.example -> orchestrator/.env and fill it in
cd orchestrator && python main.py            # omit --auto to hit the human-in-the-loop gate

# syntax-check the Python side without running it
cd orchestrator && python -m py_compile main.py qe_agents/*.py

# run just the C# test suite directly (skip the agent pipeline), from repo root
dotnet test tests/QEAgents.Tests

# run/rerun a single scenario by name substring
dotnet test tests/QEAgents.Tests --filter "Name~<partial scenario name>"
```

There is no lint/format tooling configured for either language in this repo.

## Architecture

**Pipeline is a straight sequential chain**, not a graph: `planner_agent.run()` →
`generator_agent.run()` → `executor_agent.run()` → `triage_agent.run()`, called explicitly in
`orchestrator/main.py`. No SDK `handoffs`, no tool-calling loops — each stage is one bounded
transformation. See plan.md's Architecture section for why this was chosen over LangGraph/handoffs.

**Every LLM-backed agent has a deterministic offline fallback**, used automatically whenever
`OPENAI_API_KEY` is unset (checked per-agent via `os.getenv`, not centrally). This is what makes
`python main.py --auto` reproducible with zero credentials — `planner_agent._offline_plan()`,
`generator_agent.OFFLINE_FEATURE`, `triage_agent._offline_triage()` are the fallback entry points.
When editing an agent's prompt/schema, keep the offline fallback in sync or the two modes diverge.

**The Generator only ever emits Gherkin text, never executable code.** Step definitions
(`tests/QEAgents.Tests/Steps/RedCardSuspensionSteps.cs`) are hand-authored and fixed; the Generator
is constrained by prompt to a published step-phrase vocabulary (see `STEP_VOCABULARY` in
`generator_agent.py`) and its output is checked against a line-prefix allow-list
(`_uses_only_known_steps`) before it's ever written to disk. **Known gap, evidenced by a live run**:
this allow-list catches invented step *phrasing* but not invented *logic* — a generated feature can
still contain two scenarios with identical `Given`/`When` and contradictory `Then` assertions if the
Planner proposes a scenario the fixed vocabulary can't faithfully express. See plan.md's Evaluation
section and `artifacts/sample-run-live/` for a real example before changing this area.

**The Executor reruns every first-run failure exactly once** (isolated via `dotnet test --filter`)
to produce a `passed_rerun: true/false/null` signal, which Triage is instructed to trust rather than
re-derive flakiness from the error text itself. This is the mechanism that separates "real defect"
from "flaky" — don't let Triage's prompt second-guess it.

**The system under test** (`src/BettingPlatform/MarketSuspensionService.cs`) has two intentional
defects, matched to specific test scenarios — do not "fix" them as an incidental cleanup:
1. `HandleRedCardAsync` only checks `EligiblePlayerIds[0]`, so multi-selection markets (e.g.
   "Anytime Assist Provider") only suspend correctly if the carded player happens to be listed
   first.
2. A random 0–150ms delay simulates async propagation; one scenario checks a tight 100ms budget
   with no polling tolerance, which fails intermittently by design (~1-in-3 runs) to exercise the
   flaky-detection path.

**`orchestrator/main.py` locates the repo root by walking up from its own file location looking for
`plan.md`** — don't move `plan.md` out of the repo root without updating `_find_repo_root`.

## Repo-specific environment notes

- `NuGet.Config` at the repo root clears and resets package sources to `nuget.org` only. This repo
  was built on a machine with a stale machine-wide NuGet config pointing at an unreachable private
  feed and local folder; if `dotnet test`/`build` ever fails with `NU1301`, check this file is still
  being picked up rather than overridden.
- The `.csproj` files target `net10.0` (retargeted from `net8.0` to match the .NET runtime actually
  installed during development — see README's Prerequisites for the tradeoff).
- `orchestrator/.env` (gitignored, template at `orchestrator/.env.example`) is loaded via
  `python-dotenv` in `main.py`; a real shell env var always takes precedence over it.

## Where the rest of the context lives

- `README.md` — clone-and-run instructions, prerequisites, verified exact commands.
- `plan.md` — full design doc: architecture rationale, framework/model choice, per-stage design,
  safety, and an **Evaluation section with real findings from live runs** (not just offline
  reasoning) — read this before assuming something is untested.
- `artifacts/sample-run/` vs `artifacts/sample-run-live/` — offline-mode template output vs. real
  output from live runs (including a feature file with a genuine self-contradictory scenario found
  in practice).
