"""Runtime data models for Text2Analytics V2 Analysis Planner."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RequiredMetric(BaseModel):
    """A canonical metric required by an analysis plan."""

    model_config = ConfigDict(extra="forbid")

    metric_id: str = Field(min_length=1)


class RequiredDimension(BaseModel):
    """A canonical dimension required by an analysis plan."""

    model_config = ConfigDict(extra="forbid")

    dimension_id: str = Field(min_length=1)


class RequiredTimeWindow(BaseModel):
    """A canonical time window required by an analysis plan."""

    model_config = ConfigDict(extra="forbid")

    time_window_id: str = Field(min_length=1)


class ExpectedArtifact(BaseModel):
    """A named artifact expected from a plan or step."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)


class AnalysisStep(BaseModel):
    """One ordered, inspectable analysis step."""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    expected_artifacts: list[ExpectedArtifact] = Field(default_factory=list)
    validation_requirements: list[str] = Field(default_factory=list)


class AnalysisPlan(BaseModel):
    """Runtime representation of a deterministic analysis plan."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(min_length=1)
    task_type: Literal[
        "change_explanation",
        "dimension_comparison",
        "top_n_ranking",
    ]
    objective: str = Field(min_length=1)
    ordered_steps: list[AnalysisStep] = Field(default_factory=list)
    required_metrics: list[RequiredMetric] = Field(default_factory=list)
    required_dimensions: list[RequiredDimension] = Field(default_factory=list)
    required_time_windows: list[RequiredTimeWindow] = Field(
        default_factory=list
    )
    expected_outputs: list[ExpectedArtifact] = Field(default_factory=list)
