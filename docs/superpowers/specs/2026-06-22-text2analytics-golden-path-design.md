# Text2Analytics 第一阶段黄金链路设计

## 1. 文档状态

- 日期：2026-06-22
- 状态：设计已逐节确认，等待书面复审
- 适用项目：`projects/01_insightflow_nl2sql`
- 第一阶段目标：完成一条可展示、可解释、可评测的可信分析黄金链路

## 2. 项目定位

第一阶段将现有 InsightFlow 从“自然语言生成 SQL 并输出诊断”的 Demo，升级为 Text2Analytics 的确定性 MVP。系统围绕一个业务问题，依次完成意图识别、分析规划、SQL 生成与安全校验、真实查询执行、证据化洞察、限制说明和置信度评估。

固定黄金问题为：

> 为什么北京朝阳区本周 GMV 下滑？

时间范围沿用当前数据口径：数据集中最大日期及之前 6 天为本周，本周之前连续 7 天为对比期。

第一阶段优先证明系统能够将业务问题转化为可检查、可复现的数据分析过程，而不是扩大问题覆盖范围。

## 3. 范围与非目标

### 3.1 第一阶段范围

1. 识别黄金问题的分析意图、指标、区域、时间范围和歧义。
2. 生成覆盖关键分析路径的结构化计划。
3. 根据计划生成一条或多条只读 SQL。
4. 独立校验 SQL 的语句类型、表和字段。
5. 使用 DuckDB 执行校验通过的 SQL。
6. 输出有来源的事实、基于事实的解释、数据限制和可解释置信度。
7. 使用 Streamlit 展示完整分析链路。
8. 运行 20 个结构化 Evaluation 案例并生成报告。

### 3.2 第一阶段非目标

1. 不接入真实 LLM。
2. 不引入 LangGraph、AutoGen 或其他复杂 Agent 框架。
3. 不实现自主重试、工具选择、长期记忆或多 Agent 协商。
4. 不扩展漏斗分析、Cohort 分析和任意数据集问答。
5. 不建设用户权限、多租户、远程数据库或生产级 API 服务。
6. 不声称从观察数据中识别出业务因果关系。

HTTP 接口 `/api/analytics/ask` 不属于第一阶段验收项。核心流水线通过稳定的 Python 接口暴露，后续可以在不改变领域契约的前提下增加薄 API 层。

## 4. 设计原则

1. 所有模块边界使用简单、明确的 Pydantic Schema；模块之间不传递无约束业务 `dict`。
2. Agent 名称表示职责边界，不表示第一阶段使用大模型或复杂 Agent Runtime。
3. `pipeline.py` 只负责编排、保存阶段输出和失败中止，不包含指标计算或业务判断。
4. `app.py` 只负责 Streamlit 输入与展示，不直接解析问题、计算指标或组织洞察。
5. SQL Validator 独立于 SQL Agent；SQL 必须经过独立校验后才能执行。
6. Insight 明确区分事实、解释和限制；解释必须绑定事实，不使用因果措辞。
7. 每个模块均可通过构造 Pydantic 输入独立测试。
8. 确定性优先：同一数据和问题应产生可复现结果。

## 5. 总体架构

```text
AnalyticsRequest
    ↓
Intent Agent
    ↓ IntentResult
Planner Agent
    ↓ AnalysisPlan
Plan Validator
    ↓ PlanValidationResult
SQL Agent
    ↓ SQLGenerationResult
SQL Validator + SchemaSnapshot
    ↓ SQLValidationResult / ValidatedQuery
DuckDB Executor
    ↓ QueryExecutionResult[]
Insight Agent
    ↓ InsightResult
Confidence Calculator
    ↓ ConfidenceAssessment
Pipeline
    ↓ AnalyticsResponse
Streamlit App
```

推荐的文件职责如下：

