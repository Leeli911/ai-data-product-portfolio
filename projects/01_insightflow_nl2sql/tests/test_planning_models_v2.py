import pytest
from pydantic import ValidationError

from text2analytics_engine.planning.models import (
    AnalysisPlan,
    AnalysisStep,
    ExpectedArtifact,
    RequiredDimension,
    RequiredMetric,
    RequiredTimeWindow,
)


def _artifact(artifact_id):
    return ExpectedArtifact(artifact_id=artifact_id)


def _change_explanation_plan():
    return AnalysisPlan(
        plan_id="plan_change_explanation_v1",
        task_type="change_explanation",
        objective=(
            "Explain observed GMV change within a bounded comparison window."
        ),
        required_metrics=[
            RequiredMetric(metric_id="metric_gmv"),
            RequiredMetric(metric_id="metric_orders"),
            RequiredMetric(metric_id="metric_aov"),
        ],
        required_dimensions=[
            RequiredDimension(dimension_id="dimension_district"),
            RequiredDimension(dimension_id="dimension_period"),
        ],
        required_time_windows=[
            RequiredTimeWindow(time_window_id="time_window_this_week"),
        ],
        expected_outputs=[
            _artifact("metric_change_summary"),
            _artifact("metric_decomposition"),
            _artifact("bounded_interpretation_inputs"),
            _artifact("limitation_inputs"),
        ],
        ordered_steps=[
            AnalysisStep(
                step_id="verify_metric_change",
                goal=(
                    "Verify GMV change between current and comparison "
                    "windows."
                ),
                required_inputs=[
                    "metric_gmv",
                    "time_window_this_week",
                    "comparison_week_over_week",
                ],
                expected_artifacts=[
                    _artifact("current_metric_value"),
                    _artifact("previous_metric_value"),
                    _artifact("change_rate"),
                ],
                validation_requirements=[
                    "metric_id_must_be_known",
                    "comparison_window_must_exist",
                    "current_and_previous_periods_required",
                ],
            ),
            AnalysisStep(
                step_id="decompose_metric_change",
                goal=(
                    "Decompose GMV movement using observable supporting "
                    "metrics."
                ),
                required_inputs=[
                    "metric_gmv",
                    "metric_orders",
                    "metric_aov",
                ],
                expected_artifacts=[
                    _artifact("decomposition_metrics"),
                    _artifact("decomposition_change_rates"),
                ],
                validation_requirements=[
                    "supporting_metrics_must_be_known",
                    "decomposition_must_use_observed_metrics",
                ],
            ),
            AnalysisStep(
                step_id="prepare_bounded_interpretation_inputs",
                goal=(
                    "Prepare evidence inputs for bounded, non-causal "
                    "interpretation."
                ),
                required_inputs=[
                    "metric_change_summary",
                    "metric_decomposition",
                ],
                expected_artifacts=[
                    _artifact("fact_candidates"),
                    _artifact("interpretation_boundaries"),
                    _artifact("limitation_candidates"),
                ],
                validation_requirements=[
                    "interpretations_must_bind_to_facts",
                    "causal_claims_not_allowed",
                ],
            ),
        ],
    )


def _dimension_comparison_plan():
    return AnalysisPlan(
        plan_id="plan_dimension_comparison_v1",
        task_type="dimension_comparison",
        objective=(
            "Compare GMV across district values in the selected time window."
        ),
        required_metrics=[RequiredMetric(metric_id="metric_gmv")],
        required_dimensions=[
            RequiredDimension(dimension_id="dimension_district")
        ],
        required_time_windows=[
            RequiredTimeWindow(time_window_id="time_window_this_week")
        ],
        expected_outputs=[
            _artifact("dimension_metric_table"),
            _artifact("dimension_comparison_summary"),
            _artifact("limitation_inputs"),
        ],
        ordered_steps=[
            AnalysisStep(
                step_id="compute_metric_by_dimension",
                goal=(
                    "Compute GMV for each district in the selected time "
                    "window."
                ),
                required_inputs=[
                    "metric_gmv",
                    "dimension_district",
                    "time_window_this_week",
                ],
                expected_artifacts=[_artifact("dimension_metric_table")],
                validation_requirements=[
                    "metric_id_must_be_known",
                    "dimension_id_must_be_known",
                    "time_window_must_exist",
                ],
            ),
            AnalysisStep(
                step_id="compare_dimension_values",
                goal=(
                    "Compare metric values across district rows without "
                    "causal claims."
                ),
                required_inputs=["dimension_metric_table"],
                expected_artifacts=[
                    _artifact("dimension_comparison_summary"),
                    _artifact("fact_candidates"),
                ],
                validation_requirements=[
                    "comparison_must_use_observed_values",
                    "comparison_requires_at_least_two_dimension_values",
                ],
            ),
        ],
    )


