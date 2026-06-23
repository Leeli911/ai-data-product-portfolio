"""Text2Analytics Phase 1 的类型化输入输出契约。"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


CAUSAL_TERMS = ("导致", "证明", "必然因为", "根本原因是")


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


class Fact(BaseModel):
    """由查询结果直接支持的业务事实。"""

    fact_id: str
    statement: str
    metric: str
    metric_label: str
    unit: str
    current_value: float
    previous_value: float
    change_rate: float
    source_step_id: str


class Interpretation(BaseModel):
    """引用 Fact 的非因果分析解释。"""

    statement: str
    supporting_fact_ids: list[str]
    reasoning_type: Literal["comparison", "decomposition", "correlation"]


class Limitation(BaseModel):
    """数据不足或当前方法不能判断的部分。"""

    statement: str
    impact: str
    missing_data: list[str]


class InsightRequest(BaseModel):
    """Insight Agent 的类型化输入。"""

    plan: AnalysisPlan
    query_results: list[QueryExecutionResult]


class InsightResult(BaseModel):
    """严格分离事实、解释和限制的分析输出。"""

    facts: list[Fact]
    interpretations: list[Interpretation]
    limitations: list[Limitation]

    @model_validator(mode="after")
    def validate_evidence_links(self):
        """确保解释绑定有效事实并拒绝因果措辞。"""
        fact_ids = {fact.fact_id for fact in self.facts}
        if len(fact_ids) != len(self.facts):
            raise ValueError("Fact ID 不能重复")

        for interpretation in self.interpretations:
            supporting_ids = set(interpretation.supporting_fact_ids)
            if not supporting_ids:
                raise ValueError("Interpretation 必须引用至少一个 Fact")
            if not supporting_ids <= fact_ids:
                raise ValueError("Interpretation 引用了不存在的 Fact")
            if any(
                term in interpretation.statement for term in CAUSAL_TERMS
            ):
                raise ValueError("Interpretation 不得使用因果措辞")
        return self


class ConfidenceFactor(BaseModel):
    """置信度规则中的一个可展示加减分因素。"""

    name: str
    impact: float
    reason: str


class ConfidenceAssessment(BaseModel):
    """证据完整度分数及全部评分依据。"""

    score: float
    factors: list[ConfidenceFactor]


class ConfidenceRequest(BaseModel):
    """Confidence Calculator 的类型化输入。"""

    intent: IntentResult
    plan_validation: PlanValidationResult
    query_results: list[QueryExecutionResult]
    insight: InsightResult


class PipelineError(BaseModel):
    """流水线失败阶段的结构化错误。"""

    failed_stage: str
    error_code: str
    message: str


class AnalyticsResponse(BaseModel):
    """Phase 1–4 完整流水线的统一响应。"""

    status: Literal["success", "failed", "insufficient_evidence"]
    request: AnalyticsRequest
    intent: IntentResult | None = None
    plan: AnalysisPlan | None = None
    plan_validation: PlanValidationResult | None = None
    generated_queries: list[GeneratedQuery] = Field(default_factory=list)
    sql_validations: list[SQLValidationResult] = Field(default_factory=list)
    query_results: list[QueryExecutionResult] = Field(default_factory=list)
    insight: InsightResult | None = None
    confidence: ConfidenceAssessment | None = None
    completed_stages: list[str] = Field(default_factory=list)
    error: PipelineError | None = None


class EvaluationCase(BaseModel):
    """一个带预期结果的确定性评测案例。"""

    case_id: str
    category: Literal["success", "ambiguous", "unsupported", "adversarial"]
    question: str
    expected_outcome: Literal["success", "ambiguous", "unsupported", "rejected"]
    expected_intent_type: Literal["drop_reason_analysis", "unsupported"]
    expected_metric: str | None = None
    expected_district: str | None = None
    expected_time_range: str | None = None


class EvaluationRequest(BaseModel):
    """Evaluation Runner 的类型化输入。"""

    cases: list[EvaluationCase]


class EvaluationDimensionResult(BaseModel):
    """单个评测维度的结果和可审查理由。"""

    dimension: str
    passed: bool
    score: float
    details: list[str]


class EvaluationCaseResult(BaseModel):
    """一个案例的预期、实际结果和六维评测。"""

    case_id: str
    question: str
    expected_outcome: str
    actual_outcome: str
    dimensions: list[EvaluationDimensionResult]
    passed: bool


class EvaluationSummary(BaseModel):
    """案例级和维度级聚合结果。"""

    total_cases: int
    passed_cases: int
    case_pass_rate: float
    dimension_pass_rates: dict[str, float]


class EvaluationReport(BaseModel):
    """可序列化的完整 Evaluation 报告。"""

    summary: EvaluationSummary
    cases: list[EvaluationCaseResult]
