import pytest

from text2analytics_engine.contracts import Intent
from text2analytics_engine.planning import PlanningError, plan_from_intent


def _change_intent():
    return Intent(
        task_type="change_explanation",
        is_supported=True,
        metric="metric_gmv",
        dimension="dimension_district",
        time_window="time_window_this_week",
        comparison_window="comparison_week_over_week",
    )


def _comparison_intent():
    return Intent(
        task_type="dimension_comparison",
        is_supported=True,
        metric="metric_gmv",
        dimension="dimension_district",
        time_window="time_window_this_week",
    )


def _ranking_intent():
    return Intent(
        task_type="top_n_ranking",
        is_supported=True,
        metric="metric_orders",
        dimension="dimension_district",
        time_window="time_window_this_week",
        ranking="ranking_bottom_n",
        ranking_n=5,
    )


def test_planner_builds_change_explanation_plan():
    plan = plan_from_intent(_change_intent())

    assert plan.plan_id == "plan_change_explanation_v1"
    assert plan.task_type == "change_explanation"
    assert [step.step_id for step in plan.ordered_steps] == [
        "verify_metric_change",
        "decompose_metric_change",
        "prepare_bounded_interpretation_inputs",
    ]
    assert [item.metric_id for item in plan.required_metrics][:1] == [
        "metric_gmv"
    ]
    assert "metric_gmv" in plan.ordered_steps[0].required_inputs
    assert "comparison_week_over_week" in plan.ordered_steps[0].required_inputs


def test_planner_builds_dimension_comparison_plan():
    plan = plan_from_intent(_comparison_intent())

    assert plan.plan_id == "plan_dimension_comparison_v1"
    assert plan.task_type == "dimension_comparison"
    assert [step.step_id for step in plan.ordered_steps] == [
        "compute_metric_by_dimension",
        "compare_dimension_values",
    ]
    assert [item.metric_id for item in plan.required_metrics] == [
        "metric_gmv"
    ]
    assert [item.dimension_id for item in plan.required_dimensions] == [
        "dimension_district"
    ]


def test_planner_builds_top_n_ranking_plan():
    plan = plan_from_intent(_ranking_intent())

    assert plan.plan_id == "plan_top_n_ranking_v1"
    assert plan.task_type == "top_n_ranking"
    assert [step.step_id for step in plan.ordered_steps] == [
        "compute_metric_by_dimension",
        "rank_dimension_values",
    ]
    assert plan.ordered_steps[1].required_inputs == [
        "dimension_metric_table",
        "ranking_bottom_n",
        "ranking_n=5",
    ]


@pytest.mark.parametrize(
    "intent_factory",
    [_change_intent, _comparison_intent, _ranking_intent],
)
def test_planner_uses_canonical_ids_from_intent(intent_factory):
    intent = intent_factory()
    plan = plan_from_intent(intent)

    assert intent.metric in [
        item.metric_id for item in plan.required_metrics
    ]
    assert intent.dimension in [
        item.dimension_id for item in plan.required_dimensions
    ]
    assert intent.time_window in [
        item.time_window_id for item in plan.required_time_windows
    ]


def test_unsupported_intent_does_not_generate_normal_plan():
    intent = Intent(
        task_type="forecasting",
        is_supported=False,
        metric="metric_gmv",
        unsupported_reason="forecasting",
    )

    with pytest.raises(PlanningError, match="unsupported"):
        plan_from_intent(intent)


def test_planner_does_not_output_downstream_artifacts():
    plan = plan_from_intent(_change_intent())
    dumped = plan.model_dump(mode="json")

    assert "sql" not in dumped
    assert "query" not in dumped
    assert "facts" not in dumped
    assert "interpretations" not in dumped
    assert "score" not in dumped
    assert all("sql" not in step for step in dumped["ordered_steps"])
    assert all("score" not in step for step in dumped["ordered_steps"])
