# Text2Analytics Golden Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one deterministic, type-safe, evidence-grounded analytics path for “为什么北京朝阳区本周 GMV 下滑？”, including SQL safety, explainable insight, confidence, evaluation, Streamlit display, and research-portfolio documentation.

**Architecture:** Keep the existing project simple and add focused Python modules connected only through Pydantic models. The pipeline orchestrates deterministic agents, an independent SQL validator, DuckDB execution, evidence-bound insight, and structured failure states; legacy parser and analytics modules remain untouched until the new path is proven.

**Tech Stack:** Python 3.10+, Pydantic 2, DuckDB, sqlglot, pandas, Streamlit, pytest

---

## Scope and working rules

- Work only in `projects/01_insightflow_nl2sql` unless updating the root implementation plan.
- Do not modify or stage the existing untracked `schema_profiler.py`, `data/schema_profiles.json`, or `tests/test_schema_profiler.py` as part of unrelated commits.
- Use TDD for every behavior: failing test, focused implementation, passing test, full-stage pytest, commit.
- Do not add LLM providers, LangGraph, CrewAI, AutoGen, remote APIs, funnel analysis, cohort analysis, authentication, or multiple datasets.
- At every P1–P6 checkpoint, run the full project test suite and report files changed, runnable flow, passing tests, and unresolved issues.

## File map

### New production files

- `projects/01_insightflow_nl2sql/contracts.py`: all cross-module Pydantic models and evidence invariants.
- `projects/01_insightflow_nl2sql/schema_provider.py`: convert the existing catalog to a typed snapshot.
- `projects/01_insightflow_nl2sql/intent_agent.py`: deterministic golden-question intent parsing.
- `projects/01_insightflow_nl2sql/planner_agent.py`: deterministic three-step analysis plan.
- `projects/01_insightflow_nl2sql/plan_validator.py`: required-path validation.
- `projects/01_insightflow_nl2sql/sql_agent.py`: deterministic DuckDB query generation.
- `projects/01_insightflow_nl2sql/sql_validator.py`: independent AST and schema validation.
- `projects/01_insightflow_nl2sql/query_executor.py`: DuckDB CSV view setup and read-only query execution.
- `projects/01_insightflow_nl2sql/insight_agent.py`: Fact, Interpretation, and Limitation construction.
- `projects/01_insightflow_nl2sql/confidence.py`: evidence-completeness score and factors.
- `projects/01_insightflow_nl2sql/pipeline.py`: orchestration and typed failure termination only.
- `projects/01_insightflow_nl2sql/evaluation.py`: six-dimension evaluation and report writing.
- `projects/01_insightflow_nl2sql/evaluation_cases.json`: 20 deterministic cases.

### New tests

- `tests/test_contracts.py`
- `tests/test_intent_agent.py`
- `tests/test_planner_agent.py`
- `tests/test_plan_validator.py`
- `tests/test_schema_provider.py`
- `tests/test_sql_agent.py`
- `tests/test_sql_validator.py`
- `tests/test_query_executor.py`
- `tests/test_insight_agent.py`
- `tests/test_confidence.py`
- `tests/test_pipeline.py`
- `tests/test_evaluation_v2.py`

### Modified files

- `requirements.txt`: add Pydantic, DuckDB, and sqlglot.
- `app.py`: consume `AnalyticsResponse` and render the new workflow without analysis logic.
- `tests/test_app_smoke.py`: replace the legacy workflow assertion with a rendering-boundary smoke test.
- `README.md`: rewrite as an evidence-based analytics research portfolio project.

## P1 — Typed intent and plan slice

### Task 1: Add dependencies and cross-module contracts

**Files:**
- Modify: `projects/01_insightflow_nl2sql/requirements.txt`
- Create: `projects/01_insightflow_nl2sql/contracts.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_contracts.py`

- [ ] **Step 1: Add a failing contract test**

Create `tests/test_contracts.py` with tests that instantiate `AnalyticsRequest`, `IntentResult`, `AnalysisPlan`, `GeneratedQuery`, `QueryExecutionResult`, `InsightResult`, `ConfidenceAssessment`, `PipelineError`, and `AnalyticsResponse`. Include this invariant test:

```python
import pytest
from pydantic import ValidationError

from contracts import Fact, InsightResult, Interpretation, Limitation


def test_interpretation_must_reference_an_existing_fact():
    with pytest.raises(ValidationError):
        InsightResult(
            facts=[],
            interpretations=[
                Interpretation(
                    statement="订单量与 GMV 同向下降。",
                    supporting_fact_ids=["missing"],
                    reasoning_type="correlation",
                )
            ],
            limitations=[
                Limitation(
                    statement="观察数据不能证明因果。",
                    impact="只能解释相关性。",
                    missing_data=["inventory"],
                )
            ],
        )


def test_interpretation_rejects_causal_wording():
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
    with pytest.raises(ValidationError):
        InsightResult(
            facts=[fact],
            interpretations=[
                Interpretation(
                    statement="订单下降导致 GMV 下滑。",
                    supporting_fact_ids=["fact_gmv"],
                    reasoning_type="correlation",
                )
            ],
            limitations=[],
        )
```

- [ ] **Step 2: Run the contract tests and verify the red state**

Run: `cd projects/01_insightflow_nl2sql && pytest tests/test_contracts.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'contracts'`.

- [ ] **Step 3: Add explicit runtime dependencies**

Set `requirements.txt` to:

```text
pytest
pandas
streamlit
pydantic>=2.5,<3
duckdb>=1.1,<2
sqlglot>=25,<30
```

Run: `python -m pip install -r requirements.txt`

Expected: Pydantic 2, DuckDB, and sqlglot import successfully.

- [ ] **Step 4: Implement the complete contract set**

Create `contracts.py` with the exact models from the approved design. Use `Field(default_factory=list)` for mutable lists and add this `InsightResult` validator:

```python
from typing import Literal

from pydantic import BaseModel, Field, model_validator


CAUSAL_TERMS = ("导致", "证明", "必然因为", "根本原因是")


class AnalyticsRequest(BaseModel):
    question: str
    dataset_id: str = "local_life_demo"


class ColumnSchema(BaseModel):
    name: str
    semantic_type: str


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema]


class SchemaSnapshot(BaseModel):
    tables: list[TableSchema]


class IntentResult(BaseModel):
    intent_type: Literal["drop_reason_analysis", "unsupported"]
    metric: str | None = None
    metric_label: str | None = None
    district: str | None = None
    time_range: str | None = None
    comparison_period: str | None = None
    ambiguities: list[str] = Field(default_factory=list)


class AnalysisStep(BaseModel):
    step_id: str
    goal: str
    required_metrics: list[str]
    group_by: list[str]
    is_required: bool = True


class AnalysisPlan(BaseModel):
    intent: IntentResult
    steps: list[AnalysisStep]


class PlanValidationResult(BaseModel):
    is_valid: bool
    missing_step_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class SQLGenerationRequest(BaseModel):
    plan: AnalysisPlan
    schema_snapshot: SchemaSnapshot


class GeneratedQuery(BaseModel):
    step_id: str
    purpose: str
    sql: str


class SQLGenerationResult(BaseModel):
    queries: list[GeneratedQuery]


class ValidatedQuery(BaseModel):
    step_id: str
    purpose: str
    sql: str
    referenced_tables: list[str]
    referenced_columns: list[str]


class SQLValidationResult(BaseModel):
    is_valid: bool
    validated_query: ValidatedQuery | None = None
    errors: list[str] = Field(default_factory=list)


JsonScalar = str | int | float | bool | None


class QueryExecutionResult(BaseModel):
    step_id: str
    columns: list[str]
    rows: list[dict[str, JsonScalar]]
    row_count: int


class Fact(BaseModel):
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
    statement: str
    supporting_fact_ids: list[str]
    reasoning_type: Literal["comparison", "correlation", "decomposition"]


class Limitation(BaseModel):
    statement: str
    impact: str
    missing_data: list[str]


class InsightRequest(BaseModel):
    plan: AnalysisPlan
    query_results: list[QueryExecutionResult]


class InsightResult(BaseModel):
    facts: list[Fact]
    interpretations: list[Interpretation]
    limitations: list[Limitation]

    @model_validator(mode="after")
    def validate_evidence_links(self):
        fact_ids = {fact.fact_id for fact in self.facts}
        for interpretation in self.interpretations:
            if not interpretation.supporting_fact_ids:
                raise ValueError("Interpretation 必须引用至少一个 Fact")
            if not set(interpretation.supporting_fact_ids) <= fact_ids:
                raise ValueError("Interpretation 引用了不存在的 Fact")
            if any(term in interpretation.statement for term in CAUSAL_TERMS):
                raise ValueError("Interpretation 不得使用因果措辞")
        return self


class ConfidenceFactor(BaseModel):
    name: str
    impact: float
    reason: str


class ConfidenceAssessment(BaseModel):
    score: float
    factors: list[ConfidenceFactor]


class ConfidenceRequest(BaseModel):
    intent: IntentResult
    plan_validation: PlanValidationResult
    query_results: list[QueryExecutionResult]
    insight: InsightResult


class PipelineError(BaseModel):
    failed_stage: str
    error_code: str
    message: str


class AnalyticsResponse(BaseModel):
    status: Literal["success", "failed", "insufficient_evidence"]
    request: AnalyticsRequest
    intent: IntentResult | None = None
    plan: AnalysisPlan | None = None
    generated_queries: list[GeneratedQuery] = Field(default_factory=list)
    query_results: list[QueryExecutionResult] = Field(default_factory=list)
    insight: InsightResult | None = None
    confidence: ConfidenceAssessment | None = None
    completed_stages: list[str] = Field(default_factory=list)
    error: PipelineError | None = None
```

