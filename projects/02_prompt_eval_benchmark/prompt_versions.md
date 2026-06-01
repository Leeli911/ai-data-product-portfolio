# Prompt Versions

## Prompt V1：基础版

V1 是 baseline，用最基础的关键词规则模拟 prompt 输出。

设计特点：

1. 只识别常见指标，如 GMV、订单、用户数、客单价。
2. 只识别朝阳区、海淀区等高频地区。
3. 对任务类型的判断依赖简单关键词。

主要问题：

1. 遇到“销售额”“晚高峰订单”“优惠券成本”等同义词或复合指标时容易漏识别。
2. 遇到未知地区时可能生成 schema 外的地区名。
3. 遇到“是否影响”“哪个地区”等复杂任务时容易输出不规范任务类型。

V1 的作用不是追求高分，而是作为 prompt 调优前的 baseline。

## Prompt V2：Schema Grounding 版

V2 在 prompt 中明确可用字段和地区，模拟 schema grounding 的效果。

可用字段：

```text
gmv, orders, users, aov, peak_orders, coupon_cost
```

可用地区：

```text
Chaoyang, Haidian, Fengtai, Pudong, unknown
```

可用任务类型：

```text
root_cause_analysis, trend_analysis, comparison_analysis, impact_analysis
```

设计目标：

1. 让模型只能从已有字段中选择。
2. 未识别地区时回退到 `unknown`。
3. 降低编造字段、编造地区、编造任务类型的风险。

V2 的改进重点是控制 hallucination，但它不保证所有复杂 query 都能理解正确。

## Prompt V3：Few-shot 版

V3 在 V2 的 schema 约束基础上增加 few-shot 示例。

示例 1：

```text
用户问题：为什么北京朝阳区本周 GMV 下滑？
输出：metric=gmv, district=Chaoyang, task=root_cause_analysis
```

示例 2：

```text
用户问题：优惠券成本上升是否影响 GMV？
输出：metric=coupon_cost, district=unknown, task=impact_analysis
```

示例 3：

```text
用户问题：哪个地区客单价下降最多？
输出：metric=aov, district=unknown, task=comparison_analysis
```

设计目标：

1. 提升同义词识别能力。
2. 提升复杂 query 的任务类型判断。
3. 让模型学习中文经营问题到结构化 intent 的稳定映射。

V3 代表更接近真实 AI 数据产品中的 prompt 调优方向：schema 约束负责边界，few-shot 示例负责理解稳定性。