| 文件 | 单一职责 |
|---|---|
| `contracts.py` | 定义全部领域输入输出 Schema 和枚举 |
| `intent_agent.py` | 将黄金问题及其等价表达转换为 `IntentResult` |
| `planner_agent.py` | 将意图转换为有序、可检查的分析步骤 |
| `plan_validator.py` | 检查计划是否覆盖黄金链路的必需分析路径 |
| `sql_agent.py` | 根据计划和 Schema Snapshot 生成候选 SQL |
| `sql_validator.py` | 独立检查语句类型、表、字段和多语句风险 |
| `query_executor.py` | 使用 DuckDB 执行 `ValidatedQuery` |
| `insight_agent.py` | 从成功查询结果生成 Fact、Interpretation 和 Limitation |
| `confidence.py` | 根据显式规则生成置信度及加减分依据 |
| `pipeline.py` | 串联模块、收集中间结果、在失败时中止 |
| `evaluation.py` | 执行评测案例并输出结构化报告 |
| `app.py` | 展示问题、计划、SQL、结果、洞察和置信度 |

现有 `schema_catalog.py` 和 Schema Profiler 继续作为 Schema Grounding 的事实来源。Schema Profiler 的现有未提交工作不属于本设计文档提交。

第一阶段技术栈限定为 Python、Pydantic 2、DuckDB、sqlglot、pandas、Streamlit 和 pytest。`sqlglot` 仅用于 SQL AST 解析和白名单校验，不承担 Agent 编排。

## 6. Pydantic 契约

以下字段是第一阶段必须实现的最小契约。枚举字段使用 `Literal` 或简单枚举约束，避免为未来能力预建复杂继承结构。

### 6.1 请求、Schema 和意图

```python
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
    metric: str | None
    metric_label: str | None
    district: str | None
    time_range: str | None
    comparison_period: str | None
    ambiguities: list[str]
```

`SchemaSnapshot` 由 `schema_catalog.py` 和已生成的数据画像转换而来。Agent 和 Validator 读取该快照，不自行猜测数据结构。

### 6.2 分析计划

```python
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
    missing_step_ids: list[str]
    errors: list[str]
```

黄金链路必须包含三个必需步骤：验证 GMV 变化、拆解订单量与客单价、检查辅助信号。

### 6.3 SQL 生成、校验与执行

```python
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
    validated_query: ValidatedQuery | None
    errors: list[str]

class QueryExecutionResult(BaseModel):
    step_id: str
    columns: list[str]
    rows: list[dict[str, str | int | float | bool | None]]
    row_count: int
```

Executor 只接受 `ValidatedQuery`。校验失败的 `GeneratedQuery` 不会进入执行模块。

### 6.4 Insight 与证据关系

```python
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
```

`unit` 用于前端格式化，例如 `CNY`、`orders`、`users`、`percent`；`metric_label` 用于显示中文业务名称。`decomposition` 专门表达 `GMV = order_count × average_order_value` 等指标恒等关系，但不得将恒等关系延伸为未经数据证明的业务因果关系。

### 6.5 置信度、错误和最终响应

```python
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
    intent: IntentResult | None
    plan: AnalysisPlan | None
    generated_queries: list[GeneratedQuery]
    query_results: list[QueryExecutionResult]
    insight: InsightResult | None
    confidence: ConfidenceAssessment | None
    completed_stages: list[str]
    error: PipelineError | None
```

所有公开模块函数均接收一个明确的 Pydantic 模型，并返回一个明确的 Pydantic 模型。数据连接或文件路径作为可注入运行依赖，不替代领域输入输出契约。

逐模块边界如下：

| 模块 | 输入契约 | 输出契约 |
|---|---|---|
| Schema Provider | 无跨模块领域输入；读取本地 Catalog | `SchemaSnapshot` |
| Intent Agent | `AnalyticsRequest` | `IntentResult` |
| Planner Agent | `IntentResult` | `AnalysisPlan` |
| Plan Validator | `AnalysisPlan` | `PlanValidationResult` |
| SQL Agent | `SQLGenerationRequest` | `SQLGenerationResult` |
| SQL Validator | `GeneratedQuery`、`SchemaSnapshot` | `SQLValidationResult` |
| Query Executor | `ValidatedQuery` | `QueryExecutionResult` |
| Insight Agent | `InsightRequest` | `InsightResult` |
| Confidence Calculator | `ConfidenceRequest` | `ConfidenceAssessment` |
| Pipeline | `AnalyticsRequest` | `AnalyticsResponse` |
| Evaluation | `EvaluationRequest` | `EvaluationReport` |
| Streamlit App | `AnalyticsResponse` | 页面展示，无领域输出 |