Append the Evaluation models from Task 11 to the same file when P5 begins; do not create a second contracts module.

- [ ] **Step 5: Run tests and commit**

Run: `pytest tests/test_contracts.py -q`

Expected: PASS.

Commit:

```bash
git add requirements.txt contracts.py tests/test_contracts.py
git commit -m "feat: add typed analytics contracts"
```

### Task 2: Implement deterministic intent parsing

**Files:**
- Create: `projects/01_insightflow_nl2sql/intent_agent.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_intent_agent.py`

- [ ] **Step 1: Write failing tests**

Test the canonical question, the synonym `交易额`, missing metric, missing district, missing time, and funnel rejection. The canonical assertion is:

```python
from contracts import AnalyticsRequest
from intent_agent import understand_intent


def test_understand_canonical_drop_question():
    result = understand_intent(
        AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
    )
    assert result.intent_type == "drop_reason_analysis"
    assert result.metric == "gmv"
    assert result.metric_label == "GMV"
    assert result.district == "Chaoyang"
    assert result.time_range == "latest_7_days"
    assert result.comparison_period == "previous_7_days"
    assert result.ambiguities == []
```

- [ ] **Step 2: Verify red state**

Run: `pytest tests/test_intent_agent.py -q`

Expected: FAIL because `intent_agent` does not exist.

- [ ] **Step 3: Implement `understand_intent`**

Use deterministic keyword sets:

```python
GMV_TERMS = ("gmv", "交易额", "销售额")
DROP_TERMS = ("下降", "下滑", "减少", "回落")
UNSUPPORTED_TERMS = ("漏斗", "cohort", "留存", "登录", "删除", "更新", "远程数据库")


def understand_intent(request: AnalyticsRequest) -> IntentResult:
    question = request.question.strip()
    lowered = question.lower()
    metric = "gmv" if any(term in lowered for term in GMV_TERMS) else None
    district = "Chaoyang" if "朝阳" in question else None
    time_range = "latest_7_days" if "本周" in question else None
    comparison = "previous_7_days" if time_range else None
    is_drop = any(term in question for term in DROP_TERMS)
    is_unsupported = any(term in lowered for term in UNSUPPORTED_TERMS)
    ambiguities = []
    if metric is None:
        ambiguities.append("未识别到 GMV 指标")
    if district is None:
        ambiguities.append("未识别到朝阳区")
    if time_range is None:
        ambiguities.append("未识别到本周时间范围")
    intent_type = (
        "drop_reason_analysis"
        if is_drop and not is_unsupported
        else "unsupported"
    )
    return IntentResult(
        intent_type=intent_type,
        metric=metric,
        metric_label="GMV" if metric else None,
        district=district,
        time_range=time_range,
        comparison_period=comparison,
        ambiguities=ambiguities,
    )
```

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/test_intent_agent.py -q`

Expected: PASS.

Commit:

```bash
git add intent_agent.py tests/test_intent_agent.py
git commit -m "feat: add deterministic intent agent"
```

### Task 3: Implement planning and independent plan validation

**Files:**
- Create: `projects/01_insightflow_nl2sql/planner_agent.py`
- Create: `projects/01_insightflow_nl2sql/plan_validator.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_planner_agent.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_plan_validator.py`

- [ ] **Step 1: Write failing planner and validator tests**

Assert that the canonical intent produces exactly these ordered IDs:

```python
[
    "verify_gmv_change",
    "decompose_gmv",
    "check_supporting_signals",
]
```

Also build an `AnalysisPlan` missing `decompose_gmv` and assert `validate_plan` returns `is_valid=False` and `missing_step_ids == ["decompose_gmv"]`.

- [ ] **Step 2: Verify red state**

Run: `pytest tests/test_planner_agent.py tests/test_plan_validator.py -q`

Expected: FAIL because both modules are absent.

- [ ] **Step 3: Implement the planner**

Implement `create_analysis_plan(intent: IntentResult) -> AnalysisPlan`. Return an empty plan for unsupported or ambiguous intent; otherwise return:

```python
steps = [
    AnalysisStep(
        step_id="verify_gmv_change",
        goal="比较本周与上周 GMV，确认下滑幅度",
        required_metrics=["gmv"],
        group_by=["period"],
    ),
    AnalysisStep(
        step_id="decompose_gmv",
        goal="拆解订单量、活跃用户和客单价变化",
        required_metrics=["gmv", "orders", "active_users", "aov"],
        group_by=["period"],
    ),
    AnalysisStep(
        step_id="check_supporting_signals",
        goal="检查高峰订单和优惠券成本变化",
        required_metrics=["peak_orders", "coupon_cost"],
        group_by=["period"],
    ),
]
```

- [ ] **Step 4: Implement independent validation**

In `plan_validator.py` define:

```python
REQUIRED_STEP_IDS = (
    "verify_gmv_change",
    "decompose_gmv",
    "check_supporting_signals",
)


