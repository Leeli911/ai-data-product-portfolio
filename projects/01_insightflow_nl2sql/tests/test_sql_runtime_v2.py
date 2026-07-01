import pytest
from pydantic import ValidationError

from text2analytics_engine.contracts import Intent
from text2analytics_engine.execution import ExecutionRequest
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


def _change_request():
    return _request_from_intent(
        Intent(
            task_type="change_explanation",
            is_supported=True,
            metric="metric_gmv",
            dimension="dimension_district",
            time_window="time_window_this_week",
            comparison_window="comparison_week_over_week",
        )
    )


def _comparison_request():
    return _request_from_intent(
        Intent(
            task_type="dimension_comparison",
            is_supported=True,
            metric="metric_gmv",
            dimension="dimension_district",
            time_window="time_window_this_week",
        )
    )


def _ranking_request():
    return _request_from_intent(
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


def _assert_read_only_single_statement(sql):
    normalized = sql.upper()

    assert normalized.startswith("SELECT ")
    assert " GROUP BY " in normalized
    assert " ORDER BY " in normalized
    assert " LIMIT " in normalized
    assert ";" not in sql
    for keyword in ["UPDATE", "DELETE", "INSERT", "DROP"]:
        assert keyword not in normalized


def test_generated_query_model_validates_runtime_structure():
    query = GeneratedQuery(
        query_id="query_dimension_comparison_v1",
        task_type="dimension_comparison",
        sql=(
            "SELECT district, SUM(gmv) AS metric_value "
            "FROM local_life_transactions "
            "GROUP BY district "
            "ORDER BY metric_value DESC "
            "LIMIT 50"
        ),
        required_tables=["local_life_transactions"],
        required_columns=["district", "gmv"],
        query_type="dimension_aggregation",
    )

    assert query.query_id == "query_dimension_comparison_v1"
    assert query.required_tables == ["local_life_transactions"]
    assert query.required_columns == ["district", "gmv"]


@pytest.mark.parametrize(
    ("request_factory", "expected_query_id", "expected_query_type"),
    [
        (
            _change_request,
            "query_change_explanation_v1",
            "period_aggregation",
        ),
        (
            _comparison_request,
            "query_dimension_comparison_v1",
            "dimension_aggregation",
        ),
        (_ranking_request, "query_top_n_ranking_v1", "ranking"),
    ],
)
def test_generate_query_supports_planner_execution_requests(
    request_factory,
    expected_query_id,
    expected_query_type,
):
    request = request_factory()
    query = generate_query(request)

    assert query.query_id == expected_query_id
    assert query.task_type == request.task_type
    assert query.query_type == expected_query_type
    assert query.required_tables == ["local_life_transactions"]
    assert isinstance(query.sql, str)
    _assert_read_only_single_statement(query.sql)


def test_change_explanation_sql_template_is_stable():
    query = generate_query(_change_request())

    assert query.sql == (
        "SELECT period, SUM(gmv) AS metric_gmv, "
        "SUM(orders) AS metric_orders, AVG(aov) AS metric_aov "
        "FROM local_life_transactions "
        "GROUP BY period "
        "ORDER BY period DESC "
        "LIMIT 2"
    )
    assert query.required_columns == ["period", "gmv", "orders", "aov"]


def test_dimension_comparison_sql_template_is_stable():
    query = generate_query(_comparison_request())

    assert query.sql == (
        "SELECT district, SUM(gmv) AS metric_value "
        "FROM local_life_transactions "
        "GROUP BY district "
        "ORDER BY metric_value DESC "
        "LIMIT 50"
    )
    assert query.required_columns == ["district", "gmv"]


def test_top_n_ranking_sql_template_is_stable():
    query = generate_query(_ranking_request())

    assert query.sql == (
        "SELECT district, SUM(orders) AS metric_value "
        "FROM local_life_transactions "
        "GROUP BY district "
        "ORDER BY metric_value DESC "
        "LIMIT 5"
    )
    assert query.required_columns == ["district", "orders"]


def test_generated_query_rejects_non_select_query_type():
    with pytest.raises(ValidationError):
        GeneratedQuery(
            query_id="unsafe_query",
            task_type="dimension_comparison",
            sql="UPDATE local_life_transactions SET gmv = 0",
            required_tables=["local_life_transactions"],
            required_columns=["gmv"],
            query_type="mutation",
        )


def test_sql_runtime_does_not_include_execution_backend_binding():
    query = generate_query(_change_request())
    dumped = query.model_dump(mode="json")

    assert "duckdb" not in dumped
    assert "connection" not in dumped
    assert "cursor" not in dumped
