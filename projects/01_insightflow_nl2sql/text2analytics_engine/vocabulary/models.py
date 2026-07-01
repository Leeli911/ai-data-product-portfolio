"""Pydantic vocabulary models for Text2Analytics V2 runtime."""

from pydantic import BaseModel, ConfigDict, Field


class MetricTerm(BaseModel):
    """Canonical metric vocabulary term."""

    model_config = ConfigDict(frozen=True)

    metric_id: str
    display_name: str
    aliases: tuple[str, ...] = Field(default_factory=tuple)
    definition: str
    aggregation_type: str
    unit: str


class DimensionTerm(BaseModel):
    """Canonical dimension vocabulary term."""

    model_config = ConfigDict(frozen=True)

    dimension_id: str
    aliases: tuple[str, ...] = Field(default_factory=tuple)
    supported_filters: tuple[str, ...] = Field(default_factory=tuple)


class TimeWindowTerm(BaseModel):
    """Canonical time-window vocabulary term."""

    model_config = ConfigDict(frozen=True)

    time_window_id: str
    aliases: tuple[str, ...] = Field(default_factory=tuple)
    definition: str


class ComparisonTerm(BaseModel):
    """Canonical comparison vocabulary term."""

    model_config = ConfigDict(frozen=True)

    comparison_id: str
    aliases: tuple[str, ...] = Field(default_factory=tuple)
    definition: str


class RankingTerm(BaseModel):
    """Canonical ranking vocabulary term."""

    model_config = ConfigDict(frozen=True)

    ranking_id: str
    aliases: tuple[str, ...] = Field(default_factory=tuple)
    definition: str