def validate_plan(plan: AnalysisPlan) -> PlanValidationResult:
    actual = {step.step_id for step in plan.steps}
    missing = [step_id for step_id in REQUIRED_STEP_IDS if step_id not in actual]
    errors = [f"缺少必需分析步骤：{step_id}" for step_id in missing]
    return PlanValidationResult(
        is_valid=not missing,
        missing_step_ids=missing,
        errors=errors,
    )
```

- [ ] **Step 5: Run P1 tests and full pytest**

Run: `pytest tests/test_contracts.py tests/test_intent_agent.py tests/test_planner_agent.py tests/test_plan_validator.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: all existing and P1 tests PASS.

- [ ] **Step 6: Commit and report P1 checkpoint**

```bash
git add planner_agent.py plan_validator.py tests/test_planner_agent.py tests/test_plan_validator.py
git commit -m "feat: add golden path analysis planning"
```

Report: files changed; `AnalyticsRequest -> IntentResult -> AnalysisPlan -> PlanValidationResult`; test counts; dependency or parsing limitations.

## P2 — Grounded SQL execution slice

### Task 4: Build a typed schema snapshot

**Files:**
- Create: `projects/01_insightflow_nl2sql/schema_provider.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_schema_provider.py`

- [ ] **Step 1: Test snapshot fidelity**

Assert `build_schema_snapshot()` contains exactly the three `SCHEMA_CATALOG` tables and that `fact_orders` exposes `order_date`, `district_id`, `gmv`, `orders`, `active_users`, and `peak_orders` with matching semantic types.

- [ ] **Step 2: Verify failure, implement, and pass**

Implement:

```python
def build_schema_snapshot() -> SchemaSnapshot:
    return SchemaSnapshot(
        tables=[
            TableSchema(
                name=table_name,
                columns=[
                    ColumnSchema(
                        name=column_name,
                        semantic_type=column["semantic_type"],
                    )
                    for column_name, column in definition["columns"].items()
                ],
            )
            for table_name, definition in SCHEMA_CATALOG.items()
        ]
    )
```

Run: `pytest tests/test_schema_provider.py -q`

Expected: PASS.

Commit: `git commit -m "feat: expose typed schema snapshot"` after staging only this module and test.

### Task 5: Generate deterministic SQL for all three plan steps

**Files:**
- Create: `projects/01_insightflow_nl2sql/sql_agent.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_sql_agent.py`

- [ ] **Step 1: Write failing tests**

Build `SQLGenerationRequest` from the canonical plan and snapshot. Assert three queries, matching step IDs, only `SELECT`/`WITH`, and required tables. Assert an unknown step raises `ValueError` rather than inventing SQL.

- [ ] **Step 2: Implement reusable period SQL**

Use one deterministic date-window CTE in each query:

```sql
WITH bounds AS (
    SELECT MAX(order_date::DATE) AS max_date FROM fact_orders
), periods AS (
    SELECT
        CASE
            WHEN order_date::DATE BETWEEN max_date - INTERVAL 6 DAY AND max_date THEN 'current'
            WHEN order_date::DATE BETWEEN max_date - INTERVAL 13 DAY AND max_date - INTERVAL 7 DAY THEN 'previous'
        END AS period,
        order_date,
        district_id,
        gmv,
        orders,
        active_users,
        peak_orders
    FROM fact_orders CROSS JOIN bounds
    WHERE order_date::DATE BETWEEN max_date - INTERVAL 13 DAY AND max_date
)
```

