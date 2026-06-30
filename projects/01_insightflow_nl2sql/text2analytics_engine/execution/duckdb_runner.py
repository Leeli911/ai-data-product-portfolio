"""DuckDB runner for executing generated Text2Analytics SQL."""

from typing import Any

from text2analytics_engine.execution.contracts import (
    ExecutionArtifact,
    ExecutionResult,
)
from text2analytics_engine.execution.database import initialize_duckdb
from text2analytics_engine.sql import GeneratedQuery


def _base_metadata(generated_query: GeneratedQuery) -> dict[str, Any]:
    return {
        "backend": "duckdb",
        "query_id": generated_query.query_id,
        "query_type": generated_query.query_type,
        "required_tables": generated_query.required_tables,
        "required_columns": generated_query.required_columns,
    }


def _rows_to_dicts(columns: list[str], rows: list[tuple[Any, ...]]):
    return [
        {
            column: value
            for column, value in zip(columns, row, strict=True)
        }
        for row in rows
    ]


def _artifact_type(
    generated_query: GeneratedQuery,
    columns: list[str],
    row_count: int,
) -> str:
    if generated_query.query_type == "ranking":
        return "ranking"
    if row_count == 1 and len(columns) == 1:
        return "scalar"
    return "table"


def run_query(generated_query: GeneratedQuery) -> ExecutionResult:
    """Execute a GeneratedQuery in DuckDB and return an ExecutionResult."""
    if not isinstance(generated_query, GeneratedQuery):
        raise TypeError("run_query expects a GeneratedQuery instance")

    connection = None
    try:
        connection = initialize_duckdb()
        cursor = connection.execute(generated_query.sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        row_count = len(rows)
        artifact_type = _artifact_type(generated_query, columns, row_count)
        data = (
            _rows_to_dicts(columns, rows)[0]
            if artifact_type == "scalar"
            else _rows_to_dicts(columns, rows)
        )

        metadata = {
            **_base_metadata(generated_query),
            "row_count": row_count,
        }
        artifact_metadata = {
            "columns": columns,
            "row_count": row_count,
            "query_id": generated_query.query_id,
        }

        if row_count == 0:
            metadata["insufficient_evidence"] = True
            artifact_metadata["insufficient_evidence"] = True

        return ExecutionResult(
            execution_status="partial" if row_count == 0 else "success",
            artifacts=[
                ExecutionArtifact(
                    artifact_id=generated_query.query_id,
                    artifact_type=artifact_type,
                    data=data,
                    metadata=artifact_metadata,
                )
            ],
            metadata=metadata,
        )
    except Exception as exc:
        return ExecutionResult(
            execution_status="failed",
            artifacts=[],
            metadata={
                **_base_metadata(generated_query),
                "error": str(exc),
            },
        )
    finally:
        if connection is not None:
            connection.close()
