from contracts import AnalysisPlan, AnalysisStep, IntentResult
from plan_validator import validate_plan


def build_step(step_id):
    """构造仅用于计划结构校验的必需步骤。"""
    return AnalysisStep(
        step_id=step_id,
        goal=step_id,
        required_metrics=["gmv"],
        group_by=["period"],
    )


def build_plan(step_ids):
    """按指定 step_id 构造类型化计划。"""
    intent = IntentResult(
        intent_type="drop_reason_analysis",
        metric="gmv",
        metric_label="GMV",
        district="Chaoyang",
        time_range="latest_7_days",
        comparison_period="previous_7_days",
    )
    return AnalysisPlan(
        intent=intent,
        steps=[build_step(step_id) for step_id in step_ids],
    )


def test_validate_complete_golden_plan():
    """三条必需路径齐全时校验通过。"""
    plan = build_plan(
        [
            "verify_gmv_change",
            "decompose_gmv",
            "check_supporting_signals",
        ]
    )

    result = validate_plan(plan)

    assert result.is_valid is True
    assert result.missing_step_ids == []
    assert result.errors == []


def test_validate_plan_reports_each_missing_required_path():
    """缺失路径必须逐项返回，不能只给笼统失败。"""
    plan = build_plan(["verify_gmv_change"])

    result = validate_plan(plan)

    assert result.is_valid is False
    assert result.missing_step_ids == [
        "decompose_gmv",
        "check_supporting_signals",
    ]
    assert result.errors == [
        "缺少必需分析步骤：decompose_gmv",
        "缺少必需分析步骤：check_supporting_signals",
    ]
