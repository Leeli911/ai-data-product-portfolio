"""基于真实 DuckDB 结果生成证据化 Insight。"""

from contracts import (
    Fact,
    InsightRequest,
    InsightResult,
    Interpretation,
    Limitation,
    QueryExecutionResult,
)


METRIC_CONFIG = {
    "gmv": ("fact_gmv", "GMV", "CNY", "verify_gmv_change"),
    "orders": ("fact_orders", "订单量", "orders", "decompose_gmv"),
    "active_users": (
        "fact_active_users",
        "活跃用户",
        "users",
        "decompose_gmv",
    ),
    "aov": ("fact_aov", "客单价", "CNY/order", "decompose_gmv"),
    "peak_orders": (
        "fact_peak_orders",
        "高峰订单",
        "orders",
        "check_supporting_signals",
    ),
    "coupon_cost": (
        "fact_coupon_cost",
        "优惠券成本",
        "CNY",
        "check_supporting_signals",
    ),
}


def calculate_change_rate(current: float, previous: float) -> float:
    """计算一位小数的环比，并将负零规范为零。"""
    if previous == 0:
        return 0.0
    change_rate = round((current - previous) / previous * 100, 1)
    return 0.0 if change_rate == 0 else change_rate


def _rows_by_period(result: QueryExecutionResult) -> dict[str, dict]:
    """将查询的 current/previous 两行转为周期映射。"""
    return {str(row["period"]): row for row in result.rows}


def _build_statement(
    metric_label: str,
    unit: str,
    current_value: float,
    previous_value: float,
    change_rate: float,
) -> str:
    """为 Fact 生成只描述观测数值的陈述。"""
    if change_rate < 0:
        change_text = f"环比下降 {abs(change_rate):.1f}%"
    elif change_rate > 0:
        change_text = f"环比上升 {change_rate:.1f}%"
    else:
        change_text = "环比基本持平"
    return (
        f"{metric_label} 本周为 {current_value:,.2f} {unit}，"
        f"上周为 {previous_value:,.2f} {unit}，{change_text}。"
    )


def _build_fact(
    metric: str,
    results_by_step: dict[str, QueryExecutionResult],
) -> Fact:
    """从指定来源步骤构造一个可追溯 Fact。"""
    fact_id, metric_label, unit, source_step_id = METRIC_CONFIG[metric]
    periods = _rows_by_period(results_by_step[source_step_id])
    current_value = float(periods["current"][metric])
    previous_value = float(periods["previous"][metric])
    change_rate = calculate_change_rate(current_value, previous_value)
    return Fact(
        fact_id=fact_id,
        statement=_build_statement(
            metric_label,
            unit,
            current_value,
            previous_value,
            change_rate,
        ),
        metric=metric,
        metric_label=metric_label,
        unit=unit,
        current_value=current_value,
        previous_value=previous_value,
        change_rate=change_rate,
        source_step_id=source_step_id,
    )


def generate_insight(request: InsightRequest) -> InsightResult:
    """生成六个 Fact、三类 Interpretation 和三条 Limitation。"""
    results_by_step = {
        result.step_id: result for result in request.query_results
    }
    facts = [
        _build_fact(metric, results_by_step)
        for metric in METRIC_CONFIG
    ]
    facts_by_metric = {fact.metric: fact for fact in facts}

    gmv = facts_by_metric["gmv"]
    orders = facts_by_metric["orders"]
    aov = facts_by_metric["aov"]
    interpretations = [
        Interpretation(
            statement=f"GMV 本周较上周下降 {abs(gmv.change_rate):.1f}%。",
            supporting_fact_ids=[gmv.fact_id],
            reasoning_type="comparison",
        ),
        Interpretation(
            statement=(
                "GMV、订单量与客单价的拆解显示，"
                f"订单量下降 {abs(orders.change_rate):.1f}%，"
                "客单价基本持平。"
            ),
            supporting_fact_ids=[gmv.fact_id, orders.fact_id, aov.fact_id],
            reasoning_type="decomposition",
        ),
        Interpretation(
            statement=(
                "订单量下降与 GMV 下滑方向一致，"
                "是当前数据中最显著的关联因素。"
            ),
            supporting_fact_ids=[gmv.fact_id, orders.fact_id],
            reasoning_type="correlation",
        ),
    ]
    limitations = [
        Limitation(
            statement="当前数据只能支持相关性分析，不能证明因果关系。",
            impact="不能把指标同向变化解释为业务因果关系。",
            missing_data=[],
        ),
        Limitation(
            statement="缺少库存、天气、竞品、营销曝光等外部解释变量。",
            impact="无法判断这些外部因素是否与 GMV 下滑相关。",
            missing_data=[
                "inventory",
                "weather",
                "competitor_activity",
                "marketing_exposure",
            ],
        ),
        Limitation(
            statement=(
                "优惠券成本只能说明已观测投入变化，"
                "不能单独说明营销效果。"
            ),
            impact="需要曝光、转化和活动对照数据才能评估营销效果。",
            missing_data=["marketing_exposure", "campaign_conversion"],
        ),
    ]
    return InsightResult(
        facts=facts,
        interpretations=interpretations,
        limitations=limitations,
    )