def _top_n_ranking_plan():
    return AnalysisPlan(
        plan_id="plan_top_n_ranking_v1",
        task_type="top_n_ranking",
        objective=(
            "Rank districts by order volume in the selected time window."
        ),
        required_metrics=[RequiredMetric(metric_id="metric_orders")],
        required_dimensions=[
            RequiredDimension(dimension_id="dimension_district")
        ],
        required_time_windows=[
            RequiredTimeWindow(time_window_id="time_window_this_week")
        ],
        expected_outputs=[
            _artifact("ranked_dimension_table"),
            _artifact("ranking_summary"),
            _artifact("limitation_inputs"),
        ],
        ordered_steps=[
            AnalysisStep(
                step_id="compute_metric_by_dimension",
                goal=(
                    "Compute order volume for each district in the selected "
                    "time window."
                ),
                required_inputs=[
                    "metric_orders",
                    "dimension_district",
                    "time_window_this_week",
                ],
                expected_artifacts=[_artifact("dimension_metric_table")],
                validation_requirements=[
                    "metric_id_must_be_known",
                    "dimension_id_must_be_known",
                    "time_window_must_exist",
                ],
            ),
            AnalysisStep(
                step_id="rank_dimension_values",
                goal=(
                    "Sort dimension values by the selected metric and return "
                    "bottom 5."
                ),
                required_inputs=[
                    "dimension_metric_table",
                    "ranking_bottom_n",
                    "ranking_n=5",
                ],
                expected_artifacts=[
                    _artifact("ranked_dimension_table"),
                    _artifact("ranking_summary"),
                ],
                validation_requirements=[
                    "ranking_direction_must_be_known",
                    "ranking_n_must_be_positive",
                    "ranking_requires_metric_and_dimension",
                ],
            ),
        ],
    )


@pytest.mark.parametrize(
    "plan_factory",
    [
        _change_explanation_plan,
        _dimension_comparison_plan,
        _top_n_ranking_plan,
    ],
)
def test_runtime_plans_can_express_design_examples(plan_factory):
    plan = plan_factory()

    assert plan.plan_id
    assert plan.objective
    assert len(plan.ordered_steps) >= 2
    assert all(step.step_id for step in plan.ordered_steps)
    assert all(step.required_inputs for step in plan.ordered_steps)
    assert all(step.expected_artifacts for step in plan.ordered_steps)


def test_analysis_plan_preserves_step_order():
    plan = _change_explanation_plan()

    assert [step.step_id for step in plan.ordered_steps] == [
        "verify_metric_change",
        "decompose_metric_change",
        "prepare_bounded_interpretation_inputs",
    ]


def test_analysis_step_preserves_required_inputs():
    plan = _top_n_ranking_plan()
    ranking_step = plan.ordered_steps[1]

    assert ranking_step.required_inputs == [
        "dimension_metric_table",
        "ranking_bottom_n",
        "ranking_n=5",
    ]


def test_expected_artifacts_are_structured_runtime_objects():
    plan = _dimension_comparison_plan()

    dumped = plan.model_dump(mode="json")

    assert dumped["expected_outputs"][0] == {
        "artifact_id": "dimension_metric_table"
    }
    assert dumped["ordered_steps"][1]["expected_artifacts"] == [
        {"artifact_id": "dimension_comparison_summary"},
        {"artifact_id": "fact_candidates"},
    ]


def test_required_entities_are_structured_runtime_objects():
    plan = _change_explanation_plan()

    assert [item.metric_id for item in plan.required_metrics] == [
        "metric_gmv",
        "metric_orders",
        "metric_aov",
    ]
    assert [item.dimension_id for item in plan.required_dimensions] == [
        "dimension_district",
        "dimension_period",
    ]
    assert [item.time_window_id for item in plan.required_time_windows] == [
        "time_window_this_week"
    ]


def test_models_reject_missing_required_fields():
    with pytest.raises(ValidationError):
        AnalysisStep(
            step_id="verify_metric_change",
            required_inputs=["metric_gmv"],
            expected_artifacts=[_artifact("metric_change_summary")],
            validation_requirements=["metric_id_must_be_known"],
        )

    with pytest.raises(ValidationError):
        AnalysisPlan(
            task_type="change_explanation",
            objective="Missing plan_id should fail.",
            ordered_steps=[],
        )
