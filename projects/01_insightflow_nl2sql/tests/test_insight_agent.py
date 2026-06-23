import pytest
from pydantic import ValidationError

from contracts import (
    CAUSAL_TERMS,
    AnalyticsRequest,
    Fact,
    InsightRequest,
    InsightResult,
    Interpretation,
    SQLGenerationRequest,
)
from insight_agent import generate_insight
from intent_agent import understand_intent
from planner_agent import create_analysis_plan
from query_executor import execute_query
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries
from sql_validator import validate_sql


def build_real_insight_input():
    """用 Phase 2 的真实 DuckDB 输出构造 Insight 输入。"""
    snapshot = build_schema_snapshot()
    intent = understand_intent(
        AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    )
    plan = create_analysis_plan(intent)
    generated = generate_queries(
        SQLGenerationRequest(plan=plan, schema_snapshot=snapshot)
    )
    validated = [
        validate_sql(query, snapshot).validated_query
        for query in generated.queries
    ]
    assert all(query is not None for query in validated)
    results = [execute_query(query) for query in validated]
    return InsightRequest(plan=plan, query_results=results)


def test_generate_six_facts_from_real_duckdb_results():
    """六个 Fact 必须直接来自 Phase 2 的真实查询结果。"""
    insight = generate_insight(build_real_insight_input())
    facts = {fact.metric: fact for fact in insight.facts}

    assert set(facts) == {
        "gmv",
        "orders",
        "active_users",
        "aov",
        "peak_orders",
        "coupon_cost",
    }
    assert facts["gmv"].model_dump() == {
        "fact_id": "fact_gmv",
        "statement": "GMV 本周为 680,309.00 CNY，上周为 751,318.00 CNY，环比下降 9.5%。",
        "metric": "gmv",
        "metric_label": "GMV",
        "unit": "CNY",
        "current_value": 680309.0,
        "previous_value": 751318.0,
        "change_rate": -9.5,
        "source_step_id": "verify_gmv_change",
    }
    assert facts["orders"].source_step_id == "decompose_gmv"
    assert facts["active_users"].change_rate == 0.7
    assert facts["aov"].change_rate == 0.0
    assert facts["peak_orders"].source_step_id == "check_supporting_signals"
    assert facts["coupon_cost"].unit == "CNY"


def test_interpretations_use_three_reasoning_types_and_valid_fact_links():
    """比较、拆解和相关性解释都必须绑定有效 Fact。"""
    insight = generate_insight(build_real_insight_input())
    fact_ids = {fact.fact_id for fact in insight.facts}

    assert {item.reasoning_type for item in insight.interpretations} == {
        "comparison",
        "decomposition",
        "correlation",
    }
    assert all(
        set(item.supporting_fact_ids) <= fact_ids
        for item in insight.interpretations
    )
    assert any(
        item.statement
        == "订单量下降与 GMV 下滑方向一致，是当前数据中最显著的关联因素。"
        for item in insight.interpretations
    )
    assert not any(
        term in item.statement
        for item in insight.interpretations
        for term in CAUSAL_TERMS
    )


def test_limitations_cover_causality_external_variables_and_marketing_effect():
    """限制说明必须覆盖三条已确认的证据边界。"""
    insight = generate_insight(build_real_insight_input())
    statements = [limitation.statement for limitation in insight.limitations]

    assert "当前数据只能支持相关性分析，不能证明因果关系。" in statements
    assert "缺少库存、天气、竞品、营销曝光等外部解释变量。" in statements
    assert (
        "优惠券成本只能说明已观测投入变化，不能单独说明营销效果。"
        in statements
    )


def test_insight_contract_rejects_causal_interpretation():
    """即使 Agent 误写因果措辞，Pydantic 边界也必须拒绝。"""
    fact = Fact(
        fact_id="fact_gmv",
        statement="GMV 环比下降 9.5%。",
        metric="gmv",
        metric_label="GMV",
        unit="CNY",
        current_value=680309,
        previous_value=751318,
        change_rate=-9.5,
        source_step_id="verify_gmv_change",
    )

    with pytest.raises(ValidationError, match="不得使用因果措辞"):
        InsightResult(
            facts=[fact],
            interpretations=[
                Interpretation(
                    statement="订单量下降导致 GMV 下滑。",
                    supporting_fact_ids=["fact_gmv"],
                    reasoning_type="correlation",
                )
            ],
            limitations=[],
        )