Generate:

- `verify_gmv_change`: period and `SUM(gmv) AS gmv`.
- `decompose_gmv`: period, `SUM(gmv)`, `SUM(orders)`, `SUM(active_users)`, and `SUM(gmv) / NULLIF(SUM(orders), 0) AS aov`.
- `check_supporting_signals`: two period CTEs that aggregate `peak_orders` and `coupon_cost`, then join by period.

Every query joins `dim_district` and filters `district_name_en = 'Chaoyang'`. Implement `generate_queries(request: SQLGenerationRequest) -> SQLGenerationResult` with a template map keyed by `step_id`.

- [ ] **Step 3: Run tests and commit**

Run: `pytest tests/test_sql_agent.py -q`

Expected: PASS.

Commit: `git commit -m "feat: generate golden path analytics SQL"` after staging only SQL Agent files.

### Task 6: Validate SQL independently with sqlglot

**Files:**
- Create: `projects/01_insightflow_nl2sql/sql_validator.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_sql_validator.py`

- [ ] **Step 1: Write failing guardrail tests**

Cover:

```python
safe = GeneratedQuery(
    step_id="verify_gmv_change",
    purpose="验证 GMV",
    sql="SELECT gmv FROM fact_orders",
)
unknown_table = safe.model_copy(update={"sql": "SELECT gmv FROM secret_orders"})
unknown_column = safe.model_copy(update={"sql": "SELECT profit FROM fact_orders"})
write_query = safe.model_copy(update={"sql": "DELETE FROM fact_orders"})
multi_statement = safe.model_copy(
    update={"sql": "SELECT gmv FROM fact_orders; DROP TABLE fact_orders"}
)
```

Assert only `safe` returns a `ValidatedQuery`; all others return `is_valid=False`, `validated_query=None`, and a specific error.

- [ ] **Step 2: Implement AST and schema checks**

Implement `validate_sql(query: GeneratedQuery, snapshot: SchemaSnapshot) -> SQLValidationResult` with `sqlglot.parse(sql, read="duckdb")`:

1. Require exactly one parsed statement.
2. Require the root expression to be `sqlglot.exp.Select`.
3. Reject every `exp.Star`.
4. Collect CTE aliases and exclude them from physical table checks.
5. Collect `exp.Table` names and require them in `SchemaSnapshot`.
6. Collect `exp.Alias` names; allow physical column names plus derived alias names.
7. Reject any remaining `exp.Column.name` outside that allowlist.
8. Return a typed `ValidatedQuery` only when the error list is empty.

The function must not call SQL Agent and must not execute SQL.

- [ ] **Step 3: Validate generated queries and commit**

Add a parametrized test that passes all three generated queries through `validate_sql`.

Run: `pytest tests/test_sql_validator.py tests/test_sql_agent.py -q`

Expected: PASS.

Commit: `git commit -m "feat: add independent SQL guardrails"`.

### Task 7: Execute validated queries in DuckDB

**Files:**
- Create: `projects/01_insightflow_nl2sql/query_executor.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_query_executor.py`

- [ ] **Step 1: Write failing executor tests**

Validate and execute all generated queries against `data/`. Assert:

- each result has `row_count == 2`;
- periods are `current` and `previous`;
- GMV current is `680309` and previous is `751318`;
- executor type annotation accepts `ValidatedQuery`, not `GeneratedQuery`.

- [ ] **Step 2: Implement isolated DuckDB setup**

In `query_executor.py`:

```python
DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"


def _open_demo_connection(data_dir: Path):
    connection = duckdb.connect(":memory:")
    for table in ("fact_orders", "dim_district", "fact_marketing_cost"):
        csv_path = str((data_dir / f"{table}.csv").resolve()).replace("'", "''")
        connection.execute(
            f"CREATE VIEW {table} AS SELECT * FROM read_csv_auto('{csv_path}')"
        )
    return connection


def execute_query(
    query: ValidatedQuery,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> QueryExecutionResult:
    connection = _open_demo_connection(Path(data_dir))
    try:
        cursor = connection.execute(query.sql)
        columns = [item[0] for item in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return QueryExecutionResult(
            step_id=query.step_id,
            columns=columns,
            rows=rows,
            row_count=len(rows),
        )
    finally:
        connection.close()
```

