"""Deterministic SQL generator for Text2Analytics V2."""

from text2analytics_engine.execution import ExecutionRequest
from text2analytics_engine.sql.models import GeneratedQuery


class SQLGenerationError(ValueError):
    """Raised when an execution request cannot produce a query."""


TABLE_NAME = "local_life_transactions"

METRIC_COLUMNS = {
    "metric_gmv": ("gmv", "SUM"),
    "metric_orders": ("orders", "SUM"),
    "metric_aov": ("aov", "AVG"),
}

DIMENSION_COLUMNS = {
    "dimension_district": "district",
    "dimension_period": "period",
}


def _require_metric(request: ExecutionRequest) -> tuple[str, str]:
    for metric_id in request.required_metrics:
        if metric_id in METRIC_COLUMNS:
            return METRIC_COLUMNS[metric_id]
    raise SQLGenerationError(
        f"execution request has no supported metric: {request.plan_id}"
    )


def _require_dimension(request: ExecutionRequest) -> str:
    for dimension_id in request.required_dimensions:
        if dimension_id in DIMENSION_COLUMNS:
            return DIMENSION_COLUMNS[dimension_id]
    raise SQLGenerationError(
        f"execution request has no supported dimension: {request.plan_id}"
    )


def _change_explanation_query() -> GeneratedQuery:
    return GeneratedQuery(
        query_id="query_change_explanation_v1",
        task_type="change_explanation",
        sql=(
            "SELECT period, SUM(gmv) AS metric_gmv, "
            "SUM(orders) AS metric_orders, AVG(aov) AS metric_aov "
            f"FROM {TABLE_NAME} "
            "GROUP BY period "
            "ORDER BY period DESC "
            "LIMIT 2"
        ),
        required_tables=[TABLE_NAME],
        required_columns=["period", "gmv", "orders", "aov"],
        query_type="period_aggregation",
    )


def _dimension_comparison_query(
    request: ExecutionRequest,
) -> GeneratedQuery:
    metric_column, aggregation = _require_metric(request)
    dimension_column = _require_dimension(request)

    return GeneratedQuery(
        query_id="query_dimension_comparison_v1",
        task_type="dimension_comparison",
        sql=(
            f"SELECT {dimension_column}, "
            f"{aggregation}({metric_column}) AS metric_value "
            f"FROM {TABLE_NAME} "
            f"GROUP BY {dimension_column} "
            "ORDER BY metric_value DESC "
            "LIMIT 50"
        ),
        required_tables=[TABLE_NAME],
        required_columns=[dimension_column, metric_column],
        query_type="dimension_aggregation",
    )


def _top_n_ranking_query(request: ExecutionRequest) -> GeneratedQuery:
    metric_column, aggregation = _require_metric(request)
    dimension_column = _require_dimension(request)

    return GeneratedQuery(
        query_id="query_top_n_ranking_v1",
        task_type="top_n_ranking",
        sql=(
            f"SELECT {dimension_column}, "
            f"{aggregation}({metric_column}) AS metric_value "
            f"FROM {TABLE_NAME} "
            f"GROUP BY {dimension_column} "
            "ORDER BY metric_value DESC "
            "LIMIT 5"
        ),
        required_tables=[TABLE_NAME],
        required_columns=[dimension_column, metric_column],
        query_type="ranking",
    )


def generate_query(execution_request: ExecutionRequest) -> GeneratedQuery:
    """Generate a deterministic SQL runtime query from an execution request."""
    if execution_request.task_type == "change_explanation":
        return _change_explanation_query()
    if execution_request.task_type == "dimension_comparison":
        return _dimension_comparison_query(execution_request)
    if execution_request.task_type == "top_n_ranking":
        return _top_n_ranking_query(execution_request)

    raise SQLGenerationError(
        f"unsupported SQL generation task type: {execution_request.task_type}"
    )
