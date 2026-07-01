# Text2Analytics V2 Analytics Vocabulary v1

本文档定义 Text2Analytics V2 Engine 的 Canonical Analytics Vocabulary。

本规范不是 Intent Parser、Planner、SQL 或 Engine 实现。它只定义业务词汇层，作为后续 Parser 输出、Planner 输入和测试断言的共同基准。

## 1. Core Rule

Intent Parser 后续只能输出 Canonical IDs，不输出自由字符串。

正确示例：

```text
metric_gmv
metric_revenue
dimension_district
time_window_this_week
comparison_week_over_week
aggregation_sum
ranking_top_n
```

错误示例：

```text
GMV
Revenue
Chaoyang District
This week
Top 3
```

自由文本可以作为 `raw_text` 或 `source_phrase` 保留，但不能作为 Engine 内部决策字段。

## 2. Metrics

Metric 表示可被聚合、比较或排序的数值指标。

| metric_id | display_name | aliases | definition | aggregation_type | unit |
|---|---|---|---|---|---|
| metric_gmv | GMV | GMV, revenue, sales, 交易额, 销售额 | Gross merchandise value observed in transaction records. | aggregation_sum | CNY |
| metric_revenue | Revenue | revenue, sales, 收入, 营收, 销售额 | Revenue-like business amount. In the current local dataset it maps to GMV unless a separate revenue field is introduced. | aggregation_sum | CNY |
| metric_orders | Orders | orders, order volume, order count, 订单量, 订单数 | Number of completed orders in the selected scope. | aggregation_sum | orders |
| metric_users | Active Users | users, active users, 活跃用户, 用户数 | Number of users with observed transaction activity in the selected scope. | aggregation_sum | users |
| metric_aov | Average Order Value | AOV, average order value, 客单价 | Average monetary value per order, derived as GMV divided by orders. | aggregation_average | CNY/order |
| metric_peak_orders | Peak Orders | peak orders, peak-hour orders, 高峰订单, 高峰期订单 | Number of orders completed during peak business hours. | aggregation_sum | orders |
| metric_coupon_cost | Coupon Cost | coupon cost, subsidy cost, 优惠券成本, 补贴成本 | Observed coupon or subsidy cost in the selected scope. | aggregation_sum | CNY |

### Metric ambiguity notes

- `metric_gmv` and `metric_revenue` are intentionally separate canonical IDs, even if they map to the same local field in the current demo dataset.
- Chinese `销售额` may map to either `metric_gmv` or `metric_revenue`; V2 Phase 1 should prefer `metric_gmv` when the local schema has no separate revenue field.
- `metric_users` means observed active users, not all registered users.

## 3. Dimensions

Dimension 表示过滤、分组、比较或排序的分析轴。

| dimension_id | aliases | supported_filters |
|---|---|---|
| dimension_district | district, region, area, 区域, 地区, 行政区 | Chaoyang, Haidian, 朝阳, 海淀 |
| dimension_region | region, market, business region, 大区, 区域 | North, South, East, West, 华北, 华东, 华南 |
| dimension_store | store, shop, merchant, 门店, 商家 | store_id, store_name |
| dimension_category | category, product category, 品类, 类目 | category_id, category_name |
| dimension_product | product, item, SKU, 商品, 产品 | product_id, product_name |
| dimension_city | city, 城市 | Beijing, Shanghai, 北京, 上海 |
| dimension_period | period, time period, 周期, 时间段 | current, previous, 本期, 上期 |

### Dimension support notes

- V2 Phase 1 local data primarily supports `dimension_district`, `dimension_city`, and `dimension_period`.
- `dimension_store`, `dimension_category`, and `dimension_product` are vocabulary-ready but may be rejected by the Engine until matching schema fields exist.
- Region and district are not interchangeable. Parser should preserve `dimension_region` only when the user explicitly asks for region-level analysis.

## 4. Time Windows

Time Window 表示当前分析期。相对时间必须基于本地数据集最大日期解析，不基于机器当前日期。

| time_window_id | aliases | definition |
|---|---|---|
| time_window_this_week | this week, current week, 本周, 这周 | Latest 7-day window available in the dataset. |
| time_window_last_week | last week, previous week, 上周 | The 7-day window immediately before `time_window_this_week`. |
| time_window_yesterday | yesterday, 昨天 | The latest available date minus one day, if daily data exists. |
| time_window_latest_7_days | latest 7 days, recent 7 days, 最近 7 天 | Dataset max date and previous 6 days. |
| time_window_last_30_days | last 30 days, recent 30 days, 最近 30 天 | Dataset max date and previous 29 days. |
| time_window_this_month | this month, current month, 本月 | Current month-like period inferred from dataset max date. |
| time_window_last_month | last month, previous month, 上月 | Previous month-like period before `time_window_this_month`. |

### Time window support notes