## 7. 黄金链路设计

### 7.1 Intent

黄金问题的预期意图为：

- `intent_type`: `drop_reason_analysis`
- `metric`: `gmv`
- `metric_label`: `GMV`
- `district`: `Chaoyang`
- `time_range`: `latest_7_days`
- `comparison_period`: `previous_7_days`
- `ambiguities`: 空列表

缺少指标、区域或时间范围时，Intent Agent 必须记录歧义；关键条件不足时流水线中止，不使用默认值掩盖问题。

### 7.2 Plan

黄金计划固定覆盖三条路径：

1. `verify_gmv_change`：比较本周和上周 GMV，确认下滑幅度。
2. `decompose_gmv`：比较订单量、活跃用户数和派生客单价，完成 `GMV = 订单量 × 客单价` 的指标拆解。
3. `check_supporting_signals`：比较高峰期订单和优惠券成本，提供辅助观察信号。

第一阶段允许 Planner 使用确定性规则生成该计划。`plan_validator.py` 验证三个必需 `step_id` 是否存在，不在 `pipeline.py` 中编写这些业务规则。

### 7.3 SQL 与 Result

每个必需步骤生成一条只读查询，并在 `GeneratedQuery.step_id` 中保留来源。查询使用以下现有表：

- `fact_orders`
- `fact_marketing_cost`
- `dim_district`

SQL Validator 至少执行以下独立检查：

1. 只允许单条 `SELECT` 或以 `WITH` 开始并最终返回 `SELECT` 的语句。
2. 拒绝 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER`、`CREATE`、`TRUNCATE`、`COPY`、`ATTACH`、`DETACH`、`INSTALL`、`LOAD`、`CALL` 和多语句输入。
3. 解析所有表和字段引用，并与 `SchemaSnapshot` 对照。
4. 拒绝未知表、未知字段和通配式跨 Schema 访问。
5. 通过 DuckDB `EXPLAIN` 做执行前语义校验；`EXPLAIN` 不替代上述白名单检查。

为避免基于字符串包含关系做脆弱安全判断，第一阶段使用 `sqlglot` 解析 SQL AST。它是独立安全组件，不属于 Agent 框架。

### 7.4 Fact、Interpretation 和 Limitation

黄金链路至少产生以下类别的 Fact：

- 本周与上周 GMV 及环比变化。
- 本周与上周订单量及环比变化。
- 本周与上周客单价及环比变化。
- 可用时，活跃用户、高峰订单和优惠券成本变化。

每条 Fact 必须满足：

1. `source_step_id` 对应一个成功的查询结果。
2. 当前值、对比值和变化率可以从该结果复算。
3. `metric_label` 与 `unit` 足以支持前端独立展示。

每条 Interpretation 必须满足：

1. `supporting_fact_ids` 至少包含一个已存在的 Fact。
2. `reasoning_type` 只能是 `comparison`、`correlation` 或 `decomposition`。
3. 禁止使用“导致”“证明”“必然因为”“根本原因是”等因果措辞。
4. 推荐表述为：“订单量下降与 GMV 下滑方向一致，是当前数据中最显著的关联因素。”
5. 指标拆解可描述各乘数项对结果变化的数学贡献，但不得据此声称发现业务行为原因。

Limitation 至少说明：

- 当前数据支持相关性和指标拆解，不支持因果识别。
- 缺少库存、天气、竞品、营销曝光等外部解释变量。
- 优惠券成本只表示已观测投入，不能独立说明营销效果。

## 8. 失败与中止规则

| 阶段 | 失败条件 | 流水线行为 |
|---|---|---|
| Intent | Schema 校验失败或关键条件缺失 | 立即中止 |
| Planner | 缺少任一必需分析路径 | 立即中止 |
| SQL Agent | 无法为必需步骤生成查询 | 立即中止 |
| SQL Validator | 危险语句、未知表、未知字段或多语句 | 拒绝执行并中止 |
| Executor | 任一必需查询执行失败 | 保留已有阶段结果，不生成 Insight |
| Executor | 必需查询返回空结果 | 返回 `insufficient_evidence`，不生成 Interpretation |
| Insight | Fact 无法绑定结果或 Interpretation 引用未知 Fact | 中止并返回结构化错误 |
| Confidence | 输入不完整 | 不生成分数，返回 `None` |

`pipeline.py` 只调用各模块、按规则判断返回状态、收集中间产物并生成 `PipelineError`。指标计算、必需路径判断、SQL 安全判断、Insight 生成和置信度计算分别留在对应模块中。

## 9. 置信度设计

置信度表示当前结论的证据完整度，不表示结论为真的概率，也不替代离线 Evaluation。

```text
base = 0.50

