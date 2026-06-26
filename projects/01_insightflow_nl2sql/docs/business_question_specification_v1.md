# Text2Analytics V2 Business Question Specification v1

本文档定义 Text2Analytics V2 Engine 第一阶段支持的 Business Question Scope。

本规范不是 Intent Parser 实现，不包含 SQL、Planner、DuckDB 或 Engine 编排逻辑。后续 Intent Parser 测试应优先引用本文档中的 canonical patterns 与 golden test questions。

## 1. Scope Boundary

V2 Engine 当前只支持结构化、可落到本地分析数据表的问题。问题必须能够被拆成：

```text
Metric + Time Window + Optional Dimension/Filter + Optional Comparison/Aggregation
```

当前阶段允许规则驱动解析，不承诺开放域自然语言理解能力。

## 1.1 Canonical Vocabulary Dependency

本文档定义 Business Question 的问题范围和语法结构；`analytics_vocabulary_v1.md` 定义这些语法元素可使用的 canonical IDs。

二者关系如下：

```text
Business Question Specification
-> defines supported task patterns and grammar slots

Analytics Vocabulary
-> defines canonical IDs that can fill those slots
```

后续 Intent Parser 必须先识别 Business Question 是否属于本文档支持范围，再把 metric、dimension、time window、comparison、ranking 和 aggregation 等字段归一化为 Vocabulary 中定义的 canonical IDs。

Parser 输出不得使用自由字符串作为系统决策字段。例如：

| User phrase | Incorrect internal value | Correct canonical ID |
|---|---|---|
| GMV | GMV | metric_gmv |
| Revenue | Revenue | metric_revenue |
| district | district | dimension_district |
| this week | this_week | time_window_this_week |
| top 3 | top | ranking_top_n |

如果某个用户表达不在 Vocabulary 中，Parser 应返回 ambiguity 或 unsupported，而不是临时创造新的 canonical ID。

## 2. Supported Question Types

### 2.1 Why did metric change?

用于解释一个指标在两个时间窗口之间的变化，并输出受观测指标约束的事实、解释和限制。

| Field | Definition |
|---|---|
| Pattern | Why did `<metric>` change/drop/increase in `<dimension or filter>` during `<time_window>`? |
| Example | Why did GMV drop in Chaoyang this week? |
| Required entities | Metric, Time Window, Comparison Window |
| Optional entities | Dimension, Filters |
| Expected output | Intent, Analysis Plan, bounded metric decomposition, validation summary, facts, interpretations, limitations, structural completeness metadata |

第一阶段主要黄金路径是 GMV drop analysis。解释必须保持 bounded inference space：只能说明观测指标之间的关系，不能输出因果结论。

### 2.2 Compare metric across dimensions

用于比较一个指标在不同维度值之间的表现。

| Field | Definition |
|---|---|
| Pattern | Compare `<metric>` across `<dimension>` during `<time_window>`. |
| Example | Compare GMV across districts this week. |
| Required entities | Metric, Dimension, Time Window |
| Optional entities | Filters, Aggregation |
| Expected output | Intent, Analysis Plan, dimension-level metric table, validation summary, facts, interpretations, limitations, structural completeness metadata |

当前阶段只支持描述性比较，不支持自动判断业务原因。

### 2.3 Top N ranking

用于按指标排序，返回 Top N 或 Bottom N 的维度值。

| Field | Definition |
|---|---|
| Pattern | Show top/bottom `<N>` `<dimension>` by `<metric>` during `<time_window>`. |
| Example | Show top 3 districts by GMV this week. |
| Required entities | Metric, Dimension, Time Window, Ranking Direction, N |
| Optional entities | Filters, Aggregation |
| Expected output | Intent, Analysis Plan, ranked result table, validation summary, facts, interpretations, limitations, structural completeness metadata |

当前阶段只支持基于已有数据的排序，不支持推荐、优化建议或行动方案生成。

## 3. Unsupported Question Types

### 3.1 Forecasting

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Predict future metric values | What will GMV be next week? | 当前 Engine 是描述性和对比分析原型，不包含预测模型、时间序列建模或未来外部变量。 |

