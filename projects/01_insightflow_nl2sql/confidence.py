"""根据显式规则计算证据完整度，而非答案真实概率。"""

from contracts import (
    ConfidenceAssessment,
    ConfidenceFactor,
    ConfidenceRequest,
)
from plan_validator import REQUIRED_STEP_IDS


BASE_CONFIDENCE = 0.50


def _factor(
    name: str,
    condition: bool,
    applied_impact: float,
    applied_reason: str,
    skipped_reason: str,
) -> ConfidenceFactor:
    """无论规则是否触发，都返回可展示的评分依据。"""
    return ConfidenceFactor(
        name=name,
        impact=applied_impact if condition else 0.0,
        reason=applied_reason if condition else skipped_reason,
    )


def assess_confidence(request: ConfidenceRequest) -> ConfidenceAssessment:
    """计算 0.10–0.95 范围内的 evidence completeness。"""
    intent_complete = all(
        [
            request.intent.metric,
            request.intent.district,
            request.intent.time_range,
            request.intent.comparison_period,
        ]
    ) and not request.intent.ambiguities

    result_by_step = {
        result.step_id: result for result in request.query_results
    }
    required_steps = set(REQUIRED_STEP_IDS)
    executed_steps = {
        step_id
        for step_id, result in result_by_step.items()
        if result.row_count > 0
    }
    execution_complete = required_steps <= executed_steps

    period_complete = execution_complete and all(
        {str(row.get("period")) for row in result_by_step[step_id].rows}
        >= {"current", "previous"}
        for step_id in required_steps
    )

    fact_ids = {fact.fact_id for fact in request.insight.facts}
    evidence_bound = bool(request.insight.interpretations) and all(
        bool(interpretation.supporting_fact_ids)
        and set(interpretation.supporting_fact_ids) <= fact_ids
        for interpretation in request.insight.interpretations
    )

    supporting_data_missing = "check_supporting_signals" not in executed_steps
    fact_metrics = {fact.metric for fact in request.insight.facts}
    decomposition_insufficient = (
        "decompose_gmv" not in executed_steps
        or not {"gmv", "orders", "aov"} <= fact_metrics
    )
    correlation_limitation = any(
        "相关性" in limitation.statement
        and "不能证明因果" in limitation.statement
        for limitation in request.insight.limitations
    )

    factors = [
        _factor(
            "intent_complete",
            intent_complete,
            0.10,
            "Intent 包含明确指标、区域、时间范围和对比期。",
            "Intent 关键字段不完整或仍有歧义。",
        ),
        _factor(
            "plan_coverage",
            request.plan_validation.is_valid,
            0.10,
            "Plan 覆盖三条必需分析路径。",
            "Plan 未覆盖全部必需分析路径。",
        ),
        _factor(
            "sql_execution",
            execution_complete,
            0.10,
            "三条必需 SQL 均已校验并返回非空结果。",
            "并非所有必需 SQL 都返回了非空结果。",
        ),
        _factor(
            "period_completeness",
            period_complete,
            0.10,
            "每条必需查询都包含 current 和 previous 两期数据。",
            "当前期或对比期数据不完整。",
        ),
        _factor(
            "evidence_binding",
            evidence_bound,
            0.10,
            "所有 Interpretation 均绑定有效 Fact。",
            "存在未绑定有效 Fact 的 Interpretation。",
        ),
        _factor(
            "missing_supporting_data",
            supporting_data_missing,
            -0.10,
            "缺少高峰订单或优惠券成本等关键支持数据。",
            "高峰订单和优惠券成本支持数据完整。",
        ),
        _factor(
            "insufficient_decomposition",
            decomposition_insufficient,
            -0.10,
            "查询结果不足以完成 GMV、订单量和客单价拆解。",
            "GMV、订单量和客单价拆解数据完整。",
        ),
        _factor(
            "correlation_limitation",
            correlation_limitation,
            -0.10,
            "当前证据只能支持相关性分析，不能证明因果关系。",
            "未识别到重要的相关性限制。",
        ),
    ]
    score = round(
        min(
            0.95,
            max(
                0.10,
                BASE_CONFIDENCE
                + sum(factor.impact for factor in factors),
            ),
        ),
        2,
    )
    return ConfidenceAssessment(score=score, factors=factors)
