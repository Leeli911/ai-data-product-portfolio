"""Minimal public contracts for the Text2Analytics V2 Engine."""

from enum import Enum
from typing import Literal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PipelineStatus(str, Enum):
    """Stable status values returned by the Engine pipeline."""

    SUCCESS = "success"
    FAILED = "failed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class PipelineStage(str, Enum):
    """Inspectable stage names for the Engine pipeline."""

    INTENT = "intent"
    PLAN = "plan"
    SQL = "sql"
    VALIDATION = "validation"
    EXECUTION = "execution"
    INSIGHT = "insight"
    SCORING = "scoring"


class AnalyticsRequest(BaseModel):
    """Public request accepted by the Text2Analytics V2 Engine."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    dataset_id: str = "local_life_demo"


class Intent(BaseModel):
    """Canonical intent produced by the rule-based parser."""

    model_config = ConfigDict(extra="forbid")

    task_type: Literal[
        "change_explanation",
        "dimension_comparison",
        "top_n_ranking",
        "forecasting",
        "causal_inference",
        "recommendation",
        "follow_up",
        "cross_dataset",
        "unsupported",
    ]
    is_supported: bool
    metric: str | None = None
    dimension: str | None = None
    time_window: str | None = None
    comparison_window: str | None = None
    ranking: str | None = None
    ranking_n: int | None = None
    unsupported_reason: str | None = None


class AnalysisPlan(BaseModel):
    """Minimal analysis plan placeholder for early Engine stages."""

    model_config = ConfigDict(extra="forbid")

    steps: list[str] = Field(default_factory=list)


class AnalyticsResponse(BaseModel):
    """Public response shell with extension points for later modules."""

    model_config = ConfigDict(extra="forbid")

    status: PipelineStatus
    request: AnalyticsRequest
    pipeline: list[PipelineStage] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
