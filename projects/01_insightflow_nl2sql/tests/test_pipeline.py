from pathlib import Path

import pipeline
from contracts import (
    AnalyticsRequest,
    PlanValidationResult,
    QueryExecutionResult,
    SQLValidationResult,
)


GOLDEN_QUESTION = "为什么北京朝阳区本周 GMV 下滑？"
SUCCESS_STAGES = [
    "intent",
    "plan",
    "plan_validation",
    "sql_generation",
    "sql_validation",
    "query_execution",
    "insight",
    "confidence",
]


def test_golden_question_returns_complete_success_response():
    """Phase 1–3 应被串成一个完整、类型化的黄金响应。"""
    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "success"
    assert response.error is None
    assert response.intent.intent_type == "drop_reason_analysis"
    assert response.plan_validation.is_valid is True
    assert len(response.generated_queries) == 3
    assert len(response.sql_validations) == 3
    assert all(item.is_valid for item in response.sql_validations)
    assert len(response.query_results) == 3
    assert len(response.insight.facts) == 6
    assert response.confidence.score == 0.90
    assert response.completed_stages == SUCCESS_STAGES


def test_unsupported_intent_stops_before_planning():
    """超范围问题应在 Intent 阶段结构化失败。"""
    response = pipeline.run_analytics(
        AnalyticsRequest(question="分析北京朝阳区本周转化漏斗")
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "intent"
    assert response.error.error_code == "INTENT_UNSUPPORTED"
    assert response.completed_stages == ["intent"]
    assert response.plan is None
    assert response.confidence is None


def test_ambiguous_intent_stops_before_planning():
    """缺少指标和时间的输入不得继续生成看似完整的计划。"""
    response = pipeline.run_analytics(
        AnalyticsRequest(question="为什么朝阳区下滑？")
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "intent"
    assert response.error.error_code == "INTENT_AMBIGUOUS"
    assert response.completed_stages == ["intent"]
    assert response.confidence is None


def test_invalid_plan_returns_structured_error(monkeypatch):
    """Plan Validator 拒绝后不得进入 SQL 生成。"""
    monkeypatch.setattr(
        pipeline,
        "validate_plan",
        lambda plan: PlanValidationResult(
            is_valid=False,
            missing_step_ids=["decompose_gmv"],
            errors=["缺少必需分析步骤：decompose_gmv"],
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "generate_queries",
        lambda request: (_ for _ in ()).throw(
            AssertionError("Plan 失败后不应生成 SQL")
        ),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "plan_validation"
    assert response.error.error_code == "PLAN_INVALID"
    assert response.completed_stages == [
        "intent",
        "plan",
        "plan_validation",
    ]
    assert response.confidence is None


def test_sql_generation_exception_returns_structured_error(monkeypatch):
    """SQL Agent 异常不得泄漏为未处理异常。"""
    monkeypatch.setattr(
        pipeline,
        "generate_queries",
        lambda request: (_ for _ in ()).throw(RuntimeError("generation boom")),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "sql_generation"
    assert response.error.error_code == "SQL_GENERATION_FAILED"
    assert response.completed_stages == [
        "intent",
        "plan",
        "plan_validation",
    ]
    assert response.confidence is None


def test_sql_validation_failure_prevents_all_execution(monkeypatch):
    """任一必需 SQL 未通过时，一条查询都不能执行。"""
    monkeypatch.setattr(
        pipeline,
        "validate_sql",
        lambda query, snapshot: SQLValidationResult(
            is_valid=False,
            errors=["未知字段：profit"],
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "execute_query",
        lambda query, data_dir: (_ for _ in ()).throw(
            AssertionError("SQL 校验失败后不应执行查询")
        ),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "sql_validation"
    assert response.error.error_code == "SQL_VALIDATION_FAILED"
    assert response.query_results == []
    assert response.insight is None
    assert response.confidence is None


def test_query_execution_failure_prevents_insight(monkeypatch):
    """任一必需查询异常后不得生成 Insight。"""
    monkeypatch.setattr(
        pipeline,
        "execute_query",
        lambda query, data_dir: (_ for _ in ()).throw(
            RuntimeError("execution boom")
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "generate_insight",
        lambda request: (_ for _ in ()).throw(
            AssertionError("查询失败后不应生成 Insight")
        ),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "query_execution"
    assert response.error.error_code == "QUERY_EXECUTION_FAILED"
    assert response.insight is None
    assert response.confidence is None


def test_empty_query_result_returns_insufficient_evidence(monkeypatch):
    """查询成功但无数据时应返回证据不足，而不是空洞 Insight。"""
    monkeypatch.setattr(
        pipeline,
        "execute_query",
        lambda query, data_dir: QueryExecutionResult(
            step_id=query.step_id,
            columns=[],
            rows=[],
            row_count=0,
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "generate_insight",
        lambda request: (_ for _ in ()).throw(
            AssertionError("空结果不应生成 Insight")
        ),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "insufficient_evidence"
    assert response.error.failed_stage == "query_execution"
    assert response.error.error_code == "EMPTY_QUERY_RESULT"
    assert response.insight is None
    assert response.confidence is None


def test_insight_generation_failure_returns_structured_error(monkeypatch):
    """Insight Agent 异常应保留查询结果并返回结构化错误。"""
    monkeypatch.setattr(
        pipeline,
        "generate_insight",
        lambda request: (_ for _ in ()).throw(RuntimeError("insight boom")),
    )

    response = pipeline.run_analytics(
        AnalyticsRequest(question=GOLDEN_QUESTION)
    )

    assert response.status == "failed"
    assert response.error.failed_stage == "insight"
    assert response.error.error_code == "INSIGHT_GENERATION_FAILED"
    assert len(response.query_results) == 3
    assert response.insight is None
    assert response.confidence is None


def test_pipeline_source_contains_orchestration_only():
    """Pipeline 不得吸收 SQL、指标、解释或评分实现细节。"""
    source = Path(pipeline.__file__).read_text(encoding="utf-8")
    forbidden_details = [
        "SELECT ",
        "WITH bounds",
        "SUM(",
        "INTERVAL",
        "change_rate",
        "CAUSAL_TERMS",
        "BASE_CONFIDENCE",
        "订单量下降与 GMV",
        "sqlglot",
        "duckdb",
    ]

    assert not any(detail in source for detail in forbidden_details)
