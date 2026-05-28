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

| 编号 | 项目 | 主题 | 价值 |
|---|---|---|---|
| 01 | InsightFlow | 智能问数与自动诊断 | 展示 AI workflow、NL2SQL 和数据分析 |
| 02 | Prompt Eval Benchmark | Prompt 调优评测 | 展示 Prompt 版本管理和评测体系 |
| 03 | AI Data Product PRD | 产品方案设计 | 展示产品思维、风险边界和效果评估 |

## 当前阶段

先完成 01 项目，保证能运行、能测试、能展示、能写进简历。

第一阶段只创建基础架构和文档：

1. 根目录 README
2. Codex 工作规则
3. 项目规划文档
4. TDD 测试指南
5. 工作流技能说明
6. 子角色审查说明
7. Review Checklist
8. 01 项目占位目录

## 后续迭代顺序

### 第二阶段：实现 InsightFlow 核心能力

按 TDD 顺序实现：

1. `parser.py`：中文问题解析
2. `sql_generator.py`：根据结构化 intent 生成 SQL
3. `analytics.py`：读取 mock 数据并计算环比变化
4. `evaluator.py`：做基础评测
5. `app.py`：Streamlit 页面整合

### 第三阶段：实现 Prompt Eval Benchmark

重点展示：

1. Prompt V1、V2、V3 的设计差异
2. benchmark queries 的构造方式
3. 解析准确率、任务准确率和整体准确率
4. 如何根据评测结果迭代 Prompt

### 第四阶段：补齐 AI Product Case Study

重点展示：

1. PRD 写作能力
2. AI workflow 产品设计
3. 能力边界和风险控制
4. 评测方案和人工审核机制

## GitHub 展示目标

这个仓库希望具备以下特征：

1. 首屏 README 能快速说明项目价值。
2. 每个子项目都有明确业务场景和项目价值说明。
3. 代码简单但可运行，适合面试官快速理解。
4. 文档表达接近真实 AI 数据产品工作场景。
5. 每轮开发都有测试，体现产品经理对质量和评测的重视。
