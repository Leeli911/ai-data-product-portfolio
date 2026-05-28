# Skill: Prompt Evaluation

## 适用场景

当任务涉及 Prompt 调优、效果评估、benchmark、准确率对比时，使用本技能。

## 评测指标

1. Metric Accuracy：指标识别准确率
2. Dimension Accuracy：维度识别准确率
3. Task Accuracy：任务类型识别准确率
4. SQL Validity：SQL 是否逻辑有效
5. Output Format Validity：输出格式是否符合要求
6. Latency：响应耗时

## Prompt 版本设计

至少包含三个版本：

1. V1 基础版：只要求提取指标、地区、时间。
2. V2 Schema 约束版：增加可用字段说明，要求只能从已有字段中选择。
3. V3 Few-shot 示例版：增加 2 到 3 个中文业务问题示例。

## 输出文件

后续实现 Prompt Eval Benchmark 时，至少包含：

1. `benchmark_queries.csv`
2. `prompt_versions.md`
3. `evaluator.py`
4. `results.csv`
5. `tests/test_evaluator.py`

## TDD 要求

评测逻辑必须先写测试，再写实现。

测试重点：

1. benchmark 文件是否能被正确读取。
2. 每条 query 是否能得到模拟解析结果。
3. 准确率计算是否符合预期。
4. 输出字段是否稳定。
5. 准确率统一使用 `0` 到 `1` 的小数。

## 面试表达

可以这样解释：

> Prompt 调优不是只凭感觉改提示词，而是要先构造 benchmark，再定义准确率指标，通过版本对比判断改动是否真的提升了效果。本项目用简化规则模拟模型输出，重点展示评测设计思路。

