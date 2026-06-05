# Prompt Evaluation Error Analysis

## 分析目标

本文件用于说明 Prompt V1、V2、V3 的典型失败模式。它不是为了证明某个版本绝对正确，而是为了展示 AI 数据产品在上线前应该如何定位错误、判断风险，并把失败样本沉淀进下一轮 benchmark。

## V1 典型问题

V1 是基础关键词 baseline，主要问题是没有 schema 约束，也没有复杂中文业务表达示例。

典型失败：

| Query 类型 | 可能输出 | 问题 |
|---|---|---|
| 优惠券成本上升是否影响 GMV | `coupon` | 输出不存在字段，属于 schema hallucination |
| 浦东新区 GMV 表现如何 | `PudongNewArea` | 地区值不在合法枚举中 |
| 哪个地区客单价下降最多 | `ranking` | 任务类型不符合系统定义 |
| 晚高峰订单趋势如何 | `peak` | 复合指标识别不完整 |

产品风险：

1. schema 外字段会传导到 SQL，导致查询失败或误查。
2. 非法任务类型会影响后续分析 workflow。
3. 用户很难判断错误来自模型理解、SQL 生成还是数据计算。

## V2 改进与残留问题

V2 加入 schema grounding，把指标、地区和任务类型限制在合法集合内。

改进：

1. hallucination rate 降到 0。
2. 未识别地区回退到 `unknown`，避免编造地区。
3. 输出更适合进入 SQL 生成前的校验流程。

残留问题：

1. 对“是否影响”“是否导致”这类影响分析问题仍可能识别成 root cause。
2. 对多意图、多指标问题的理解还不稳定。
3. schema 合法不等于语义正确，仍需要看 accuracy 和人工评审。

## V3 改进与边界

V3 在 schema grounding 基础上加入 few-shot 示例，提升同义词、复合指标和任务类型判断。

改进：

1. `销售额` 可以映射到 `gmv`。
2. `晚高峰订单` 可以映射到 `peak_orders`。
3. `是否影响` 可以映射到 `impact_analysis`。
4. `哪个地区` 可以映射到 `comparison_analysis`。

必须说明的边界：

1. 当前 V3 满分只代表受控 benchmark 表现。
2. 样本量仍然有限，不能代表生产环境所有表达。
3. 还需要 adversarial query、真实用户问题、线上反馈和人工评审。
4. 如果新增指标或业务线，需要重新评测，不应该复用旧结论。

## 高风险失败样本类型

后续 benchmark 应持续加入以下样本：

1. schema hallucination：诱导模型生成不存在字段。
2. permission bypass：诱导模型查询无权限城市、商户或用户数据。
3. unsafe SQL：诱导模型删除、更新或全表扫描。
4. causal overclaim：诱导模型把相关变化说成确定因果。
5. no evidence request：要求模型在没有数据时直接给结论。
6. sensitive field request：要求返回手机号、地址等敏感明细。

## 如何使用失败样本

每个失败样本都要记录：

1. 原始 query。
2. prompt 版本。
3. 模型输出。
4. 失败类型。
5. 下游风险。
6. 修复方式。
7. 是否进入 release gate。

这样做的价值是让 prompt 迭代从“凭感觉修改”变成“基于失败样本和风险等级修复”。
