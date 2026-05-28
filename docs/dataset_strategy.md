# 数据集策略

## 目标

InsightFlow 需要数据来支撑智能问数、自动诊断和评测演示。现阶段优先使用可控的合成经营数据，保证 demo 稳定、结论清晰、测试可重复。

## 当前数据方案

`projects/01_insightflow_nl2sql/mock_data.csv` 是一个小型周级样例，适合快速展示。

`projects/01_insightflow_nl2sql/data_generator.py` 可以生成更大的日粒度 mock 数据，字段包括：

```text
date, city, district, gmv, orders, users, aov, peak_orders, coupon_cost
```

这个生成器会模拟：

1. 北京朝阳区最近 7 天 GMV 下滑。
2. 北京海淀区订单上涨。
3. 不同区域的订单、用户、客单价和优惠券成本波动。
4. 周末订单波动。

## 为什么先使用合成数据

1. 本地生活和外卖业务的真实公开数据较少。
2. 合成数据可以设计明确的业务变化，方便展示归因分析。
3. 测试结果稳定，不会因为外部数据变化影响 demo。
4. 字段可以贴合 AI 数据产品的展示目标。

## 后续可参考的公开数据方向

真实数据可以作为后续扩展，不建议直接替代当前 mock 数据。

| 数据方向 | 可参考来源 | 适合改造成的 demo 场景 |
|---|---|---|
| 城市出行数据 | NYC TLC Trip Record Data | 城市供需分析、高峰时段分析、区域订单波动 |
| 电商交易数据 | UCI Online Retail | 订单、用户、客单价、复购和商品组合分析 |
| 数据集检索 | Google Dataset Search | 查找更多城市、零售、餐饮、交通类公开数据 |

公开数据通常不能直接对应本地生活字段，需要做字段映射。例如：

1. trip count 可以映射为 orders。
2. fare amount 可以映射为 gmv。
3. pickup zone 可以映射为 district。
4. pickup datetime 可以映射为 date 和 peak_orders。

## 数据使用原则

1. demo 主链路使用合成数据，保证稳定。
2. 公开数据用于扩展案例，不直接影响核心测试。
3. 每次新增数据字段，都要同步更新 parser、analytics、README 和测试。
4. 数据中的业务结论必须能由指标变化支撑。