### 3.2 Open-domain QA

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Ask general knowledge or business theory questions | What is the best strategy for local services growth? | 当前 Engine 只回答可落到本地 schema 和观测数据的问题，不连接开放域知识库。 |

### 3.3 Causal inference

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Ask for root cause, proof, or causal effect | Did coupon cuts cause the GMV drop? | 当前数据和方法只能支持相关性与指标拆解，不能证明因果关系。 |

### 3.4 Recommendation

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Ask for decisions or prescriptions | What should we do to recover GMV? | 当前 Engine 不生成业务行动建议；它只输出事实、受限解释和数据限制。 |

### 3.5 Conversational follow-up

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Rely on previous context | What about Haidian? | 当前阶段无多轮上下文状态，不解析省略指代或前文继承。 |

### 3.6 Cross-dataset or unknown schema analysis

| Unsupported pattern | Example | Rejection reason |
|---|---|---|
| Refer to unavailable data | Compare GMV with weather and competitor campaigns. | 当前 Engine 只能访问本地受控 schema；缺失表和字段必须显式拒绝。 |

## 4. Canonical Business Question Grammar

Canonical question representation:

```text
BusinessQuestion :=
  TaskType
  + Metric
  + TimeWindow
  + Optional[ComparisonWindow]
  + Optional[Dimension]
  + Optional[Filters]
  + Optional[Aggregation]
  + Optional[Ranking]
```

### 4.1 TaskType

| TaskType | Meaning | Supported |
|---|---|---|
| change_explanation | Explain observed metric change between two windows | Yes |
| dimension_comparison | Compare metric across dimension values | Yes |
| top_n_ranking | Rank dimension values by metric | Yes |
| forecasting | Predict future metric values | No |
| causal_inference | Prove or estimate causal effect | No |
| recommendation | Generate action plan | No |
| open_domain_qa | Answer general knowledge question | No |
| follow_up | Resolve question from previous dialogue context | No |

### 4.2 Metric

Metric is the target numerical measure.

Canonical metrics for V2 Phase 1:

| Canonical metric | English aliases | Chinese aliases |
|---|---|---|
| gmv | GMV, revenue, sales | GMV, 交易额, 销售额 |
| orders | orders, order volume | 订单量, 订单数 |
| active_users | active users, users | 活跃用户, 用户数 |
| aov | average order value, AOV | 客单价 |
| peak_orders | peak orders, peak-hour orders | 高峰订单, 高峰期订单 |
| coupon_cost | coupon cost, subsidy cost | 优惠券成本, 补贴成本 |

### 4.3 Dimension

Dimension is the grouping or comparison axis.

Canonical dimensions for V2 Phase 1:

| Canonical dimension | English aliases | Chinese aliases |
|---|---|---|
| district | district, region, area | 区域, 地区, 行政区 |
| city | city | 城市 |
| period | period, time period | 周期, 时间段 |

### 4.4 Time Window

Time Window identifies the current observation period.

Canonical time windows:

| Canonical value | Meaning | Examples |
|---|---|---|
| this_week | Latest 7-day window in the dataset | this week, 本周 |
| last_week | Previous 7-day window before this_week | last week, 上周 |
| latest_7_days | Dataset max date and previous 6 days | latest 7 days, 最近 7 天 |

For deterministic execution, relative time windows must be resolved against the maximum date available in the local dataset, not the machine clock.

### 4.5 Comparison Window

Comparison Window defines the baseline period.

Canonical comparison windows:

| Canonical value | Meaning | Examples |
|---|---|---|
| previous_7_days | The 7 days immediately before the current window | vs previous week, 和上周相比 |
| previous_period | Previous comparable period inferred from Time Window | compared with previous period, 环比 |

If a change-explanation question does not provide or imply a comparison window, the Intent Parser should mark the question ambiguous.

### 4.6 Filters

Filters constrain the data subset.

Canonical filters:

| Filter type | Example | Canonical form |
|---|---|---|
| district filter | in Chaoyang, 朝阳区 | district = Chaoyang |
| city filter | in Beijing, 北京 | city = Beijing |

