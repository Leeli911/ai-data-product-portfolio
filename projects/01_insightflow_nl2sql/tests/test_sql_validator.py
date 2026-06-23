import pytest

from contracts import GeneratedQuery, SQLGenerationRequest
from intent_agent import understand_intent
from planner_agent import create_analysis_plan
from schema_provider import build_schema_snapshot
from sql_agent import generate_queries
from sql_validator import validate_sql
from contracts import AnalyticsRequest


def build_query(sql):
    """构造 Guardrail 测试使用的候选 SQL。"""
    return GeneratedQuery(
        step_id="verify_gmv_change",
        purpose="验证 GMV",
        sql=sql,
    )


def test_validator_accepts_known_read_only_query():
    """只读且使用已知表字段的查询应通过。"""
    result = validate_sql(
        build_query("SELECT gmv FROM fact_orders"),
        build_schema_snapshot(),
    )

    assert result.is_valid is True
    assert result.errors == []
    assert result.validated_query is not None
    assert result.validated_query.referenced_tables == ["fact_orders"]
    assert result.validated_query.referenced_columns == ["gmv"]


@pytest.mark.parametrize(
    ("sql", "expected_error"),
    [
        ("SELECT gmv FROM secret_orders", "未知表：secret_orders"),
        ("SELECT profit FROM fact_orders", "未知字段：profit"),
        ("DELETE FROM fact_orders", "只允许 SELECT 查询"),
        (
            "SELECT gmv FROM fact_orders; DROP TABLE fact_orders",
            "只允许单条 SQL",
        ),
        ("SELECT * FROM fact_orders", "禁止使用通配符"),
    ],
)
def test_validator_rejects_unsafe_or_ungrounded_sql(sql, expected_error):
    """Validator 必须独立拒绝危险语句和未知 Schema。"""
    result = validate_sql(build_query(sql), build_schema_snapshot())

    assert result.is_valid is False
    assert result.validated_query is None
    assert expected_error in result.errors


def test_validator_accepts_all_three_generated_queries():
    """SQL Agent 的候选查询仍须逐条通过独立 Validator。"""
    snapshot = build_schema_snapshot()
    intent = understand_intent(
        AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    )
    plan = create_analysis_plan(intent)
    generated = generate_queries(
        SQLGenerationRequest(plan=plan, schema_snapshot=snapshot)
    )

    validations = [validate_sql(query, snapshot) for query in generated.queries]

    assert all(validation.is_valid for validation in validations)
    assert all(
        validation.validated_query is not None
        for validation in validations
    )
