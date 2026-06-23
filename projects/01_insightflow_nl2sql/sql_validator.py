"""独立于 SQL Agent 的只读 SQL 与 Schema Guardrail。"""

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from contracts import (
    GeneratedQuery,
    SQLValidationResult,
    SchemaSnapshot,
    ValidatedQuery,
)


def _invalid(*errors: str) -> SQLValidationResult:
    """构造统一的失败校验结果。"""
    return SQLValidationResult(is_valid=False, errors=list(errors))


def validate_sql(
    query: GeneratedQuery,
    snapshot: SchemaSnapshot,
) -> SQLValidationResult:
    """仅允许单条、只读、字段与表均已知的 SELECT。"""
    try:
        statements = parse(query.sql, read="duckdb")
    except ParseError as error:
        return _invalid(f"SQL 解析失败：{error}")

    if len(statements) != 1:
        return _invalid("只允许单条 SQL")

    statement = statements[0]
    if not isinstance(statement, exp.Select):
        return _invalid("只允许 SELECT 查询")

    errors = []
    if any(True for _ in statement.find_all(exp.Star)):
        errors.append("禁止使用通配符")

    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
    }
    referenced_tables = {
        table.name.lower()
        for table in statement.find_all(exp.Table)
        if table.name.lower() not in cte_names
    }
    unknown_tables = referenced_tables - {
        name.lower() for name in snapshot.table_names
    }
    errors.extend(f"未知表：{name}" for name in sorted(unknown_tables))

    derived_aliases = {
        alias.alias.lower()
        for alias in statement.find_all(exp.Alias)
        if alias.alias
    }
    referenced_column_names = {
        column.name.lower()
        for column in statement.find_all(exp.Column)
    }
    known_columns = {name.lower() for name in snapshot.column_names}
    unknown_columns = referenced_column_names - known_columns - derived_aliases
    errors.extend(f"未知字段：{name}" for name in sorted(unknown_columns))

    if errors:
        return SQLValidationResult(is_valid=False, errors=errors)

    return SQLValidationResult(
        is_valid=True,
        validated_query=ValidatedQuery(
            step_id=query.step_id,
            purpose=query.purpose,
            sql=query.sql,
            referenced_tables=sorted(referenced_tables),
            referenced_columns=sorted(
                referenced_column_names & known_columns
            ),
        ),
    )
