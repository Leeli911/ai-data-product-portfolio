# Prompt Evaluation Results Summary

## 结果来源

本报告基于 `python evaluator.py` 实际生成的 `results.csv`，不是手写结果。

当前 benchmark 共包含 22 条中文业务 query，覆盖 GMV、订单、用户数、客单价、高峰期订单、优惠券成本，以及 root cause、trend、comparison、impact 四类任务。

## 结果概览

| Prompt Version | Metric Accuracy | District Accuracy | Task Accuracy | Overall Accuracy | Hallucination Rate |
|---|---:|---:|---:|---:|---:|
| V1 | 0.591 | 0.273 | 0.545 | 0.182 | 0.773 |
| V2 | 0.727 | 0.955 | 0.773 | 0.636 | 0.000 |
| V3 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |

## V1、V2、V3 的差异

V1 是基础关键词版本，整体准确率只有 0.182，hallucination rate 达到 0.773。这个结果符合 baseline 的定位：它能处理“GMV”“订单”“朝阳区”这类高频直白表达，但遇到“优惠券成本”“晚高峰订单”“哪个地区”“是否影响”等复杂 query 时，会出现字段漏识别、任务类型不规范、地区输出不在 schema 内等问题。

V2 加入 schema grounding 后，overall accuracy 提升到 0.636，hallucination rate 降到 0。这个变化说明 schema 约束对智能问数非常关键。即使模型还没有完全理解每个复杂问题，只要输出被约束在合法字段、合法地区和合法任务类型内，后续 SQL 生成和数据查询的风险就会明显降低。

V3 在 schema 约束基础上加入 few-shot 风格规则，overall accuracy 达到 1.000。它主要补齐了 V2 仍然薄弱的部分：同义词、复合指标和复杂任务类型。例如，“优惠券成本上升是否影响 GMV”不应该只被理解成 GMV 问题，而应该识别出 `coupon_cost` 和 `impact_analysis`。

## Schema Grounding 如何降低 Hallucination

在 V1 中，模型可能把“优惠券成本”输出成 `coupon`，把“浦东新区”输出成 `PudongNewArea`，把比较类问题输出成 `ranking`。这些输出看起来接近语义，但不属于系统真实 schema。

V2 的 schema grounding 明确限制了可选字段、地区和任务类型。无法识别时，系统会回退到合法默认值，例如 `unknown` district 或 `trend_analysis` task。这样做不一定让答案完全正确，但可以防止后续 SQL 使用不存在的字段或地区。

从产品角度看，hallucination control 的优先级很高。智能问数产品一旦生成不存在的字段，用户很难判断错误来自模型理解、SQL 生成还是数据计算。把输出限制在合法 schema 内，是进入自动取数链路前的必要防线。

## Few-shot 为什么提升复杂 Query 稳定性

Few-shot 的价值不是让模型记住几个例子，而是让模型学习业务问题到结构化 intent 的映射方式。

在当前 benchmark 中，V3 对以下类型更稳定：

1. 同义词：`销售额` 映射到 `gmv`。
2. 复合指标：`晚高峰订单`、`高峰期订单` 映射到 `peak_orders`。
3. 影响分析：`是否影响`、`是否导致`、`是否拉动` 映射到 `impact_analysis`。
4. 比较分析：`哪个地区`、`相比`、`最高`、`最多` 映射到 `comparison_analysis`。

这类表达在真实业务里很常见。如果 prompt 只写字段定义，不给业务示例，模型可能知道有哪些字段，但不知道这些字段在中文问题中如何出现。

## 为什么不能只看 Accuracy

Accuracy 能说明解析是否命中标准答案，但它不是 AI 数据产品唯一重要的指标。

在智能问数场景中，至少还要看：

1. Hallucination rate：是否生成不存在的字段、地区或任务。
2. 稳定性：同类 query 换一种说法后，输出是否一致。
3. 可解释性：错误能否定位到 metric、district 还是 task。
4. 下游风险：错误是否会传导到 SQL、图表和业务诊断。
5. 人工审核成本：高风险 query 是否需要进入人工确认。

例如，一个 prompt 即使 overall accuracy 不低，但 hallucination rate 很高，也不适合直接接入自动 SQL 生成，因为它可能产生无法执行或误导用户的查询。

## 如何指导真实产品迭代

这个 benchmark 可以用于真实智能问数产品的 prompt 迭代。

如果 V1 表现差，说明基础关键词规则或 prompt 指令不足，需要先补字段说明和任务定义。

如果 V2 hallucination rate 下降但 accuracy 仍不高，说明 schema grounding 有效，但模型对中文业务表达理解不足，需要继续补充 few-shot 示例。

如果 V3 在当前 benchmark 上表现较好，下一步不应该直接上线，而是扩展 benchmark：

1. 增加更多业务线和地区。
2. 增加更口语化的 query。
3. 增加多指标、多地区、多时间范围问题。
4. 增加 adversarial query，测试模型是否会生成 schema 外字段。
5. 把高风险 query 接入人工审核灰度。

对 AI 数据产品来说，prompt evaluation 的价值不是证明某个 prompt 永远正确，而是建立一套持续发现问题、定位问题、推动迭代的机制。