+0.10 Intent 关键字段完整
+0.10 Plan 覆盖三条必需路径
+0.10 所有 SQL 校验并执行成功
+0.10 当前期和对比期数据完整
+0.10 所有 Interpretation 均绑定 Fact

-0.10 缺少关键支持数据
-0.10 查询结果不足以完成指标拆解
-0.10 存在只能观察相关性的重要限制
```

分数限制在 `0.10` 到 `0.95`。流程失败时 `confidence` 为 `None`。每次加减分都通过 `ConfidenceFactor` 返回名称、影响值和理由，前端同时展示分数及依据。

## 10. Evaluation 设计

### 10.1 测试集

第一阶段包含 20 个确定性案例：

1. 8 个黄金问题的等价表达。
2. 4 个缺少指标、区域或时间条件的模糊问题。
3. 4 个超出第一阶段能力的问题，预期返回 `unsupported`。
4. 4 个包含危险操作或越权字段要求的对抗问题，预期被安全规则拒绝。

### 10.2 评测维度

1. **Intent Correctness**：任务类型、指标、区域、时间范围和歧义标记是否符合期望。
2. **Plan Coverage**：三个必需分析路径是否全部覆盖。
3. **SQL Groundedness**：所有表和字段是否来自 Schema Snapshot，查询是否只读。
4. **SQL Executability**：预期执行的查询能否在 DuckDB 成功执行。
5. **Insight Groundedness**：Fact 是否与结果一致，Interpretation 是否引用有效 Fact，拆解关系是否可复算。
6. **Uncertainty Clarity**：是否明确说明相关性边界、缺失数据和无法判断内容。

无 SQL 是某些负向案例的正确结果，因此报告必须按 `expected_outcome` 判断，而不能把所有未执行 SQL 的案例计为失败。

### 10.3 结构化报告契约

```python
class EvaluationCase(BaseModel):
    case_id: str
    question: str
    expected_intent: IntentResult
    required_plan_step_ids: list[str]
    expected_outcome: str

class EvaluationRequest(BaseModel):
    cases: list[EvaluationCase]

class EvaluationDimensionResult(BaseModel):
    dimension: str
    passed: bool
    score: float
    details: list[str]

class EvaluationCaseResult(BaseModel):
    case_id: str
    dimensions: list[EvaluationDimensionResult]
    passed: bool

class EvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    dimension_pass_rates: dict[str, float]

class EvaluationReport(BaseModel):
    summary: EvaluationSummary
    cases: list[EvaluationCaseResult]
