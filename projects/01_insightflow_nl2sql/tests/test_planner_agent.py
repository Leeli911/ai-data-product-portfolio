from contracts import IntentResult
from planner_agent import create_analysis_plan


def build_complete_intent():
    """构造黄金链路的完整意图。"""
    return IntentResult(
        intent_type="drop_reason_analysis",
        metric="gmv",
        metric_label="GMV",
        district="Chaoyang",
        time_range="latest_7_days",
        comparison_period="previous_7_days",
    )


def test_create_plan_covers_three_required_analysis_paths():
    """黄金计划应按顺序覆盖验证、拆解和辅助信号。"""
    result = create_analysis_plan(build_complete_intent())

    assert [step.step_id for step in result.steps] == [
        "verify_gmv_change",
        "decompose_gmv",
        "check_supporting_signals",
    ]
    assert result.steps[0].required_metrics == ["gmv"]
    assert result.steps[1].required_metrics == [
        "gmv",
        "orders",
        "active_users",
        "aov",
    ]
    assert result.steps[2].required_metrics == ["peak_orders", "coupon_cost"]
    assert all(step.group_by == ["period"] for step in result.steps)


def test_create_plan_does_not_expand_unsupported_intent():
    """超出范围的意图不应被 Planner 擅自扩成分析计划。"""
    intent = IntentResult(intent_type="unsupported")

    result = create_analysis_plan(intent)

    assert result.steps == []


def test_create_plan_stops_when_intent_is_ambiguous():
    """关键条件有歧义时不应生成看似完整的计划。"""
    intent = build_complete_intent().model_copy(
        update={"metric": None, "ambiguities": ["未识别到 GMV 指标"]}
    )

    result = create_analysis_plan(intent)

    assert result.steps == []
