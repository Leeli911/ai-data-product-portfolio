# AI 数据产品作品集面试策略

## 当前作品集状态

当前作品集已经完成 3 个 v1 项目：

1. Project 01 `InsightFlow`：智能问数与自动诊断原型。
2. Project 02 `Prompt Eval Benchmark`：prompt 调优与评测体系。
3. Project 03 `AI Product Case Study`：智能问数与自动归因产品方案。

这三个项目组成一条完整主线：

```text
智能问数 workflow
  -> prompt evaluation
  -> 产品化 PRD、上线门槛和风险防护
```

这个作品集不主打算法复杂度，而是主打 AI 数据产品经理需要的落地能力：能把业务问题拆成 workflow，能定义评测指标，能识别 AI 风险边界，并能写出接近真实内部评审的产品方案。

## 面试时必须讲清楚的内容

### 1. 你不是在做一个聊天 demo

Project 01 的重点不是页面，而是把智能问数拆成可检查的链路：

```text
中文问题
  -> intent parsing
  -> SQL generation
  -> pandas 确定性计算
  -> 业务诊断
  -> parser benchmark
```

面试表达：

```text
我没有让模型直接给结论，而是把理解、取数、计算和诊断拆成独立模块。这样每一步都可以校验，也方便后续替换成真实 LLM。
```

### 2. Project 02 的价值是评测意识

Project 02 不要讲成“我调了三个 prompt”，而要讲成“我设计了一个可复现的 prompt benchmark”。

推荐表达：

```text
我没有把 prompt 调优理解成改几句提示词，而是把它做成一个可复现的 benchmark。V1 是 baseline，V2 加 schema grounding 控制 schema 外输出，V3 加 few-shot 提升复杂中文业务问题的解析稳定性。这个结果不是为了证明 prompt 永远正确，而是为了展示上线前应该如何定义指标、比较版本、发现风险和决定是否进入灰度。
```

注意边界：

1. `V3 = 1.000` 只代表在受控 benchmark 上达到满分。
2. 不能说已经生产可用。
3. 要主动补充下一步会扩展 adversarial query、多业务线、多时间范围和人工评审。

### 3. Project 03 是产品经理能力证明

Project 03 的重点是证明你不是只会写 demo，而是能定义一个 AI 数据产品如何上线。

面试时重点讲：

1. 用户是谁：运营、产品、分析师、管理层。
2. 产品边界：LLM 负责理解和组织，计算、SQL 校验、权限和口径治理走确定性系统。
3. 评测体系：离线 benchmark、线上反馈、人工评审、prompt 版本门槛。
4. 风险防护：hallucination、SQL 误生成、指标口径、权限、结果误读。
5. 上线节奏：MVP、内测、灰度、全量和反馈闭环。

## 总体讲法

```text
这个作品集模拟的是 AI 数据产品经理在智能分析产品中的完整落地链路。Project 01 先做智能问数原型，把自然语言问题拆成 intent、SQL、数据计算和诊断；Project 02 进一步做 prompt evaluation，验证 schema grounding、few-shot 和 hallucination control 对稳定性的影响；Project 03 补齐产品方案能力，说明这个能力如何定义用户边界、上线门槛、灰度策略和风险防护。
```

## 现阶段你需要知道的风险点

1. 不要把当前作品集包装成真实生产系统，它是求职作品集 v1。
2. 不要把规则解析说成真实 LLM 能力，要说是用规则模拟 LLM workflow。
3. 不要过度强调代码复杂度，重点强调产品链路、评测闭环和边界控制。
4. 不要说 AI 可以自动完成归因，只能说可以辅助生成基于数据证据的诊断摘要。
5. 面试官如果追问生产化，要回答 SQL 校验、权限控制、指标字典、人工审核和线上监控。

## 未来优化方向

### 第一优先级：补一份作品集总览截图或导览

目标是让面试官 30 秒看懂仓库结构。

建议新增：

1. 根 README 的项目流程图。
2. Project 01、02、03 的一页式总览图。
3. 一个 `docs/demo_walkthrough.md`，按面试演示顺序串起三个项目。

### 第二优先级：扩展 Project 02 的评测可信度

建议新增：

1. adversarial queries：诱导模型生成不存在字段、越权查询或错误口径。
2. error analysis：列出 V1/V2/V3 典型失败样本。
3. prompt release gate：明确什么指标达标才能进入灰度。
4. 更多时间范围和多指标问题：比如最近 30 天、环比、同比、多地区对比。

### 第三优先级：让 Project 03 更像真实评审材料

建议新增：

1. `metrics_dictionary.md`：指标字典和口径样例。
2. `sample_review_cases.md`：人工评审样例，包括通过、澄清、拒答、转人工。
3. `launch_checklist.md`：上线前检查清单。

### 第四优先级：做一次轻量真实 LLM 接入

如果后续要增加技术可信度，可以新增一个可选实验：

1. 使用真实 LLM 做 intent parsing。
2. 用 JSON schema 或 structured output 限制输出。
3. 继续复用 Project 02 的 benchmark。
4. 比较规则 baseline 和真实 LLM 的结果。

这个方向不要急着做。当前阶段 Project 03 比接模型更重要，因为目标岗位是 AI 数据产品经理，不是 LLM 应用工程师。

### 第五优先级：准备简历和面试作品集页面

建议把仓库提炼成简历中的 3 条 bullet：

1. 设计并实现智能问数原型，覆盖中文问题解析、NL2SQL、数据计算和业务诊断 workflow。
2. 构建 prompt evaluation benchmark，对比 baseline、schema grounding、few-shot 的解析准确率和 hallucination rate。
3. 撰写 AI 数据产品 PRD、评测方案、灰度计划和 guardrails，定义智能分析能力的上线边界。

## 推荐下一步

下一步不要继续大改 Project 01 和 Project 02。建议先完成三件小事：

1. 手动同步原始工作目录到远端最新 commit。
2. 打开 GitHub 检查根 README 和 Project 03 目录。
3. 准备一版 3 分钟面试讲稿，把三个项目串起来。
