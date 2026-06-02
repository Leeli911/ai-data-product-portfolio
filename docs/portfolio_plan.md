# AI 数据产品作品集总规划

## 目标

本作品集用于系统化展示 AI 数据产品、数据平台产品和智能分析产品的设计与评估能力。

核心展示能力：

1. 数据分析经验如何升级为 AI 数据产品能力
2. 如何设计智能问数 workflow
3. 如何进行 Prompt 调优
4. 如何设计评测体系
5. 如何用产品文档说明 AI 能力边界
6. 如何用单元测试证明功能稳定可迭代

## 项目列表

| 编号 | 项目 | 状态 | 主题 | 价值 |
|---|---|---|---|---|
| 01 | InsightFlow | Completed v1 | 智能问数与自动诊断 | 展示 AI workflow、NL2SQL 和数据分析 |
| 02 | Prompt Eval Benchmark | Completed v1 | Prompt 调优评测 | 展示 Prompt 版本管理、Schema Grounding、Few-shot 和 hallucination control |
| 03 | AI Product Case Study | Completed v1 | 产品方案设计 | 展示 PRD、评测方案、灰度策略、风险边界和 guardrails |

## 当前阶段

Project 01、Project 02 和 Project 03 已完成 v1。

当前作品集已经覆盖：

1. 智能问数 workflow
2. NL2SQL 原型
3. pandas 数据分析与诊断
4. Prompt 版本设计
5. Prompt benchmark
6. hallucination rate 评估
7. AI 数据产品 PRD
8. 上线门槛、灰度策略和风险防护机制

## 后续迭代顺序

### 第二阶段：实现 InsightFlow 核心能力

状态：Completed v1。

已完成：

1. `parser.py`：中文问题解析
2. `sql_generator.py`：根据结构化 intent 生成 SQL
3. `analytics.py`：读取 mock 数据并计算环比变化
4. `evaluator.py`：做基础评测
5. `app.py`：Streamlit 页面整合

### 第三阶段：实现 Prompt Eval Benchmark

状态：Completed v1。

已完成：

1. Prompt V1、V2、V3 的设计差异
2. benchmark queries 的构造方式
3. metric、district、task、overall accuracy
4. hallucination rate
5. 基于 results.csv 的结果分析报告

### 第四阶段：补齐 AI Product Case Study

状态：Completed v1。

已完成：

1. PRD 写作能力
2. AI workflow 产品设计
3. 能力边界和风险控制
4. 评测方案和人工审核机制
5. MVP、内测、灰度和全量 rollout 计划

## 当前面试主线

这个作品集模拟的是 AI 数据产品经理在智能分析产品中的完整落地链路：

1. Project 01 展示智能问数 workflow 如何从自然语言问题进入 SQL、计算和诊断。
2. Project 02 展示 prompt 调优如何通过 benchmark、schema grounding、few-shot 和 hallucination rate 评估。
3. Project 03 展示产品经理如何定义用户边界、上线门槛、灰度策略、人工审核和风险防护。

## GitHub 展示目标

这个仓库希望具备以下特征：

1. 首屏 README 能快速说明项目价值。
2. 每个子项目都有明确业务场景和项目价值说明。
3. 代码简单但可运行，适合读者快速理解。
4. 文档表达接近真实 AI 数据产品工作场景。
5. 每轮开发都有测试，体现产品经理对质量和评测的重视。
