# 作品集面试演示导览

## 演示目标

这份导览用于把 Project 01、Project 02 和 Project 03 串成一次完整的面试展示。目标不是逐个解释文件，而是在 3 到 8 分钟内让面试官理解：

1. 你为什么选择智能问数作为 AI 数据产品场景。
2. 你如何把自然语言问题拆成可验证 workflow。
3. 你如何用 prompt benchmark 和 hallucination 指标评估稳定性。
4. 你如何把 demo 推进到 PRD、灰度、上线门槛和 guardrails。

## 30 秒开场

```text
这个作品集模拟的是 AI 数据产品经理在智能分析产品中的完整落地链路。Project 01 做智能问数原型，把中文业务问题拆成 intent、SQL、数据计算和诊断；Project 02 做 prompt evaluation，用 benchmark 比较 baseline、schema grounding 和 few-shot 的效果；Project 03 做产品方案，定义用户边界、上线门槛、灰度策略和风险防护。
```

## 3 分钟演示路线

### 第一步：先讲总览

打开根 README，指向项目列表。

重点讲：

1. 这不是算法工程作品集，而是 AI 数据产品经理作品集。
2. 三个项目分别证明 workflow、evaluation 和 product design。
3. 核心场景是本地生活、外卖、零售运营里的智能问数和自动归因。

### 第二步：展示 Project 01

打开 `projects/01_insightflow_nl2sql/README.md`。

演示问题：

```text
为什么北京朝阳区本周 GMV 下滑？
```

讲清楚四层链路：

1. Intent Parsing：识别指标、地区、任务和时间。
2. SQL Generation：生成可检查的取数逻辑。
3. pandas Calculation：用确定性代码计算环比和拆解项。
4. Diagnosis：基于数据证据输出诊断摘要。

推荐表达：

```text
我没有让 AI 直接算 GMV 或环比，而是让 AI 负责理解和组织，计算由确定性模块完成。这样每一步都可以被测试和复盘。
```

### 第三步：展示 Project 02

打开 `projects/02_prompt_eval_benchmark/results_summary.md`。

讲清楚 V1、V2、V3：

1. V1 是 baseline，用来暴露漏识别和 hallucination。
2. V2 加 schema grounding，把输出限制在合法字段、地区和任务里。
3. V3 加 few-shot，提升复杂中文业务问题的解析稳定性。

必须主动说明边界：

```text
V3 在当前受控 benchmark 上达到 1.000，不代表生产可用。真实上线前还需要 adversarial query、多业务线、多时间范围和人工评审。
```

### 第四步：展示 Project 03

打开 `projects/03_ai_product_case_study/README.md`。

讲清楚产品化能力：

1. PRD 定义用户、痛点、MVP 和非目标。
2. evaluation plan 定义离线评测、在线反馈、人工评审和上线门槛。
3. rollout plan 定义 MVP、内测、灰度和全量节奏。
4. risk and guardrails 定义 hallucination、SQL、权限、口径和结果误读的防护。

推荐表达：

```text
Project 03 是为了说明这个能力怎么从 demo 进入产品化：哪些问题可以自动回答，哪些问题必须澄清、拒答或人工审核。
```

## 8 分钟深讲路线

如果面试官愿意深入，可以按下面顺序展开：

1. 先讲 Project 01 的模块边界：parser、SQL generator、analytics、evaluator。
2. 再讲 Project 02 的评测指标：overall accuracy 和 hallucination rate 要同时看。
3. 补充 Project 02 的失败样本：baseline 会生成 schema 外字段，说明 prompt 需要约束。
4. 转到 Project 03 的上线门槛：SQL validity 必须是 1.00，hallucination rate 在核心集上必须为 0。
5. 最后讲 guardrails：LLM 不能直接执行 SQL，不能直接计算指标，不能把相关性包装成因果。

## 常见追问回答

### 为什么没有直接接真实 LLM？

```text
我当前阶段先用规则模拟 LLM workflow，是为了先把字段、任务、输出格式、SQL 校验和评测指标定义清楚。真实 LLM 可以替换 intent parsing 模块，但产品边界和评测体系应该先稳定下来。
```

### V3 满分是不是有点过拟合？

```text
是的，所以我在文档里明确写了它只代表受控 benchmark 表现。下一步要扩展 adversarial query、多业务线、多时间范围和线上反馈样本，用持续评测判断是否真的稳定。
```

### 这个项目更偏产品还是工程？

```text
它是 AI 数据产品作品集，不是算法工程作品集。代码用于验证 workflow 可运行，文档用于说明产品设计、评测体系、上线门槛和风险边界。
```

### 如果上线，你最担心什么？

```text
我最担心三个问题：模型生成 schema 外字段、SQL 执行越权或成本失控、用户把相关性误读成因果。因此我会优先做 schema grounding、SQL 校验、权限控制、指标口径卡片和人工审核机制。
```

## 演示时不要说的话

1. 不要说“这个系统已经生产可用”。
2. 不要说“AI 自动完成归因”。
3. 不要说“V3 已经解决 hallucination”。
4. 不要把规则解析包装成真实 LLM 能力。

## 演示结束语

```text
我希望这个作品集展示的是：AI 数据产品经理不只是会写需求或调用模型，而是能把业务问题拆成 workflow，能定义评测指标和上线门槛，也能提前设计风险边界和人工审核机制。
```