- V2 Phase 1 golden path should rely on `time_window_this_week` and `time_window_latest_7_days`.
- `time_window_yesterday`, `time_window_last_30_days`, `time_window_this_month`, and `time_window_last_month` are vocabulary-ready but may require later execution support.

## 5. Comparison Types

Comparison Type 表示当前期与基准期之间的比较关系。

| comparison_id | aliases | definition |
|---|---|---|
| comparison_week_over_week | WoW, week over week, compared with last week, 环比上周, 周环比 | Compare a current 7-day or week-like window with the immediately previous comparable window. |
| comparison_month_over_month | MoM, month over month, compared with last month, 月环比 | Compare a current month-like window with the previous month-like window. |
| comparison_year_over_year | YoY, year over year, compared with last year, 同比 | Compare a current period with the same period in the previous year. |
| comparison_previous_period | previous period, prior period, 环比, 与上一期相比 | Compare current period with the immediately previous comparable period. |
| comparison_current_vs_previous | current vs previous, 本期对比上期 | Generic current period versus previous period comparison. |

### Comparison support notes

- V2 Phase 1 should normalize “this week vs last week” to `comparison_week_over_week`.
- If a change question lacks an explicit or inferable comparison type, Parser should mark it ambiguous.
- Year-over-year requires historical data coverage and may be rejected until schema/data support exists.

## 6. Ranking Keywords

Ranking Keyword 表示排序方向与 Top/Bottom N 意图。

| ranking_id | aliases | definition |
|---|---|---|
| ranking_top_n | top N, highest, largest, best performing, 最高, 最大, Top N, 前 N | Return the N dimension values with the largest metric values. |
| ranking_bottom_n | bottom N, lowest, smallest, worst performing, 最低, 最小, Bottom N, 后 N | Return the N dimension values with the smallest metric values. |

### Ranking support notes

- Ranking requires a positive integer `n`, a known metric, and a known group-by dimension.
- Ranking does not imply recommendation. “Top 3 districts by GMV” is supported; “which district should we invest in” is unsupported recommendation.

## 7. Aggregation Types

Aggregation Type 表示指标的聚合或派生方式。

| aggregation_id | aliases | definition |
|---|---|---|
| aggregation_sum | sum, total, 总和, 合计 | Add metric values over selected rows. |
| aggregation_count | count, number of, 数量, 计数 | Count rows or entities, only when the target entity is defined. |
| aggregation_average | average, avg, mean, 平均, 均值 | Compute average value or derived average metric. |
| aggregation_ratio | ratio, rate, percentage, 占比, 比率 | Compute a numerator divided by a denominator. |

### Aggregation support notes

- V2 Phase 1 should support `aggregation_sum` for GMV, revenue, orders, users, peak orders, and coupon cost.
- `metric_aov` should use `aggregation_average` as a derived metric.
- `aggregation_count` and `aggregation_ratio` are vocabulary-ready but require explicit schema and calculation rules before execution.

## 8. Golden Question Coverage

The vocabulary covers the current English and Chinese golden questions from `business_question_specification_v1.md`:

| Golden pattern | Vocabulary coverage |
|---|---|
| GMV drop / GMV 下滑 | `metric_gmv`, `comparison_week_over_week`, `time_window_this_week` |
| revenue decline / 交易额下降 | `metric_revenue` or `metric_gmv` by schema policy |
| order volume decrease / 订单量减少 | `metric_orders` |
| compare across districts / 各区域对比 | `dimension_district` |
| top 3 by GMV / GMV 最高的 3 个区域 | `ranking_top_n`, `metric_gmv`, `dimension_district` |
| bottom 5 by orders / 订单量最低的 5 个区域 | `ranking_bottom_n`, `metric_orders`, `dimension_district` |
| forecasting / 预测 | unsupported task type, vocabulary may identify metric and time phrase but Engine must reject forecasting |
| causal inference / 是否导致 | unsupported task type, vocabulary may identify metric but Engine must reject causal inference |

## 9. Expansion Policy

新增 Vocabulary 时必须遵循：

1. 新增 canonical ID 先进入本文档。
2. Intent Parser 只能输出文档中存在的 canonical ID。
3. Planner、SQL 和 Execution 支持范围不得仅因 Vocabulary 存在而自动扩大。
4. Vocabulary-ready 不等于 execution-supported。
5. 如果一个 alias 可映射到多个 canonical ID，必须在本文档中记录 disambiguation rule。

Future likely extensions:

- `metric_refund_rate`
- `metric_conversion_rate`
- `metric_marketing_roi`
- `dimension_channel`
- `dimension_campaign`
- `time_window_custom_date_range`
- `comparison_same_period_last_year`
- `aggregation_distinct_count`

## 10. Version Notes

`analytics_vocabulary_v1.md` 是 Text2Analytics V2 的第一版 canonical vocabulary。

本版本服务于 Intent Parser 之前的语义收敛：先定义可被系统稳定引用的业务词汇，再逐步实现 parser、planner、SQL 和 execution。
