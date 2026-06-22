"""第一阶段黄金问题的确定性 Intent Agent。"""

from contracts import AnalyticsRequest, IntentResult


GMV_TERMS = ("gmv", "交易额", "销售额")
DROP_TERMS = ("下降", "下滑", "减少", "回落")
UNSUPPORTED_TERMS = ("漏斗", "cohort", "留存")


def understand_intent(request: AnalyticsRequest) -> IntentResult:
    """识别黄金链路所需字段，并显式保留缺失条件。"""
    question = request.question.strip()
    normalized_question = question.lower()

    metric = (
        "gmv"
        if any(term in normalized_question for term in GMV_TERMS)
        else None
    )
    district = "Chaoyang" if "朝阳" in question else None
    time_range = "latest_7_days" if "本周" in question else None
    comparison_period = "previous_7_days" if time_range else None

    ambiguities = []
    if metric is None:
        ambiguities.append("未识别到 GMV 指标")
    if district is None:
        ambiguities.append("未识别到朝阳区")
    if time_range is None:
        ambiguities.append("未识别到本周时间范围")

    is_drop_question = any(term in question for term in DROP_TERMS)
    is_unsupported = any(
        term in normalized_question for term in UNSUPPORTED_TERMS
    )
    intent_type = (
        "drop_reason_analysis"
        if is_drop_question and not is_unsupported
        else "unsupported"
    )

    return IntentResult(
        intent_type=intent_type,
        metric=metric,
        metric_label="GMV" if metric else None,
        district=district,
        time_range=time_range,
        comparison_period=comparison_period,
        ambiguities=ambiguities,
    )