Filters must map to known schema fields or known dimension values. Unknown filters should be rejected or marked ambiguous.

### 4.7 Aggregation

Aggregation defines how a metric is summarized.

Canonical aggregations:

| Aggregation | Supported metrics | Meaning |
|---|---|---|
| sum | gmv, orders, active_users, peak_orders, coupon_cost | Sum over the selected rows |
| average | aov | Average order value calculated as GMV / orders |
| count | future extension | Count rows or entities |

The Engine should not infer unsupported aggregations without explicit rules.

### 4.8 Ranking

Ranking is only required for Top N questions.

Canonical ranking fields:

| Field | Allowed values |
|---|---|
| direction | top, bottom |
| n | positive integer |
| sort_metric | known metric |
| group_by | known dimension |

## 5. Golden Test Questions

Future Intent Parser tests must import or mirror this list as fixtures. Each question should map to one of the supported task types or a known unsupported category.

### 5.1 English Golden Questions

| ID | Question | Expected classification |
|---|---|---|
| EN-01 | Why did GMV drop in Chaoyang this week? | supported: change_explanation |
| EN-02 | Why did revenue decline in Chaoyang this week? | supported: change_explanation |
| EN-03 | Why did order volume decrease in Chaoyang this week? | supported: change_explanation |
| EN-04 | Explain the GMV change in Chaoyang compared with last week. | supported: change_explanation |
| EN-05 | Compare GMV across districts this week. | supported: dimension_comparison |
| EN-06 | Compare orders across districts this week. | supported: dimension_comparison |
| EN-07 | Show top 3 districts by GMV this week. | supported: top_n_ranking |
| EN-08 | Show bottom 5 districts by order volume this week. | supported: top_n_ranking |
| EN-09 | What will GMV be next week? | unsupported: forecasting |
| EN-10 | Did coupon cuts cause the GMV drop? | unsupported: causal_inference |

### 5.2 Chinese Golden Questions

| ID | Question | Expected classification |
|---|---|---|
| ZH-01 | 为什么朝阳区本周 GMV 下滑？ | supported: change_explanation |
| ZH-02 | 为什么朝阳区本周交易额下降？ | supported: change_explanation |
| ZH-03 | 为什么朝阳区本周订单量减少？ | supported: change_explanation |
| ZH-04 | 分析朝阳区本周 GMV 相比上周的变化。 | supported: change_explanation |
| ZH-05 | 对比本周各区域的 GMV。 | supported: dimension_comparison |
| ZH-06 | 对比本周各行政区的订单量。 | supported: dimension_comparison |
| ZH-07 | 查看本周 GMV 最高的 3 个区域。 | supported: top_n_ranking |
| ZH-08 | 查看本周订单量最低的 5 个区域。 | supported: top_n_ranking |
| ZH-09 | 预测下周 GMV 会是多少？ | unsupported: forecasting |
| ZH-10 | 优惠券减少是否导致了 GMV 下滑？ | unsupported: causal_inference |

## 6. Parser Test Usage

后续 Intent Parser 测试应遵循以下原则：

1. 使用本文档中的 Golden Test Questions 作为第一批 parser fixtures。
2. 每个 supported question 至少验证：
   - `task_type`
   - `metric`
   - `time_window`
   - 必需的 `dimension` 或 `filter`
   - 是否需要 `comparison_window`
3. 每个 unsupported question 至少验证：
   - `task_type` 或 rejection category
   - `is_supported = false`
   - 明确 rejection reason
4. Parser 不应在测试中直接生成 Plan、SQL、Facts 或 Score。
5. 如果新增 supported pattern，必须先更新本文档，再新增 parser tests。

## 7. Version Notes

`business_question_specification_v1.md` 是 V2 Engine 的第一版问题范围规范。

本版本只定义问题边界和 canonical grammar，不定义执行策略。后续模块可以逐步扩展本规范，但不能让 Parser、Planner 或 SQL 生成逻辑隐式扩大支持范围。
