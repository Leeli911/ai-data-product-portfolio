# Prompt Eval Benchmark

## 项目背景

Project 01 `InsightFlow` 已经跑通了智能问数 workflow：用户输入中文业务问题后，系统完成 Intent Parsing、SQL 生成、数据分析和业务诊断。

Project 02 关注另一个更接近真实 AI 数据产品落地的问题：如果未来把 Intent Parsing 接入真实 LLM，如何判断 prompt 是否真的变好了？

这个 benchmark 用规则模拟 Prompt V1、V2、V3 的输出差异，通过统一 query 集合和评测指标，展示 Prompt Engineering 不只是改提示词，而是要建立可复现的实验和评估闭环。

## 与 InsightFlow 的关系

InsightFlow 解决的是“智能问数链路怎么跑通”。

Prompt Eval Benchmark 解决的是“这个链路接入 LLM 后，怎么评估解析质量和 hallucination 风险”。

两个项目组合起来，可以形成一条完整的 AI 数据产品思路：

```text
智能问数 workflow
  -> prompt 版本设计
  -> benchmark 评测
  -> hallucination control
  -> prompt 迭代
```

## Prompt V1/V2/V3 如何迭代

| 版本 | 设计思路 | 主要价值 |
|---|---|---|
| V1 | 基础关键词识别 | 建立 baseline，暴露漏识别和幻觉问题 |
| V2 | Schema Grounding | 限定可用字段、地区和任务，降低 schema 外输出 |
| V3 | Few-shot Examples | 用中文业务示例提升复杂 query 的解析稳定性 |

## Schema Grounding 如何降低字段幻觉

智能问数产品中，LLM 很容易生成不存在的字段、地区或任务类型。例如把“优惠券成本”输出成 `coupon`，把“浦东新区”输出成 `PudongNewArea`。

Schema Grounding 的做法是把可用字段和可用地区明确给模型，让模型只能从合法 schema 中选择。这个机制不能保证理解一定正确，但可以显著降低 schema 外输出，减少后续 SQL 生成和数据查询的风险。

## Few-shot 如何提升解析稳定性

Few-shot 的价值在于让模型看到业务问题和结构化输出之间的映射。

例如：

```text
优惠券成本上升是否影响 GMV？
```

这个问题不是简单问 GMV，而是在问优惠券成本对 GMV 的影响。Few-shot 示例可以帮助模型学习这种表达方式，把任务识别为 `impact_analysis`，并把指标识别为 `coupon_cost`。

## 评测指标

| 指标 | 含义 |
|---|---|
| metric_accuracy | 指标识别准确率 |
| district_accuracy | 地区识别准确率 |
| task_accuracy | 任务类型识别准确率 |
| overall_accuracy | metric、district、task 全部正确的比例 |
| hallucination_rate | 输出中任一字段不在合法 schema 内的比例 |

## 如何运行

安装依赖：

```bash
cd projects/02_prompt_eval_benchmark
pip install -r requirements.txt
```

运行评测并生成 `results.csv`：

```bash
python evaluator.py
```

运行测试：

```bash
pytest
```

## 如何解读 results.csv

`results.csv` 由 `evaluator.py` 实际生成，包含 V1、V2、V3 三行结果。

解读时不只看 overall accuracy，还要看 hallucination rate：

1. V1 作为 baseline，可以暴露基础 prompt 在字段覆盖、地区识别和任务判断上的问题。
2. V2 如果 hallucination rate 明显下降，说明 schema grounding 对控制字段幻觉有效。
3. V3 如果 overall accuracy 提升，说明 few-shot 对复杂 query 和同义词识别有帮助。

## 扩展评测材料

除了基础 benchmark，本项目还补充了上线前需要关注的风险样本和发布门槛：

1. `adversarial_queries.csv`：记录权限绕过、敏感字段、危险 SQL、schema hallucination 和因果过度推断等对抗样本。
2. `error_analysis.md`：分析 V1、V2、V3 的典型失败模式，以及为什么 schema 合法不等于语义正确。
3. `release_gate.md`：定义 prompt 版本进入内测或灰度前需要满足的 accuracy、hallucination、SQL validity 和人工评审门槛。

这些材料用于说明：prompt evaluation 不应该只停留在 accuracy 表格，而应该覆盖安全、权限、口径和上线决策。

## 项目价值

我做这个 benchmark，是为了把 Prompt Engineering 从“凭感觉改 prompt”变成“可比较、可复现、可解释的实验”。

在真实 AI 数据产品里，prompt 调优不应该只看几个 demo case 是否回答得顺，而应该有固定 query 集合、稳定指标、版本对比和风险评估。这个项目展示的是这种评测意识：不仅要让 AI 生成结果，也要知道结果是否稳定、是否符合 schema、是否能进入下一步 SQL 和分析链路。
