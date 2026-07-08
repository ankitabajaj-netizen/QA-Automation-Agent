"""QE Agents pipeline: Red Card -> Suspended Markets.

Test Planning -> Test Generation -> Test Execution -> Defect Triaging, end to end, for one story.
See plan.md for the design rationale.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from qe_agents import executor_agent, generator_agent, planner_agent, triage_agent
from qe_agents.models import DefectReport, ExecutionSummary, TestPlan

THIS_DIR = Path(__file__).resolve().parent


def _find_repo_root(start_dir: Path) -> Path:
    current = start_dir
    while current != current.parent:
        if (current / "plan.md").exists():
            return current
        current = current.parent
    return start_dir


def _write_test_plan_artifact(artifacts_dir: Path, plan: TestPlan) -> None:
    lines = [f"# Test Plan: {plan.feature_name}", "", "## Scenarios",
              "| ID | Priority | Type | Title | Rationale |", "|----|----------|------|-------|-----------|"]
    for s in plan.scenarios:
        lines.append(f"| {s.id} | {s.priority} | {s.type} | {s.title} | {s.rationale} |")
    lines += ["", "## Open Questions / Ambiguities"]
    lines += [f"- {q}" for q in plan.open_questions]
    lines += ["", "## Entry Criteria"]
    lines += [f"- {e}" for e in plan.entry_criteria]
    lines += ["", "## Exit Criteria"]
    lines += [f"- {e}" for e in plan.exit_criteria]
    (artifacts_dir / "test_plan.md").write_text("\n".join(lines), encoding="utf-8")


def _write_defect_report_artifact(artifacts_dir: Path, execution: ExecutionSummary, report: DefectReport) -> None:
    lines = ["# Defect Report", "", f"Execution: {execution.passed_count}/{execution.total} passed on first run.", ""]
    if not report.defects:
        lines.append("No defects - all scenarios passed.")
    for d in report.defects:
        lines += [
            f"## {d.title}",
            f"- **Classification:** {d.classification}",
            f"- **Severity/Priority:** {d.severity} / {d.priority}",
            f"- **Likely root cause:** {d.likely_root_cause}",
            f"- **Suggested owner:** {d.suggested_owner}",
            f"- **Affected scenarios:** {', '.join(d.affected_scenarios)}",
            f"- **Dedup key:** {d.dedup_key}",
            f"- **Recommendation:** {d.recommendation}",
            "",
        ]
    (artifacts_dir / "defect_report.md").write_text("\n".join(lines), encoding="utf-8")


async def main() -> None:
    auto_mode = "--auto" in sys.argv

    repo_root = _find_repo_root(THIS_DIR)
    artifacts_dir = repo_root / "artifacts" / f"run-{datetime.now():%Y%m%d-%H%M%S}"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    print("=== QE Agents Pipeline: Red Card -> Suspended Markets ===")
    print(
        "Mode: OFFLINE (OPENAI_API_KEY not set) - agents use deterministic templates/heuristics."
        if not api_key_present
        else "Mode: LIVE (calling OpenAI via the Agents SDK)."
    )

    story = (THIS_DIR / "story" / "story.md").read_text(encoding="utf-8")

    # ---- 1. Test Planning ----
    plan = await planner_agent.run(story)
    _write_test_plan_artifact(artifacts_dir, plan)
    (artifacts_dir / "test_plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    print(f"\n[Plan] {len(plan.scenarios)} scenario(s) planned. {len(plan.open_questions)} open question(s) surfaced:")
    for q in plan.open_questions:
        print(f"  - {q}")

    if not auto_mode:
        print(f"\nReview {artifacts_dir / 'test_plan.md'}.")
        print("Press Enter to continue to test generation (human-in-the-loop gate), or Ctrl+C to stop.")
        input()

    # ---- 2. Test Generation ----
    feature_text = await generator_agent.run(plan)

    tests_project_dir = repo_root / "tests" / "QEAgents.Tests"
    feature_path = tests_project_dir / "Features" / "RedCardSuspendsMarkets.feature"
    feature_path.write_text(feature_text, encoding="utf-8")
    (artifacts_dir / "generated.feature").write_text(feature_text, encoding="utf-8")
    print(f"\n[Generate] Feature file written to {feature_path}")

    # ---- 3. Test Execution ----
    test_project_path = tests_project_dir / "QEAgents.Tests.csproj"
    print("\n[Execute] Running dotnet test in a sandboxed subprocess (5 min timeout)...")
    execution = await executor_agent.run(test_project_path, artifacts_dir)
    print(f"[Execute] {execution.passed_count}/{execution.total} scenario(s) passed on first run.")

    # ---- 4. Defect Triage ----
    report = await triage_agent.run(execution)
    _write_defect_report_artifact(artifacts_dir, execution, report)
    (artifacts_dir / "defect_report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")

    print(f"\n[Triage] {len(report.defects)} defect(s) filed:")
    for d in report.defects:
        print(f"  - [{d.classification}] {d.title} (Severity {d.severity}, Priority {d.priority}) -> {d.suggested_owner}")

    print(f"\nAll artifacts written to: {artifacts_dir}")


if __name__ == "__main__":
    asyncio.run(main())
