"""Typed contracts passed between pipeline stages.

Using pydantic models as `Agent(output_type=...)` gets us the real Agents SDK's structured-output
enforcement for free - the model is constrained to this schema at the API level, not just asked
nicely in a prompt. See plan.md, "Framework and model choice".
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RiskScenario(BaseModel):
    id: str
    title: str
    priority: str  # P0 | P1 | P2
    type: str  # Positive | Negative | Boundary | Edge
    rationale: str


class TestPlan(BaseModel):
    feature_name: str
    scenarios: list[RiskScenario]
    open_questions: list[str]
    entry_criteria: list[str]
    exit_criteria: list[str]


class ScenarioResult(BaseModel):
    name: str
    passed_first_run: bool
    passed_rerun: Optional[bool] = None  # None if never rerun (only reruns failures)
    error_message: Optional[str] = None


class ExecutionSummary(BaseModel):
    total: int = 0
    passed_count: int = 0
    failed_count: int = 0
    results: list[ScenarioResult] = Field(default_factory=list)


class Defect(BaseModel):
    title: str
    classification: str  # RealDefect | Flaky | TestIssue
    severity: str
    priority: str
    likely_root_cause: str
    suggested_owner: str
    affected_scenarios: list[str]
    dedup_key: str
    recommendation: str


class DefectReport(BaseModel):
    defects: list[Defect] = Field(default_factory=list)
