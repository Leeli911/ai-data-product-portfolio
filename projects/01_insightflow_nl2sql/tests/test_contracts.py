import pytest
from pydantic import ValidationError

from contracts import (
    AnalysisPlan,
    AnalysisStep,
    AnalyticsRequest,
    IntentResult,
    PlanValidationResult,
)


def test_phase_one_contracts_form_a_typed_chain():
    """Phase 1 的四段输出必须能通过 Pydantic 契约首尾相接。"""
    request = AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    intent = IntentResult(
        intent_type="drop_reason_analysis",
        metric="gmv",
        metric_label="GMV",
        district="Chaoyang",
        time_range="latest_7_days",
        comparison_period="previous_7_days",
    )
    plan = AnalysisPlan(
        intent=intent,
        steps=[
            AnalysisStep(
                step_id="verify_gmv_change",
                goal="比较本周与上周 GMV",
                required_metrics=["gmv"],
                group_by=["period"],
            )
        ],
    )
    validation = PlanValidationResult(is_valid=True)

    assert request.dataset_id == "local_life_demo"
    assert plan.intent is intent
    assert validation.missing_step_ids == []
    assert validation.errors == []


def test_intent_type_rejects_values_outside_phase_one_scope():
    """第一阶段只允许下降归因或明确标记为 unsupported。"""
    with pytest.raises(ValidationError):
        IntentResult(intent_type="funnel_analysis")
