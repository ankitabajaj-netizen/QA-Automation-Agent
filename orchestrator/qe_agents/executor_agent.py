"""Test Execution: runs the Reqnroll suite as an isolated subprocess, parses TRX results, and
reruns any first-run failures once to get a deterministic flaky-vs-consistent signal for the
Triage agent.

No LLM call in this stage at all - a deliberate omission, not an oversight. Running a fixed
program and reporting what happened is not a reasoning task; using a model here would add cost,
latency, and a new source of non-determinism to something that's already fully deterministic and
cheap to do with a subprocess. See plan.md, "Why Execution has no model call".
"""

from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from qe_agents.models import ExecutionSummary, ScenarioResult

DEFAULT_TIMEOUT_SECONDS = 300


async def run(test_project_path: Path, artifacts_dir: Path, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> ExecutionSummary:
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    first_run = _run_dotnet_test(test_project_path, artifacts_dir, filter_expr=None, trx_name="run1.trx", timeout_seconds=timeout_seconds)

    summary = ExecutionSummary()
    for name, passed, error in first_run:
        summary.results.append(ScenarioResult(name=name, passed_first_run=passed, error_message=error))

    failed = [r for r in summary.results if not r.passed_first_run]
    if failed:
        print(f"[Executor] {len(failed)} scenario(s) failed on first run - rerunning each once to check for flakiness.")
        for scenario in failed:
            sanitized = _sanitize(scenario.name)
            rerun = _run_dotnet_test(
                test_project_path, artifacts_dir,
                filter_expr=f"Name~{sanitized}", trx_name=f"rerun_{sanitized}.trx",
                timeout_seconds=timeout_seconds,
            )
            if rerun:
                scenario.passed_rerun = rerun[0][1]
            else:
                print(f"[Executor] Could not isolate scenario '{scenario.name}' for rerun (filter matched nothing); leaving flaky signal unknown.")

    summary.total = len(summary.results)
    summary.passed_count = sum(1 for r in summary.results if r.passed_first_run)
    summary.failed_count = summary.total - summary.passed_count
    return summary


def _run_dotnet_test(
    test_project_path: Path, artifacts_dir: Path, filter_expr: str | None, trx_name: str, timeout_seconds: int
) -> list[tuple[str, bool, str | None]]:
    args = [
        "dotnet", "test", str(test_project_path),
        "--logger", f"trx;LogFileName={trx_name}",
        "--results-directory", str(artifacts_dir),
    ]
    if filter_expr:
        args += ["--filter", filter_expr]

    try:
        subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,  # dotnet test returns non-zero on test failure; that's expected, not an error
        )
    except subprocess.TimeoutExpired:
        print(f"[Executor] dotnet test exceeded the sandbox timeout ({timeout_seconds}s) and was killed.")
    except FileNotFoundError as ex:
        raise RuntimeError(
            "Could not find the 'dotnet' executable. Install the .NET 8 SDK "
            "(https://dotnet.microsoft.com/download/dotnet/8.0) and ensure it's on PATH."
        ) from ex

    trx_path = artifacts_dir / trx_name
    return _parse_trx(trx_path) if trx_path.exists() else []


def _parse_trx(trx_path: Path) -> list[tuple[str, bool, str | None]]:
    tree = ET.parse(trx_path)
    root = tree.getroot()
    ns_match = re.match(r"\{(.*)\}", root.tag)
    ns = {"t": ns_match.group(1)} if ns_match else {"t": ""}

    results: list[tuple[str, bool, str | None]] = []
    for unit_test_result in root.iter(f"{{{ns['t']}}}UnitTestResult" if ns["t"] else "UnitTestResult"):
        name = unit_test_result.get("testName", "Unknown")
        outcome = unit_test_result.get("outcome", "Failed")
        passed = outcome.lower() == "passed"

        message = None
        if not passed:
            message_el = unit_test_result.find(f".//{{{ns['t']}}}Message" if ns["t"] else ".//Message")
            stack_el = unit_test_result.find(f".//{{{ns['t']}}}StackTrace" if ns["t"] else ".//StackTrace")
            message = (message_el.text if message_el is not None else None) or (stack_el.text if stack_el is not None else None)

        results.append((name, passed, message))

    return results


def _sanitize(name: str) -> str:
    return name.replace('"', "").strip()