```

Evaluation 同时输出机器可读 JSON 和 README 可引用的 Markdown 摘要。报告保留每个维度的失败原因，而不只输出 `pytest` 是否通过。

## 11. 测试策略

实现阶段遵循 TDD。每个模块至少覆盖以下独立测试：

- Intent Agent：黄金表达、等价表达、模糊输入和超范围输入。
- Planner Agent：完整计划及缺失必需路径的质量校验。
- SQL Agent：每个步骤生成与 `step_id` 对齐的候选 SQL。
- SQL Validator：安全查询、危险语句、多语句、未知表和未知字段。
- Query Executor：成功结果、空结果和执行错误。
- Insight Agent：Fact 复算、Fact 引用、三类 reasoning type、因果禁词和 Limitation。
- Confidence：每个加减分因素、分数边界和失败时不评分。
- Pipeline：完整成功路径及每个阶段的失败中止。
- App：页面能够消费 `AnalyticsResponse`，且不重复领域计算。
- Evaluation：20 个案例生成完整、可序列化的 `EvaluationReport`。

## 12. 第一阶段验收标准

1. 所有模块公开输入输出均由 `contracts.py` 中的 Pydantic Schema 约束。
2. 黄金问题完整展示 Intent、Plan、SQL、Result、Fact、Interpretation、Limitation 和 Confidence。
3. 预期成功案例的三条必需分析路径覆盖率为 100%。
4. 预期执行 SQL 的 Schema Groundedness、安全校验通过率和可执行率均为 100%；负向案例按预期中止阶段单独计分。
5. 所有 Interpretation 均引用有效 Fact，且不包含因果措辞。
6. 所有成功分析均明确展示相关性边界和数据限制。
7. 危险 SQL、未知字段、空结果和执行失败均按设计中止。
8. `pipeline.py` 不包含业务判断，`app.py` 不包含分析逻辑。
9. 每个模块均有独立单元测试，并有完整端到端测试。
10. 20 个 Evaluation 案例能够生成结构化 JSON 报告和 Markdown 摘要。
11. 全量 `pytest` 通过，Streamlit 黄金链路可在本地复现。
12. 实现不包含 LLM、LangGraph 或复杂 Agent 框架。

## 13. Research Portfolio 包装接口

第一阶段的实现产物应直接支持 README 按以下研究型结构包装：

1. **Project Motivation**：解释为什么 Text2SQL 不足以支持可信决策。
2. **Research Question**：自然语言分析系统如何组织证据、解释和不确定性。
3. **System Overview**：展示类型化流水线和独立安全边界。
4. **Golden Use Case**：完整展示从问题到证据化洞察的过程。
5. **Grounding and Guardrails**：说明 Schema Grounding、SQL Validator 和失败中止。
6. **Evidence and Uncertainty**：解释 Fact、Interpretation、Limitation 的分离设计。
7. **Evaluation**：展示 20 个案例、维度指标和典型失败分析。
8. **Limitations**：明确确定性实现、单场景和非因果边界。
9. **Research Relevance**：关联 human-centered AI、explainable analytics、decision support 和 human-AI collaboration。
10. **Reproducibility**：提供数据口径、运行命令、测试命令和评测产物。

该包装依赖的证据均来自第一阶段可运行产物，而不是额外撰写无法验证的项目叙事。

## 14. 后续阶段边界

只有第一阶段通过验收后，才考虑以下扩展：更多分析意图、更多业务数据表、可替换 LLM Provider、HTTP API、真实可视化图表和更大规模 Evaluation。所有扩展继续复用本设计的 Pydantic 契约和模块边界，不反向污染黄金链路。

## 15. 设计自检

| 自检项 | 设计依据 | 结果 |
|---|---|---|
| 第一阶段不接入 LLM、LangGraph 或复杂 Agent 框架 | 第 3、4、5、14 节 | 通过 |
| 所有跨模块领域数据均使用 Pydantic Schema | 第 6 节契约与逐模块边界表 | 通过 |
| 黄金链路完整展示 Intent、Plan、SQL、Result、Fact、Interpretation、Limitation、Confidence | 第 5、7、12 节 | 通过 |
| Interpretation 必须绑定 Fact 且禁止因果措辞 | 第 6.4、7.4、12 节 | 通过 |
| Evaluation 输出结构化报告而非单一测试状态 | 第 10 节 | 通过 |
| 实现产物能够直接支持 Research Portfolio README | 第 13 节 | 通过 |

占位符、未决字段和跨章节矛盾检查已完成。第一阶段范围能够由一份独立实施计划覆盖，无需再拆分子项目。
