"""将完整黄金意图转换为三步确定性分析计划。"""

from contracts import AnalysisPlan, AnalysisStep, IntentResult


def create_analysis_plan(intent: IntentResult) -> AnalysisPlan:
    """仅为完整的下降归因意图生成第一阶段计划。"""
    if intent.intent_type != "drop_reason_analysis" or intent.ambiguities:
        return AnalysisPlan(intent=intent, steps=[])

    steps = [
        AnalysisStep(
            step_id="verify_gmv_change",
            goal="比较本周与上周 GMV，确认下滑幅度",
            required_metrics=["gmv"],
            group_by=["period"],
        ),
        AnalysisStep(
            step_id="decompose_gmv",
            goal="拆解订单量、活跃用户和客单价变化",
            required_metrics=["gmv", "orders", "active_users", "aov"],
            group_by=["period"],
        ),
        AnalysisStep(
            step_id="check_supporting_signals",
            goal="检查高峰订单和优惠券成本变化",
            required_metrics=["peak_orders", "coupon_cost"],
            group_by=["period"],
        ),
    ]
    return AnalysisPlan(intent=intent, steps=steps)
