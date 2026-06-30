"""Runtime SQL models for Text2Analytics V2."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeneratedQuery(BaseModel):
    """A deterministic, backend-agnostic SQL query artifact."""

    model_config = ConfigDict(extra="forbid")

    query_id: str = Field(min_length=1)
    task_type: Literal[
        "change_explanation",
        "dimension_comparison",
        "top_n_ranking",
    ]
    sql: str = Field(min_length=1)
    required_tables: list[str] = Field(default_factory=list)
    required_columns: list[str] = Field(default_factory=list)
    query_type: Literal[
        "period_aggregation",
        "dimension_aggregation",
        "ranking",
    ]

    @field_validator("sql")
    @classmethod
    def validate_read_only_single_statement(cls, value: str) -> str:
        """Keep generated runtime queries read-only and single-statement."""
        normalized = value.upper()
        padded = f" {normalized} "

        if not normalized.startswith("SELECT "):
            raise ValueError("generated SQL must start with SELECT")
        if ";" in value:
            raise ValueError("generated SQL must be a single statement")
        for keyword in (" UPDATE ", " DELETE ", " INSERT ", " DROP "):
            if keyword in padded:
                raise ValueError(
                    "generated SQL must not contain mutation keywords"
                )

        return value
