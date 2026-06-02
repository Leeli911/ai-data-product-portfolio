# AI Product Case Study

智能问数与自动归因分析产品设计

## 项目定位

这个 case study 面向本地生活、外卖、零售等高频经营场景，设计一款面向业务团队的数据分析产品。产品目标不是让大模型直接回答所有经营问题，而是把自然语言提问、指标口径、SQL 生成、数据校验、归因分析和人工审核连接成一条可控的智能分析链路。

在真实业务里，运营、产品和管理层经常会问：

```text
为什么北京朝阳区本周 GMV 下滑？
```

这个问题看似简单，实际涉及指标口径、地区筛选、时间范围、取数逻辑、环比计算和原因解释。Project 03 重点展示 AI 数据产品经理如何把这类需求从 demo 推进到可评审、可灰度、可评估的产品方案。

## 与前两个项目的关系

Project 01 `InsightFlow` 跑通了智能问数原型，展示从中文问题到 intent、SQL、数据计算和业务诊断的 workflow。

Project 02 `Prompt Eval Benchmark` 补齐了 prompt 调优和评测体系，展示 schema grounding、few-shot 和 hallucination rate 如何用于判断解析能力是否稳定。

Project 03 在前两个项目基础上补齐产品方案能力，回答三个问题：

1. 这个能力应该先服务哪些用户和场景。
2. 哪些问题可以自动回答，哪些必须降级或人工审核。
3. 如何定义上线门槛、灰度策略和持续评估机制。

## 目录结构

```text
README.md                 项目说明和作品集价值
prd.md                    产品需求文档
evaluation_plan.md        评测方案和上线门槛
rollout_plan.md           MVP、内测、灰度和全量计划
risk_and_guardrails.md    风险边界和防护机制
```

## 展示能力点

1. AI 数据产品场景拆解：从业务问题识别用户、痛点、核心场景和 MVP 范围。
2. 智能分析 workflow 设计：把 LLM 能力放在理解和组织环节，把计算和校验交给确定性系统。
3. 评测体系设计：同时关注 intent accuracy、SQL validity、hallucination rate、answer usefulness 和 latency。
4. 风险边界设计：覆盖 SQL 误生成、指标口径错误、数据权限、结果误读和人工审核。
5. 产品落地节奏：从 MVP 到内测、灰度、全量和多业务线扩展，形成可执行路线图。
