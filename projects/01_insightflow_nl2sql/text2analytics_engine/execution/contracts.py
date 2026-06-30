"""Execution layer contracts for Text2Analytics V2.

These models define the boundary between deterministic planning and a future
execution implementation. They intentionally do not encode SQL, DuckDB, or
backend-specific execution details.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionRequest(BaseModel):
    """Planner-to-execution request using canonical runtime identifiers."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(min_length=1)
    task_type: Literal[
        "change_explanation",
        "dimension_comparison",
        "top_n_ranking",
    ]
    required_metrics: list[str] = Field(default_factory=list)
    required_dimensions: list[str] = Field(default_factory=list)
    required_time_windows: list[str] = Field(default_factory=list)
    execution_targets: list[str] = Field(default_factory=list)


class ExecutionArtifact(BaseModel):
    """A backend-agnostic artifact produced by execution."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    artifact_type: Literal["scalar", "table", "ranking", "series"]
    data: Any
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Execution output shell consumed by later insight and scoring stages."""

    model_config = ConfigDict(extra="forbid")

    artifacts: list[ExecutionArtifact] = Field(default_factory=list)
    execution_status: Literal["success", "failed", "partial"]
    metadata: dict[str, Any] = Field(default_factory=dict)
