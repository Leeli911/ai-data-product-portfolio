import pytest

from contracts import AnalysisPlan, AnalysisStep, IntentResult, SQLGenerationRequest
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries


def build_plan(step_ids=None):
    """构造 SQL Agent 所需的黄金分析计划。"""
    step_ids = step_ids or [
        "verify_gmv_change",
        "decompose_gmv",
        "check_supporting_signals",
    ]
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
        steps=[
            AnalysisStep(
                step_id=step_id,
                goal=step_id,
                required_metrics=["gmv"],
                group_by=["period"],
            )
            for step_id in step_ids
        ],
    )


def test_generate_one_grounded_query_for_each_plan_step():
    """三条必需路径必须各自产生一条可追溯的候选 SQL。"""
    request = SQLGenerationRequest(
        plan=build_plan(),
        schema_snapshot=build_schema_snapshot(),
    )

    result = generate_queries(request)

    assert [query.step_id for query in result.queries] == [
        "verify_gmv_change",
        "decompose_gmv",
        "check_supporting_signals",
    ]
    assert all(query.sql.lstrip().upper().startswith("WITH") for query in result.queries)
    assert all("*" not in query.sql for query in result.queries)
    assert all("dim_district" in query.sql for query in result.queries)
    assert "fact_marketing_cost" in result.queries[2].sql


def test_generate_queries_refuses_unknown_plan_step():
    """SQL Agent 遇到未知步骤时必须失败，不能编造查询。"""
    request = SQLGenerationRequest(
        plan=build_plan(["unknown_step"]),
        schema_snapshot=build_schema_snapshot(),
    )

    with pytest.raises(ValueError, match="不支持的分析步骤"):
        generate_queries(request)


def test_generate_queries_requires_catalog_tables():
    """Schema Snapshot 缺表时不应继续生成看似可用的 SQL。"""
    snapshot = build_schema_snapshot()
    incomplete_snapshot = snapshot.model_copy(
        update={
            "tables": [
                table for table in snapshot.tables if table.name != "dim_district"
            ]
        }
    )
    request = SQLGenerationRequest(
        plan=build_plan(),
        schema_snapshot=incomplete_snapshot,
    )

    with pytest.raises(ValueError, match="Schema Snapshot 缺少表"):
        generate_queries(request)