- [ ] **Step 3: Run P2 tests and full pytest**

Run: `pytest tests/test_schema_provider.py tests/test_sql_agent.py tests/test_sql_validator.py tests/test_query_executor.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: all P1, P2, and legacy tests PASS.

- [ ] **Step 4: Commit and report P2 checkpoint**

Commit: `git commit -m "feat: execute validated analytics SQL"` after staging only executor files.

Report the complete `AnalysisPlan -> GeneratedQuery -> ValidatedQuery -> QueryExecutionResult` path, test count, exact golden GMV values, and any DuckDB portability warning.

## P3 — Evidence and confidence slice

### Task 8: Generate evidence-bound insight

**Files:**
- Create: `projects/01_insightflow_nl2sql/insight_agent.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_insight_agent.py`

- [ ] **Step 1: Write failing evidence tests**

Run the P2 path and pass its three results into `generate_insight`. Assert:

- facts include `gmv`, `orders`, `active_users`, `aov`, `peak_orders`, `coupon_cost`;
- each fact has `metric_label`, `unit`, and a valid `source_step_id`;
- reasoning types include `comparison`, `decomposition`, and `correlation`;
- every supporting fact ID exists;
- no statement contains a term from `CAUSAL_TERMS`;
- limitations mention both causal uncertainty and missing external data.

- [ ] **Step 2: Implement deterministic fact construction**

Implement helpers:

```python
def calculate_change_rate(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 1)


def _rows_by_period(result: QueryExecutionResult) -> dict[str, dict]:
    return {str(row["period"]): row for row in result.rows}
```

Build six facts from the three step results. Use units `CNY`, `orders`, `users`, `CNY/order`, `orders`, and `CNY`. Use stable IDs such as `fact_gmv`, `fact_orders`, and `fact_aov`.

- [ ] **Step 3: Implement interpretations and limitations**

Return these three interpretation forms with real calculated rates inserted:

```text
comparison: GMV 本周较上周下降 X%。
decomposition: GMV、订单量与客单价的拆解显示，订单量下降而客单价基本稳定。
correlation: 订单量下降与 GMV 下滑方向一致，是当前数据中最显著的关联因素。
```

Return limitations stating that observational data cannot prove causality and that inventory, weather, competitors, and marketing exposure are unavailable.

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/test_insight_agent.py -q`

Expected: PASS.

Commit: `git commit -m "feat: add evidence-bound analytics insight"`.

### Task 9: Calculate evidence completeness

**Files:**
- Create: `projects/01_insightflow_nl2sql/confidence.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_confidence.py`

- [ ] **Step 1: Write failing scoring tests**

Construct a complete `ConfidenceRequest` and assert:

- score is between `0.10` and `0.95`;
- factors include positive intent, plan, execution, comparison, and evidence-link checks;
- at least one negative factor explains the correlation limitation;
- factor impacts sum with base `0.50` to the returned score.

- [ ] **Step 2: Implement explicit factors**

Implement `assess_confidence(request: ConfidenceRequest) -> ConfidenceAssessment` using the approved rule table. Determine completeness only from typed inputs. Clamp with:

```python
score = round(min(0.95, max(0.10, 0.50 + sum(f.impact for f in factors))), 2)
```

Do not estimate model probability and do not inspect raw SQL.

- [ ] **Step 3: Run P3 tests and full pytest**

