# AI Data Product Portfolio

## 项目目标

本仓库是一个 AI 数据产品方向的公开项目集，围绕智能问数、自然语言转 SQL、自动归因分析、Prompt 调优和评测体系设计，展示 AI 如何进入数据分析产品的真实工作流。

这个项目不追求堆叠复杂工程架构，重点展示以下能力：

1. 将业务问题拆解为可执行的数据分析流程。
2. 设计清晰的 AI workflow，而不是只停留在模型调用。
3. 区分自然语言解析、SQL 生成、数据计算和业务诊断的职责边界。
4. 通过 benchmark 和单元测试建立可评估、可迭代的产品闭环。
5. 用产品文档说明用户场景、功能流程、风险边界和版本规划。

## 项目列表

| 项目 | 主题 | 展示能力 |
|---|---|---|
| InsightFlow | 智能问数与自动诊断 | AI workflow、NL2SQL、数据分析、TDD |
| Prompt Eval Benchmark | Prompt 调优评测 | Prompt Engineering、评测体系、Benchmark |
| AI Product Case Study | 产品方案设计 | PRD、AI 产品思维、效果评估 |

## 仓库结构

```text
docs/        项目规划和测试指南
skills/      可复用工作流说明
subagents/   子角色审查说明
hooks/       检查清单
projects/    具体作品集项目
```

## 当前阶段

当前优先完成 `projects/01_insightflow_nl2sql`。

该项目会模拟一个智能数据分析助手，让用户输入中文业务问题后，系统输出：

1. 结构化解析结果
2. 自动生成的 SQL
3. pandas 数据分析结果
4. 业务诊断建议

## TDD 开发方式

后续每轮功能开发都遵循测试驱动开发：

1. 先写单元测试，明确输入和预期输出。
2. 再写最小可运行实现。
3. 执行 `pytest` 验证。
4. 更新 README 和项目说明。

详细测试规范见 [docs/testing_guide.md](/Users/apple/Documents/Codex/2026-05-28/ai-github-github-1000-ai-github/docs/testing_guide.md)。

## 未来运行方式

第二阶段实现 InsightFlow demo 后，运行方式预计为：

```bash
cd projects/01_insightflow_nl2sql
pip install -r requirements.txt
streamlit run app.py
```

单元测试预计为：

```bash
cd projects/01_insightflow_nl2sql
pytest
```

## 项目价值

本项目关注 AI 数据产品从需求理解到效果评估的完整链路：

1. 用规则解析模拟自然语言理解，展示智能问数的基础产品形态。
2. 用 SQL 生成和 pandas 分析连接业务问题与数据计算。
3. 用 Prompt 版本管理和 benchmark 评估不同方案的效果。
4. 用 pytest 建立测试驱动开发流程，保证每轮迭代都有可验证结果。
5. 用 PRD 和评测方案说明 AI 能力边界、人工审核机制和产品演进路径。
