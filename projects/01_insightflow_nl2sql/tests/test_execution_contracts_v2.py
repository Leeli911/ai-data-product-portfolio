import pytest
from pydantic import ValidationError

from text2analytics_engine.contracts import Intent
from text2analytics_engine.execution.contracts import (
    ExecutionArtifact,
    ExecutionRequest,
    ExecutionResult,
)
from text2analytics_engine.planning import plan_from_intent


def _request_from_plan(plan):
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


def _change_plan():
    intent = Intent(
        task_type="change_explanation",
        is_supported=True,
        metric="metric_gmv",
        dimension="dimension_district",
        time_window="time_window_this_week",
        comparison_window="comparison_week_over_week",
    )
    return plan_from_intent(intent)


def _comparison_plan():
    intent = Intent(
        task_type="dimension_comparison",
        is_supported=True,
        metric="metric_gmv",
        dimension="dimension_district",
        time_window="time_window_this_week",
    )
    return plan_from_intent(intent)


def _ranking_plan():
    intent = Intent(
        task_type="top_n_ranking",
        is_supported=True,
        metric="metric_orders",
        dimension="dimension_district",
        time_window="time_window_this_week",
        ranking="ranking_bottom_n",
        ranking_n=5,
    )
    return plan_from_intent(intent)


@pytest.mark.parametrize(
    "plan_factory",
    [_change_plan, _comparison_plan, _ranking_plan],
)
def test_execution_request_can_represent_planner_output(plan_factory):
    plan = plan_factory()
    request = _request_from_plan(plan)

    assert request.plan_id == plan.plan_id
    assert request.task_type == plan.task_type
    assert request.required_metrics == [
        item.metric_id for item in plan.required_metrics
    ]
    assert request.required_dimensions == [
        item.dimension_id for item in plan.required_dimensions
    ]
    assert request.required_time_windows == [
        item.time_window_id for item in plan.required_time_windows
    ]
    assert request.execution_targets == [
        artifact.artifact_id for artifact in plan.expected_outputs
    ]


def test_execution_artifact_can_represent_supported_artifact_shapes():
    scalar = ExecutionArtifact(
        artifact_id="current_metric_value",
        artifact_type="scalar",
        data={"metric_id": "metric_gmv", "value": 120000},
    )
    table = ExecutionArtifact(
        artifact_id="dimension_metric_table",
        artifact_type="table",
        data=[
            {"dimension_district": "Chaoyang", "metric_gmv": 120000},
            {"dimension_district": "Haidian", "metric_gmv": 98000},
        ],
    )
    ranking = ExecutionArtifact(
        artifact_id="ranked_dimension_table",
        artifact_type="ranking",
        data=[
            {"rank": 1, "dimension_district": "Chaoyang"},
            {"rank": 2, "dimension_district": "Haidian"},
        ],
    )
    series = ExecutionArtifact(
        artifact_id="metric_time_series",
        artifact_type="series",
        data=[
            {"time_window": "time_window_this_week", "metric_gmv": 120000},
            {"time_window": "time_window_last_week", "metric_gmv": 150000},
        ],
    )

    assert [
        artifact.artifact_type
        for artifact in [scalar, table, ranking, series]
    ] == ["scalar", "table", "ranking", "series"]


def test_execution_result_collects_artifacts_status_and_metadata():
    result = ExecutionResult(
        execution_status="success",
        artifacts=[
            ExecutionArtifact(
                artifact_id="metric_change_summary",
                artifact_type="scalar",
                data={"change_rate": -0.2},
            )
        ],
        metadata={"plan_id": "plan_change_explanation_v1"},
    )

    assert result.execution_status == "success"
    assert result.artifacts[0].artifact_id == "metric_change_summary"
    assert result.metadata["plan_id"] == "plan_change_explanation_v1"


def test_execution_contracts_do_not_bind_to_sql_or_duckdb():
    request = _request_from_plan(_change_plan())
    result = ExecutionResult(
        execution_status="success",
        artifacts=[
            ExecutionArtifact(
                artifact_id="metric_change_summary",
                artifact_type="scalar",
                data={"change_rate": -0.2},
            )
        ],
    )

    dumped = {
        "request": request.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
    }

    assert "sql" not in dumped
    assert "query" not in dumped
    assert "duckdb" not in dumped


def test_execution_artifact_rejects_unknown_artifact_type():
    with pytest.raises(ValidationError):
        ExecutionArtifact(
            artifact_id="unknown_output",
            artifact_type="sql",
            data="select * from table",
        )
