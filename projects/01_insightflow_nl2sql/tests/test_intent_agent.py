from contracts import AnalyticsRequest
from intent_agent import understand_intent


def test_understand_canonical_gmv_drop_question():
    """黄金问题应解析出完整的下降归因意图。"""
    result = understand_intent(
        AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    )

    assert result.intent_type == "drop_reason_analysis"
    assert result.metric == "gmv"
    assert result.metric_label == "GMV"
    assert result.district == "Chaoyang"
    assert result.time_range == "latest_7_days"
    assert result.comparison_period == "previous_7_days"
    assert result.ambiguities == []


def test_understand_trade_amount_synonym():
    """交易额是黄金链路中 GMV 的确定性同义词。"""
    result = understand_intent(
        AnalyticsRequest(question="北京朝阳区本周交易额为什么下降？")
    )

    assert result.intent_type == "drop_reason_analysis"
    assert result.metric == "gmv"
    assert result.ambiguities == []


def test_missing_conditions_are_reported_instead_of_defaulted():
    """缺少指标和时间时必须返回歧义，不能用默认值掩盖。"""
    result = understand_intent(AnalyticsRequest(question="为什么朝阳区下滑？"))

    assert result.metric is None
    assert result.time_range is None
    assert result.comparison_period is None
    assert result.ambiguities == ["未识别到 GMV 指标", "未识别到本周时间范围"]


def test_out_of_scope_question_is_explicitly_unsupported():
    """漏斗问题不属于第一阶段，必须明确拒绝扩展。"""
    result = understand_intent(
        AnalyticsRequest(question="分析北京朝阳区本周转化漏斗")
    )

    assert result.intent_type == "unsupported"
