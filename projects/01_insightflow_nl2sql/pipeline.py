"""编排 Text2Analytics 黄金链路，并在失败阶段立即中止。"""

from pathlib import Path

from confidence import assess_confidence
from contracts import (
    AnalysisPlan,
    AnalyticsRequest,
    AnalyticsResponse,
    ConfidenceAssessment,
    ConfidenceRequest,
    GeneratedQuery,
    InsightRequest,
    InsightResult,
    IntentResult,
    PipelineError,
    PlanValidationResult,
    QueryExecutionResult,
    SQLGenerationRequest,
    SQLValidationResult,
)
from insight_agent import generate_insight
from intent_agent import understand_intent
from plan_validator import validate_plan
from planner_agent import create_analysis_plan
from query_executor import DEFAULT_DATA_DIR, execute_query
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries
from sql_validator import validate_sql


def _build_response(
    request: AnalyticsRequest,
    status: str,
    completed_stages: list[str],
    intent: IntentResult | None = None,
    plan: AnalysisPlan | None = None,
    plan_validation: PlanValidationResult | None = None,
    generated_queries: list[GeneratedQuery] | None = None,
    sql_validations: list[SQLValidationResult] | None = None,
    query_results: list[QueryExecutionResult] | None = None,
    insight: InsightResult | None = None,
    confidence: ConfidenceAssessment | None = None,
    error: PipelineError | None = None,
) -> AnalyticsResponse:
    """把当前阶段产物收敛成统一响应。"""
    return AnalyticsResponse(
        status=status,
        request=request,
        intent=intent,
        plan=plan,
        plan_validation=plan_validation,
        generated_queries=generated_queries or [],
        sql_validations=sql_validations or [],
        query_results=query_results or [],
        insight=insight,
        confidence=confidence,
        completed_stages=completed_stages,
        error=error,
    )


def _error(stage: str, code: str, message: str) -> PipelineError:
    """构造一致的阶段错误。"""
    return PipelineError(
        failed_stage=stage,
        error_code=code,
        message=message,
    )


def run_analytics(
    request: AnalyticsRequest,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> AnalyticsResponse:
    """依次调用已实现模块，失败时保留已完成阶段并立即返回。"""
    completed_stages = []

    intent = understand_intent(request)
    completed_stages.append("intent")
    if intent.intent_type == "unsupported":
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            error=_error(
                "intent",
                "INTENT_UNSUPPORTED",
                "当前阶段不支持该分析意图。",
            ),
        )
    if intent.ambiguities:
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            error=_error(
                "intent",
                "INTENT_AMBIGUOUS",
                "；".join(intent.ambiguities),
            ),
        )

    plan = create_analysis_plan(intent)
    completed_stages.append("plan")
    plan_validation = validate_plan(plan)
    completed_stages.append("plan_validation")
    if not plan_validation.is_valid:
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            plan=plan,
            plan_validation=plan_validation,
            error=_error(
                "plan_validation",
                "PLAN_INVALID",
                "；".join(plan_validation.errors),
            ),
        )

    schema_snapshot = build_schema_snapshot()
    try:
        generation = generate_queries(
            SQLGenerationRequest(
                plan=plan,
                schema_snapshot=schema_snapshot,
            )
        )
    except Exception as exception:
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            plan=plan,
            plan_validation=plan_validation,
            error=_error(
                "sql_generation",
                "SQL_GENERATION_FAILED",
                str(exception),
            ),
        )

    generated_queries = generation.queries
    completed_stages.append("sql_generation")
    sql_validations = [
        validate_sql(query, schema_snapshot)
        for query in generated_queries
    ]
    completed_stages.append("sql_validation")
    invalid_items = [
        (query, validation)
        for query, validation in zip(
            generated_queries,
            sql_validations,
            strict=True,
        )
        if not validation.is_valid or validation.validated_query is None
    ]
    if invalid_items:
        messages = [
            f"{query.step_id}: {'；'.join(validation.errors)}"
            for query, validation in invalid_items
        ]
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            plan=plan,
            plan_validation=plan_validation,
            generated_queries=generated_queries,
            sql_validations=sql_validations,
            error=_error(
                "sql_validation",
                "SQL_VALIDATION_FAILED",
                "；".join(messages),
            ),
        )

    query_results = []
    for validation in sql_validations:
        validated_query = validation.validated_query
        try:
            result = execute_query(validated_query, data_dir)
        except Exception as exception:
            return _build_response(
                request,
                "failed",
                completed_stages,
                intent=intent,
                plan=plan,
                plan_validation=plan_validation,
                generated_queries=generated_queries,
                sql_validations=sql_validations,
                query_results=query_results,
                error=_error(
                    "query_execution",
                    "QUERY_EXECUTION_FAILED",
                    str(exception),
                ),
            )
        query_results.append(result)
        if result.row_count == 0:
            return _build_response(
                request,
                "insufficient_evidence",
                completed_stages,
                intent=intent,
                plan=plan,
                plan_validation=plan_validation,
                generated_queries=generated_queries,
                sql_validations=sql_validations,
                query_results=query_results,
                error=_error(
                    "query_execution",
                    "EMPTY_QUERY_RESULT",
                    f"{result.step_id} 未返回数据。",
                ),
            )
    completed_stages.append("query_execution")

    try:
        insight = generate_insight(
            InsightRequest(plan=plan, query_results=query_results)
        )
    except Exception as exception:
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            plan=plan,
            plan_validation=plan_validation,
            generated_queries=generated_queries,
            sql_validations=sql_validations,
            query_results=query_results,
            error=_error(
                "insight",
                "INSIGHT_GENERATION_FAILED",
                str(exception),
            ),
        )
    completed_stages.append("insight")

    try:
        confidence = assess_confidence(
            ConfidenceRequest(
                intent=intent,
                plan_validation=plan_validation,
                query_results=query_results,
                insight=insight,
            )
        )
    except Exception as exception:
        return _build_response(
            request,
            "failed",
            completed_stages,
            intent=intent,
            plan=plan,
            plan_validation=plan_validation,
            generated_queries=generated_queries,
            sql_validations=sql_validations,
            query_results=query_results,
            insight=insight,
            error=_error(
                "confidence",
                "CONFIDENCE_ASSESSMENT_FAILED",
                str(exception),
            ),
        )
    completed_stages.append("confidence")

    return _build_response(
        request,
        "success",
        completed_stages,
        intent=intent,
        plan=plan,
        plan_validation=plan_validation,
        generated_queries=generated_queries,
        sql_validations=sql_validations,
        query_results=query_results,
        insight=insight,
        confidence=confidence,
    )
