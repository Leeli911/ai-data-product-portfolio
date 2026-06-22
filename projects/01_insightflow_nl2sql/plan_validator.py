"""独立检查黄金计划是否覆盖三条必需分析路径。"""

from contracts import AnalysisPlan, PlanValidationResult


REQUIRED_STEP_IDS = (
    "verify_gmv_change",
    "decompose_gmv",
    "check_supporting_signals",
)


def validate_plan(plan: AnalysisPlan) -> PlanValidationResult:
    """返回缺失的必需步骤及逐项错误说明。"""
    actual_step_ids = {step.step_id for step in plan.steps}
    missing_step_ids = [
        step_id
        for step_id in REQUIRED_STEP_IDS
        if step_id not in actual_step_ids
    ]
    return PlanValidationResult(
        is_valid=not missing_step_ids,
        missing_step_ids=missing_step_ids,
        errors=[
            f"缺少必需分析步骤：{step_id}"
            for step_id in missing_step_ids
        ],
    )
