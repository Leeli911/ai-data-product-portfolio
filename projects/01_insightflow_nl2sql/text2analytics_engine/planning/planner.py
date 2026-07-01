"""Deterministic Intent-to-AnalysisPlan planner for Text2Analytics V2."""

from text2analytics_engine.contracts import Intent
from text2analytics_engine.planning.models import (
    AnalysisPlan,
    AnalysisStep,
    ExpectedArtifact,
    RequiredDimension,
    RequiredMetric,
    RequiredTimeWindow,
)


class PlanningError(ValueError):
    """Raised when an Intent cannot produce a normal AnalysisPlan."""


def _artifact(artifact_id: str) -> ExpectedArtifact:
    return ExpectedArtifact(artifact_id=artifact_id)


def _required_metrics(*metric_ids: str | None) -> list[RequiredMetric]:
    return [
        RequiredMetric(metric_id=metric_id)
        for metric_id in metric_ids
        if metric_id
    ]


def _required_dimensions(
    *dimension_ids: str | None,
) -> list[RequiredDimension]:
    return [
        RequiredDimension(dimension_id=dimension_id)
        for dimension_id in dimension_ids
        if dimension_id
    ]


def _required_time_windows(
    *time_window_ids: str | None,
) -> list[RequiredTimeWindow]:
    return [
        RequiredTimeWindow(time_window_id=time_window_id)
        for time_window_id in time_window_ids
        if time_window_id
    ]


def _ensure_supported_intent(intent: Intent) -> None:
    if not intent.is_supported:
        raise PlanningError(
            f"unsupported intent cannot be planned: {intent.task_type}"
        )


def _change_explanation_plan(intent: Intent) -> AnalysisPlan:
    return AnalysisPlan(
        plan_id="plan_change_explanation_v1",
        task_type="change_explanation",
        objective=(
            "Explain observed metric change within a bounded comparison "
            "window."
        ),
        required_metrics=_required_metrics(
            intent.metric,
            "metric_orders",
            "metric_aov",
        ),
        required_dimensions=_required_dimensions(
            intent.dimension,
            "dimension_period",
        ),
        required_time_windows=_required_time_windows(intent.time_window),
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
                    "Verify target metric change between current and "
                    "comparison windows."
                ),
                required_inputs=[
                    intent.metric,
                    intent.time_window,
                    intent.comparison_window,
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
                    "Decompose metric movement using observable supporting "
                    "metrics."
                ),
                required_inputs=[
                    intent.metric,
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
                    _artifact("evidence_inputs"),
                    _artifact("interpretation_boundaries"),
                    _artifact("limitation_candidates"),
                ],
                validation_requirements=[
                    "interpretations_must_bind_to_evidence",
                    "causal_claims_not_allowed",
                ],
            ),
        ],
    )


def _dimension_comparison_plan(intent: Intent) -> AnalysisPlan:
    return AnalysisPlan(
        plan_id="plan_dimension_comparison_v1",
        task_type="dimension_comparison",
        objective=(
            "Compare selected metric across dimension values in the selected "
            "time window."
        ),
        required_metrics=_required_metrics(intent.metric),
        required_dimensions=_required_dimensions(intent.dimension),
        required_time_windows=_required_time_windows(intent.time_window),
        expected_outputs=[
            _artifact("dimension_metric_table"),
            _artifact("dimension_comparison_summary"),
            _artifact("limitation_inputs"),
        ],
        ordered_steps=[
            AnalysisStep(
                step_id="compute_metric_by_dimension",
                goal=(
                    "Compute selected metric for each dimension value in the "
                    "selected time window."
                ),
                required_inputs=[
                    intent.metric,
                    intent.dimension,
                    intent.time_window,
                ],
                expected_artifacts=[
                    _artifact("dimension_metric_table"),
                ],
                validation_requirements=[
                    "metric_id_must_be_known",
                    "dimension_id_must_be_known",
                    "time_window_must_exist",
                ],
            ),
            AnalysisStep(
                step_id="compare_dimension_values",
                goal=(
                    "Compare metric values across dimension rows without "
                    "causal claims."
                ),
                required_inputs=[
                    "dimension_metric_table",
                ],
                expected_artifacts=[
                    _artifact("dimension_comparison_summary"),
                    _artifact("evidence_inputs"),
                ],
                validation_requirements=[
                    "comparison_must_use_observed_values",
                    "comparison_requires_at_least_two_dimension_values",
                ],
            ),
        ],
    )


def _top_n_ranking_plan(intent: Intent) -> AnalysisPlan:
    return AnalysisPlan(
        plan_id="plan_top_n_ranking_v1",
        task_type="top_n_ranking",
        objective=(
            "Rank dimension values by the selected metric in the selected "
            "time window."
        ),
        required_metrics=_required_metrics(intent.metric),
        required_dimensions=_required_dimensions(intent.dimension),
        required_time_windows=_required_time_windows(intent.time_window),
        expected_outputs=[
            _artifact("ranked_dimension_table"),
            _artifact("ranking_summary"),
            _artifact("limitation_inputs"),
        ],
        ordered_steps=[
            AnalysisStep(
                step_id="compute_metric_by_dimension",
                goal=(
                    "Compute selected metric for each dimension value in the "
                    "selected time window."
                ),
                required_inputs=[
                    intent.metric,
                    intent.dimension,
                    intent.time_window,
                ],
                expected_artifacts=[
                    _artifact("dimension_metric_table"),
                ],
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
                    "the requested ranking window."
                ),
                required_inputs=[
                    "dimension_metric_table",
                    intent.ranking,
                    f"ranking_n={intent.ranking_n}",
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


def plan_from_intent(intent: Intent) -> AnalysisPlan:
    """Build a deterministic AnalysisPlan from a canonical Intent."""
    _ensure_supported_intent(intent)

    if intent.task_type == "change_explanation":
        return _change_explanation_plan(intent)
    if intent.task_type == "dimension_comparison":
        return _dimension_comparison_plan(intent)
    if intent.task_type == "top_n_ranking":
        return _top_n_ranking_plan(intent)

    raise PlanningError(
        f"unsupported planner task type: {intent.task_type}"
    )
