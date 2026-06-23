import pytest

from contracts import AnalyticsRequest, GeneratedQuery, SQLGenerationRequest
from intent_agent import understand_intent
from planner_agent import create_analysis_plan
from query_executor import execute_query
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries
from sql_validator import validate_sql


def execute_golden_queries():
    """运行从黄金问题到 DuckDB 的 Phase 2 链路。"""
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
    return [execute_query(query) for query in validated]


def rows_by_period(result):
    """把两行周期结果转换为便于断言的映射。"""
    return {row["period"]: row for row in result.rows}


def test_execute_three_validated_queries_against_real_csv_data():
    """三条查询都应从 DuckDB 返回 current/previous 两期结果。"""
    results = execute_golden_queries()

    assert [result.step_id for result in results] == [
        "verify_gmv_change",
        "decompose_gmv",
        "check_supporting_signals",
    ]
    assert all(result.row_count == 2 for result in results)
    assert all(
        set(rows_by_period(result)) == {"current", "previous"}
        for result in results
    )


def test_execute_golden_queries_returns_expected_business_values():
    """黄金数据的 GMV、拆解指标和辅助信号必须可复现。"""
    gmv_result, decomposition_result, supporting_result = (
        execute_golden_queries()
    )
    gmv = rows_by_period(gmv_result)
    decomposition = rows_by_period(decomposition_result)
    supporting = rows_by_period(supporting_result)

    assert gmv["current"]["gmv"] == 680309.0
    assert gmv["previous"]["gmv"] == 751318.0
    assert decomposition["current"]["orders"] == 6776.0
    assert decomposition["previous"]["orders"] == 7481.0
    assert decomposition["current"]["active_users"] == 6174.0
    assert decomposition["current"]["aov"] == pytest.approx(100.3998, rel=1e-5)
    assert supporting["current"]["peak_orders"] == 2096.0
    assert supporting["previous"]["peak_orders"] == 2316.0
    assert supporting["current"]["coupon_cost"] == 68027.0
    assert supporting["previous"]["coupon_cost"] == 75128.0


def test_executor_rejects_unvalidated_generated_query():
    """Executor 不能相信 SQL Agent 的候选输出已经安全。"""
    candidate = GeneratedQuery(
        step_id="unsafe",
        purpose="未校验候选",
        sql="SELECT gmv FROM fact_orders",
    )

    with pytest.raises(TypeError, match="ValidatedQuery"):
        execute_query(candidate)
