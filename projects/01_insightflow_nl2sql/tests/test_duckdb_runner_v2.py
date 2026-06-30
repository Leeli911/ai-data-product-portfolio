import pytest

from text2analytics_engine.contracts import Intent
from text2analytics_engine.execution import ExecutionRequest
from text2analytics_engine.execution.database import initialize_duckdb
from text2analytics_engine.execution.duckdb_runner import run_query
from text2analytics_engine.planning import plan_from_intent
from text2analytics_engine.sql import GeneratedQuery, generate_query


def _request_from_intent(intent):
    plan = plan_from_intent(intent)
    return ExecutionRequest(
        plan_id=plan.plan_id,
        task_type=plan.task_type,
        required_metrics=[
            item.metric_id for item in plan.required_metrics
        ],
        required_dimensions=[
            item.dimension_id for item in plan.required_dimensions
        ],
        required_time_windows=[
            item.time_window_id for item in plan.required_time_windows
        ],
        execution_targets=[
            artifact.artifact_id for artifact in plan.expected_outputs
        ],
    )


def _change_query():
    return generate_query(
        _request_from_intent(
            Intent(
                task_type="change_explanation",
                is_supported=True,
                metric="metric_gmv",
                dimension="dimension_district",
                time_window="time_window_this_week",
                comparison_window="comparison_week_over_week",
            )
        )
    )


def _comparison_query():
    return generate_query(
        _request_from_intent(
            Intent(
                task_type="dimension_comparison",
                is_supported=True,
                metric="metric_gmv",
                dimension="dimension_district",
                time_window="time_window_this_week",
            )
        )
    )


def _ranking_query():
    return generate_query(
        _request_from_intent(
            Intent(
                task_type="top_n_ranking",
                is_supported=True,
                metric="metric_orders",
                dimension="dimension_district",
                time_window="time_window_this_week",
                ranking="ranking_top_n",
                ranking_n=5,
            )
        )
    )


def test_database_initializes_local_life_transactions_view():
    connection = initialize_duckdb()

    try:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM local_life_transactions"
        ).fetchone()[0]
    finally:
        connection.close()

    assert row_count > 0


def test_runner_executes_change_explanation_query():
    result = run_query(_change_query())

    assert result.execution_status == "success"
    assert result.metadata["row_count"] == 2
    artifact = result.artifacts[0]
    assert artifact.artifact_type == "table"
    assert artifact.metadata["columns"] == [
        "period",
        "metric_gmv",
        "metric_orders",
        "metric_aov",
    ]
    assert len(artifact.data) == 2


def test_runner_executes_dimension_comparison_query():
    result = run_query(_comparison_query())

    assert result.execution_status == "success"
    artifact = result.artifacts[0]
    assert artifact.artifact_type == "table"
    assert artifact.metadata["row_count"] > 0
    assert set(artifact.data[0]) == {"district", "metric_value"}


def test_runner_executes_top_n_ranking_query():
    result = run_query(_ranking_query())

    assert result.execution_status == "success"
    artifact = result.artifacts[0]
    assert artifact.artifact_type == "ranking"
    assert 0 < len(artifact.data) <= 5
    assert set(artifact.data[0]) == {"district", "metric_value"}


def test_runner_can_return_scalar_artifact():
    query = GeneratedQuery(
        query_id="query_scalar_smoke_v1",
        task_type="dimension_comparison",
        sql=(
            "SELECT SUM(gmv) AS metric_value "
            "FROM local_life_transactions "
            "GROUP BY city "
            "ORDER BY metric_value DESC "
            "LIMIT 1"
        ),
        required_tables=["local_life_transactions"],
        required_columns=["gmv", "city"],
        query_type="dimension_aggregation",
    )

    result = run_query(query)

    assert result.execution_status == "success"
    artifact = result.artifacts[0]
    assert artifact.artifact_type == "scalar"
    assert set(artifact.data) == {"metric_value"}


def test_runner_returns_failed_result_for_sql_execution_failure():
    query = GeneratedQuery(
        query_id="query_invalid_column_v1",
        task_type="dimension_comparison",
        sql=(
            "SELECT missing_column "
            "FROM local_life_transactions "
            "GROUP BY missing_column "
            "ORDER BY missing_column "
            "LIMIT 1"
        ),
        required_tables=["local_life_transactions"],
        required_columns=["missing_column"],
        query_type="dimension_aggregation",
    )

    result = run_query(query)

    assert result.execution_status == "failed"
    assert result.artifacts == []
    assert result.metadata["query_id"] == "query_invalid_column_v1"
    assert "missing_column" in result.metadata["error"]


def test_runner_returns_empty_artifact_with_insufficient_evidence_metadata():
    query = GeneratedQuery(
        query_id="query_empty_result_v1",
        task_type="dimension_comparison",
        sql=(
            "SELECT district, SUM(gmv) AS metric_value "
            "FROM local_life_transactions "
            "GROUP BY district "
            "ORDER BY metric_value DESC "
            "LIMIT 0"
        ),
        required_tables=["local_life_transactions"],
        required_columns=["district", "gmv"],
        query_type="dimension_aggregation",
    )

    result = run_query(query)

    assert result.execution_status == "partial"
    assert result.metadata["insufficient_evidence"] is True
    artifact = result.artifacts[0]
    assert artifact.data == []
    assert artifact.metadata["insufficient_evidence"] is True


def test_runner_rejects_raw_sql_input():
    with pytest.raises(TypeError, match="GeneratedQuery"):
        run_query("SELECT * FROM local_life_transactions")
