"""Text2Analytics Phase 1 的类型化输入输出契约。"""

from typing import Literal

from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    """用户提交给分析流水线的业务问题。"""

    question: str
    dataset_id: str = "local_life_demo"


class IntentResult(BaseModel):
    """Intent Agent 对第一阶段问题的结构化理解。"""

    intent_type: Literal["drop_reason_analysis", "unsupported"]
    metric: str | None = None
    metric_label: str | None = None
    district: str | None = None
    time_range: str | None = None
    comparison_period: str | None = None
    ambiguities: list[str] = Field(default_factory=list)


class AnalysisStep(BaseModel):
    """一个可独立检查的分析步骤。"""

    step_id: str
    goal: str
    required_metrics: list[str]
    group_by: list[str]
    is_required: bool = True


class AnalysisPlan(BaseModel):
    """Planner Agent 输出的有序分析计划。"""

    intent: IntentResult
    steps: list[AnalysisStep]


class PlanValidationResult(BaseModel):
    """Plan Validator 对必需分析路径的检查结果。"""

    is_valid: bool
    missing_step_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ColumnSchema(BaseModel):
    """Schema Catalog 中一个可供 SQL 使用的字段。"""

    name: str
    semantic_type: str


class TableSchema(BaseModel):
    """一张表的最小字段快照。"""

    name: str
    columns: list[ColumnSchema]


class SchemaSnapshot(BaseModel):
    """SQL Agent 与 Validator 共用的已知 Schema。"""

    tables: list[TableSchema]

    @property
    def table_names(self) -> set[str]:
        """返回所有允许访问的物理表名。"""
        return {table.name for table in self.tables}

    @property
    def column_names(self) -> set[str]:
        """返回所有已知物理字段名。"""
        return {
            column.name
            for table in self.tables
            for column in table.columns
        }


class SQLGenerationRequest(BaseModel):
    """SQL Agent 的类型化输入。"""

    plan: AnalysisPlan
    schema_snapshot: SchemaSnapshot


class GeneratedQuery(BaseModel):
    """尚未通过独立安全校验的候选 SQL。"""

    step_id: str
    purpose: str
    sql: str


class SQLGenerationResult(BaseModel):
    """SQL Agent 为计划生成的候选查询集合。"""

    queries: list[GeneratedQuery]


class ValidatedQuery(BaseModel):
    """SQL Validator 校验通过后才可执行的查询。"""

    step_id: str
    purpose: str
    sql: str
    referenced_tables: list[str]
    referenced_columns: list[str]


class SQLValidationResult(BaseModel):
    """独立 SQL 安全校验的结构化结果。"""

    is_valid: bool
    validated_query: ValidatedQuery | None = None
    errors: list[str] = Field(default_factory=list)


JsonScalar = str | int | float | bool | None


class QueryExecutionResult(BaseModel):
    """DuckDB 查询返回的列、行和行数。"""

    step_id: str
    columns: list[str]
    rows: list[dict[str, JsonScalar]]
    row_count: int
