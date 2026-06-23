import pytest

from confidence import assess_confidence
from contracts import (
    AnalyticsRequest,
    ConfidenceRequest,
    InsightRequest,
    SQLGenerationRequest,
)
from insight_agent import generate_insight
from intent_agent import understand_intent
from plan_validator import validate_plan
from planner_agent import create_analysis_plan
from query_executor import execute_query
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries
from sql_validator import validate_sql


def build_complete_confidence_request():
    """构造包含真实查询结果和 Insight 的完整评分输入。"""
    snapshot = build_schema_snapshot()
    intent = understand_intent(
        AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    )
    plan = create_analysis_plan(intent)
    plan_validation = validate_plan(plan)
    generated = generate_queries(
        SQLGenerationRequest(plan=plan, schema_snapshot=snapshot)
    )
    validated = [
        validate_sql(query, snapshot).validated_query
        for query in generated.queries
    ]
    assert all(query is not None for query in validated)
    query_results = [execute_query(query) for query in validated]
    insight = generate_insight(
        InsightRequest(plan=plan, query_results=query_results)
    )
    return ConfidenceRequest(
        intent=intent,
        plan_validation=plan_validation,
        query_results=query_results,
        insight=insight,
    )


def test_complete_golden_path_has_explainable_evidence_score():
    """完整链路得到 0.90，并返回全部八个评分因素。"""
    assessment = assess_confidence(build_complete_confidence_request())
    factors = {factor.name: factor for factor in assessment.factors}

    assert assessment.score == 0.90
    assert set(factors) == {
        "intent_complete",
        "plan_coverage",
        "sql_execution",
        "period_completeness",
        "evidence_binding",
        "missing_supporting_data",
        "insufficient_decomposition",
        "correlation_limitation",
    }
    assert factors["intent_complete"].impact == 0.10
    assert factors["plan_coverage"].impact == 0.10
    assert factors["sql_execution"].impact == 0.10
    assert factors["period_completeness"].impact == 0.10
    assert factors["evidence_binding"].impact == 0.10
    assert factors["missing_supporting_data"].impact == 0.0
    assert factors["insufficient_decomposition"].impact == 0.0
    assert factors["correlation_limitation"].impact == -0.10
    assert all(factor.reason for factor in assessment.factors)
    assert assessment.score == pytest.approx(
        0.50 + sum(factor.impact for factor in assessment.factors)
    )


def test_missing_query_paths_reduce_evidence_completeness():
    """查询路径不完整时必须失去执行加分并触发缺失数据扣分。"""
    complete = build_complete_confidence_request()
    incomplete = complete.model_copy(
        update={"query_results": complete.query_results[:1]}
    )

    assessment = assess_confidence(incomplete)
    factors = {factor.name: factor for factor in assessment.factors}

    assert assessment.score < 0.90
    assert factors["sql_execution"].impact == 0.0
    assert factors["period_completeness"].impact == 0.0
    assert factors["missing_supporting_data"].impact == -0.10
    assert factors["insufficient_decomposition"].impact == -0.10


def test_confidence_score_is_always_clamped_to_design_range():
    """Evidence completeness 始终限制在 0.10 到 0.95。"""
    assessment = assess_confidence(build_complete_confidence_request())

    assert 0.10 <= assessment.score <= 0.95
