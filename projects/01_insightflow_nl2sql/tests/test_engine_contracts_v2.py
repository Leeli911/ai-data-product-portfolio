import pytest
from pydantic import ValidationError

from text2analytics_engine.contracts import (
    AnalyticsRequest,
    AnalyticsResponse,
    AnalysisPlan,
    Intent,
    PipelineStage,
    PipelineStatus,
)


def test_analytics_request_accepts_business_question():
    request = AnalyticsRequest(
        question="Why did GMV drop in Chaoyang this week?"
    )

    assert request.question == "Why did GMV drop in Chaoyang this week?"
    assert request.dataset_id == "local_life_demo"


def test_analytics_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        AnalyticsRequest(question="")


def test_analytics_response_keeps_minimal_pipeline_contract():
    request = AnalyticsRequest(
        question="Why did GMV drop in Chaoyang this week?"
    )
    intent = Intent(
        task_type="change_explanation",
        is_supported=True,
        metric="metric_gmv",
        dimension="dimension_district",
        time_window="time_window_this_week",
        comparison_window="comparison_week_over_week",
    )
    plan = AnalysisPlan(
        steps=[
            "Verify GMV change",
            "Prepare deterministic analysis plan",
        ]
    )

    response = AnalyticsResponse(
        status=PipelineStatus.SUCCESS,
        request=request,
        pipeline=[
            PipelineStage.INTENT,
            PipelineStage.PLAN,
        ],
        result={
            "intent": intent.model_dump(mode="json"),
            "analysis_plan": plan.model_dump(mode="json"),
        },
        metadata={"engine_version": "v2"},
    )

    dumped = response.model_dump(mode="json")

    assert dumped["status"] == "success"
    assert dumped["pipeline"] == ["intent", "plan"]
    assert dumped["result"]["intent"]["metric"] == "metric_gmv"
    assert dumped["result"]["intent"]["dimension"] == "dimension_district"
    assert dumped["result"]["analysis_plan"]["steps"][0] == (
        "Verify GMV change"
    )
    assert dumped["metadata"]["engine_version"] == "v2"


def test_pipeline_stage_enum_values_are_stable():
    assert PipelineStage("intent") is PipelineStage.INTENT
    assert PipelineStage("plan") is PipelineStage.PLAN
    assert PipelineStage("validation") is PipelineStage.VALIDATION
    assert PipelineStage("scoring") is PipelineStage.SCORING