Run: `pytest tests/test_insight_agent.py tests/test_confidence.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: all P1–P3 and legacy tests PASS.

- [ ] **Step 4: Commit and report P3 checkpoint**

Commit: `git commit -m "feat: score analytics evidence completeness"`.

Report the `QueryExecutionResult -> Fact -> Interpretation -> Limitation -> ConfidenceAssessment` path and confirm that no causal wording is emitted.

## P4 — Pipeline orchestration slice

### Task 10: Orchestrate success and every failure stage

**Files:**
- Create: `projects/01_insightflow_nl2sql/pipeline.py`
- Create: `projects/01_insightflow_nl2sql/tests/test_pipeline.py`

- [ ] **Step 1: Write failing success-path test**

Call:

```python
response = run_analytics(
    AnalyticsRequest(question="为什么北京朝阳区本周 GMV 下滑？")
)
```

Assert `status == "success"`, all eight display layers are populated, `completed_stages` is ordered, three queries and results exist, and confidence is present.

- [ ] **Step 2: Write failing termination tests**

Use monkeypatch to force failures at intent, plan validation, SQL generation, SQL validation, execution, and insight. Assert every response contains `PipelineError.failed_stage`, `error_code`, and `message`. Also assert:

- required execution failure produces no Insight or Confidence;
- zero-row result returns `insufficient_evidence`;
- SQL Validator rejection prevents executor invocation.

- [ ] **Step 3: Implement orchestration-only pipeline**

Implement `run_analytics(request: AnalyticsRequest, data_dir=DEFAULT_DATA_DIR) -> AnalyticsResponse` with sequential calls to the already-tested modules. Use a private response helper only to avoid repeated constructor boilerplate. The pipeline may inspect typed status fields such as `intent.ambiguities`, `plan_validation.is_valid`, `validation.is_valid`, and `result.row_count`; it must not contain metric names, SQL keywords, change-rate formulas, or insight text.

Required error codes:

```text
INTENT_UNSUPPORTED
INTENT_AMBIGUOUS
PLAN_INVALID
SQL_GENERATION_FAILED
SQL_VALIDATION_FAILED
QUERY_EXECUTION_FAILED
EMPTY_QUERY_RESULT
INSIGHT_GENERATION_FAILED
```

- [ ] **Step 4: Add a boundary test for forbidden pipeline logic**

Read `pipeline.py` as text and assert it does not contain `SUM(`, `gmv_change`, `CAUSAL_TERMS`, `sqlglot`, or confidence arithmetic. This guards architectural drift without replacing behavior tests.

- [ ] **Step 5: Run P4 tests and full pytest**

Run: `pytest tests/test_pipeline.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: all tests PASS.

- [ ] **Step 6: Commit and report P4 checkpoint**

Commit: `git commit -m "feat: orchestrate typed analytics pipeline"`.

Report success path, typed failures, empty-result behavior, test count, and unresolved issues.

## P5 — Structured evaluation slice

### Task 11: Add Evaluation contracts and 20 cases

**Files:**
- Modify: `projects/01_insightflow_nl2sql/contracts.py`
- Create: `projects/01_insightflow_nl2sql/evaluation_cases.json`
- Create: `projects/01_insightflow_nl2sql/tests/test_evaluation_v2.py`

- [ ] **Step 1: Add Evaluation models**

Append the approved `EvaluationCase`, `EvaluationRequest`, `EvaluationDimensionResult`, `EvaluationCaseResult`, `EvaluationSummary`, and `EvaluationReport` models. Constrain `expected_outcome` to `success`, `failed`, `unsupported`, or `rejected`.

- [ ] **Step 2: Add exactly 20 cases**

Create:

- eight equivalent GMV-drop phrasings using GMV, 交易额, 销售额, 下降, 下滑, 减少, and 回落;
- four ambiguous phrasings missing metric, district, time, or analytical direction;
- four unsupported questions for funnel, cohort, Shanghai order trend, and marketing ROI;
- four adversarial requests for delete, update, remote database attachment, and nonexistent profit.

Every JSON object must include `case_id`, `question`, `expected_intent`, `required_plan_step_ids`, and `expected_outcome`.

- [ ] **Step 3: Test case loading**

Assert exactly 20 unique IDs, each case validates through `EvaluationCase`, and all four categories are present by ID prefix.

Run: `pytest tests/test_evaluation_v2.py::test_loads_twenty_typed_cases -q`

Expected: PASS.

Commit: `git commit -m "test: add Text2Analytics evaluation cases"`.

### Task 12: Generate JSON and Markdown evaluation reports

**Files:**
- Create: `projects/01_insightflow_nl2sql/evaluation.py`
- Modify: `projects/01_insightflow_nl2sql/tests/test_evaluation_v2.py`

- [ ] **Step 1: Write failing six-dimension report tests**

Assert each `EvaluationCaseResult` contains exactly:

```python
{
    "intent_correctness",
    "plan_coverage",
    "sql_groundedness",
    "sql_executability",
    "insight_groundedness",
    "uncertainty_clarity",
}
```

Assert every dimension has `passed`, `score`, and non-empty `details`. Assert `write_json_report` produces valid JSON and `write_markdown_summary` includes totals, per-dimension pass rates, and failed-case reasons.

- [ ] **Step 2: Implement deterministic evaluators**

Implement one focused function per dimension. For expected negative outcomes, mark downstream dimensions passed only when the pipeline stopped at the expected boundary, and explain that decision in `details`. For successful cases:

- intent fields must equal expected fields;
- required plan IDs must be a subset of actual IDs;
- every generated query must pass independent validation;
- every query result must be non-empty;
- every Interpretation fact ID must exist;
- Limitations must mention causal uncertainty and unavailable data.

Implement `run_evaluation(request: EvaluationRequest) -> EvaluationReport` and the two output writers.

- [ ] **Step 3: Run P5 tests and the evaluation command**

Run: `pytest tests/test_evaluation_v2.py -q`

Expected: PASS.

Run: `python evaluation.py`

Expected files:

```text
evaluation_results.json
evaluation_summary.md
```

Both must contain 20 cases or their aggregate summary.

Run: `pytest -q`

Expected: all tests PASS.

- [ ] **Step 4: Commit and report P5 checkpoint**

Stage `contracts.py`, `evaluation.py`, `evaluation_cases.json`, tests, and the two deterministic report artifacts. Commit:

```bash
git commit -m "feat: evaluate evidence-based analytics pipeline"
```

Report per-dimension pass rates, failing cases with reasons, test count, and unresolved quality gaps.

## P6 — Streamlit and research portfolio slice

### Task 13: Make Streamlit a presentation-only consumer

**Files:**
- Modify: `projects/01_insightflow_nl2sql/app.py`
- Modify: `projects/01_insightflow_nl2sql/tests/test_app_smoke.py`

- [ ] **Step 1: Replace the legacy app smoke test**

Test a thin wrapper `run_analysis_workflow(query: str) -> AnalyticsResponse` that only calls `run_analytics(AnalyticsRequest(question=query))`. Add a source-boundary assertion that `app.py` contains no imports from legacy `analytics`, `parser`, or `sql_generator` and no change-rate formula.

- [ ] **Step 2: Implement presentation sections**

Keep `run_analysis_workflow` for testability and render:

1. Question Input.
2. Intent Understanding.
3. Analysis Plan.
4. SQL Queries.
5. Query Results.
6. Facts.
7. Interpretations.
8. Limitations.
9. Confidence score and factor list.

For failed responses, render `status`, `failed_stage`, and `message`; do not attempt to dereference missing Insight.

- [ ] **Step 3: Run app tests and smoke launch**

Run: `pytest tests/test_app_smoke.py tests/test_pipeline.py -q`

Expected: PASS.

Run: `streamlit run app.py --server.headless true`

Expected: server starts without import errors; stop it after the health check.

Commit: `git commit -m "feat: present Text2Analytics golden path"`.

### Task 14: Rewrite README as a research portfolio artifact

**Files:**
- Modify: `projects/01_insightflow_nl2sql/README.md`

- [ ] **Step 1: Add a documentation structure test**

Create or extend `tests/test_app_smoke.py` to assert README contains these headings or exact phrases:

```text
Why Text2SQL Is Not Enough
Type-safe Analytics Pipeline
Schema Grounding and SQL Guardrails
Fact / Interpretation / Limitation
Evidence Completeness
Evaluation Framework
Research Relevance
Reproducibility
```

- [ ] **Step 2: Rewrite the README**

Title it `Text2Analytics: An Evidence-based Analytics System for Decision Support`. Include the golden question, architecture, exact dataset window, successful evidence output, guardrail examples, evaluation table sourced from `evaluation_summary.md`, limitations, run commands, test commands, and relevance to human-centered AI, explainable analytics, decision support, and human-AI collaboration.

State explicitly that confidence measures evidence completeness, not truth probability, and that the first phase is deterministic and does not use an LLM.

- [ ] **Step 3: Run P6 and full verification**

Run: `pytest tests/test_app_smoke.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: all tests PASS.

Run: `python evaluation.py`

Expected: JSON and Markdown reports regenerate deterministically.

- [ ] **Step 4: Commit and report P6 checkpoint**

Commit: `git commit -m "docs: package Text2Analytics research portfolio"`.

Report changed files, final runnable demo, full pytest result, Evaluation pass rates, Streamlit smoke result, and remaining first-phase limitations.

## Final completion check

- [ ] Run `git status --short` and confirm the only remaining untracked files are the pre-existing Schema Profiler files unless they were separately approved.
- [ ] Run `git log --oneline --decorate -12` and confirm P1–P6 commits are individually reviewable.
- [ ] Confirm no source or dependency contains `langgraph`, `crewai`, `autogen`, or an LLM SDK.
- [ ] Confirm `pipeline.py` contains orchestration only and `app.py` contains presentation only.
- [ ] Confirm the golden question is reproducible from a fresh project install.
