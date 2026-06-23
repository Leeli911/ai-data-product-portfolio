# Text2Analytics 个人作品集页设计

## 1. 目标与受众

页面用于个人网站的项目详情页，而不是 Text2Analytics 系统本身的操作台。核心目标是让 PhD admissions committee、ML / AI research reviewers 和 Tech recruiter 在短时间内理解：

1. Text2Analytics 解决的不是单纯 Text2SQL，而是可检查的结构化分析链路。
2. 项目对 Fact、Interpretation、Limitation 和 Confidence 有明确的证据边界。
3. 项目是可复现的确定性研究原型，不宣称生产级或开放域能力。

## 2. 视觉方向

采用已确认的 A 方案 `Editorial Research`：

- 白色和极浅灰为主背景，使用克制的深蓝作为唯一主要强调色。
- 标题使用编辑感衬线字体，正文使用高可读无衬线字体。
- 通过留白、细边框、轻阴影和小型技术标签建立专业层级。
- 不使用大面积渐变、玻璃拟态、重阴影、装饰性图标或复杂动画。
- 页面以桌面阅读为主，同时保证手机端单列阅读与交互。

## 3. 技术选型与交付位置

- 技术栈：React 18 + Vite + CSS Modules 风格的普通 CSS。
- 不引入 Tailwind、组件库、路由库或后端服务。
- 交互数据使用前端内置的确定性模拟响应，不读取本地 DuckDB 或 Python 进程。
- 目标目录：`projects/01_insightflow_nl2sql/portfolio-page/`。
- 保留现有 Streamlit 原型，作品集页作为独立静态前端运行。

## 4. 信息架构

页面为单页长滚动结构，使用轻量顶部导航跳转到主要区域。

### 4.1 Hero

- 项目名：`Text2Analytics`
- 一句话描述：`An Evidence-based Analytics System for Structured Decision Support`
- 技术标签：Python / DuckDB / Pydantic / Streamlit / SQL Guardrails
- 编辑化主标题：`From business questions to inspectable evidence.`
- 一句研究问题，强调 visible、verifiable 和 appropriately uncertain。

### 4.2 Problem

使用左右对比或两张轻量卡片说明：

- Text2SQL 主要解决“如何取数”，但不自动解决意图澄清、分析路径、结果验证和不确定性表达。
- Structured analytics pipeline 将 Intent、Plan、SQL、Execution、Insight 和 Confidence 拆分为可检查的中间状态。

### 4.3 System Demo

这是页面的主视觉焦点，使用白色大卡片包含：

1. `Business Question` 输入框。
2. `Run Analysis` 按钮。
3. 分阶段进度状态，但不使用持续动画。
4. 完整输出：Intent、Analysis Plan、SQL Query、Query Result、Facts、Interpretations、Limitations 和 Confidence Score。

默认页面展示未运行状态。点击 `Run Analysis` 后展示内置的确定性结果：

- Intent：GMV drop reason analysis / Chaoyang / current week vs previous week。
- Plan：验证 GMV 变化、拆解订单量与客单价、检查辅助信号。
- SQL：只读、Schema-grounded 的 DuckDB 查询示例。
- Query Result：GMV `680,309` vs `751,318`，环比 `-9.5%`；同时展示订单量、活跃用户和客单价等关键指标。
- Facts / Interpretations / Limitations：明确分层，Interpretation 不使用因果措辞。
- Confidence Score：`0.90`，标注其含义为 evidence completeness，而不是结论为真的概率。

### 4.4 Architecture

用紧凑横向流程展示：

`Business Question → Intent → Plan → SQL → Execution → Insight → Confidence`

手机端改为纵向或可换行流程，不使用必须横向滚动才能理解的图。

### 4.5 Key Contributions

四个等权卡片：

- Evidence decomposition
- Uncertainty representation
- Pipeline-level verification
- Schema grounded SQL execution

每张卡片包含一句具体解释，不只展示标题。

### 4.6 Live Demo

设置独立 CTA 区域和 `Try Demo Question` 按钮。点击后：

1. 将 `Why did GMV drop in Chaoyang this week?` 填入 Business Question。
2. 平滑滚动到 System Demo。
3. 不自动运行，保留用户点击 `Run Analysis` 的明确操作。

### 4.7 Footer

明确展示：

- Controlled deterministic system
- Not a production system
- Research prototype for human-centered AI

## 5. React 组件边界

- `App`：持有 demo 输入和运行状态，组织页面区块。
- `Header`：项目标识和锚点导航。
- `HeroSection`：项目定位和技术标签。
- `ProblemSection`：Text2SQL 限制与 structured pipeline 的对比。
- `DemoSection`：输入、运行按钮、运行状态和输出容器。
- `PipelineTrace`：Intent、Plan、SQL 和 Query Result。
- `EvidencePanel`：Facts、Interpretations、Limitations 和 Confidence。
- `ArchitectureSection`：流程节点。
- `ContributionsSection`：四项关键贡献。
- `LiveDemoSection`：填入示例问题并返回 Demo。
- `Footer`：研究原型声明。

组件只通过小型 props 通信。模拟结果单独放在 `src/data/demoResult.js`，避免将数据内容散落在 JSX 中。

## 6. 交互与状态

`App` 保留三个状态：

- `question`：当前输入。
- `status`：`idle | running | success | empty`。
- `hasRun`：控制结果区是否展开。

点击 `Run Analysis` 时：

1. 如果输入为空，进入 `empty` 状态，在输入框下方显示简短说明。
2. 否则进入短暂 `running` 状态，按钮文案变为 `Analyzing…`。
3. 约 450 ms 后进入 `success`，展示结果。这个短延迟只用于交互反馈，不用于模拟复杂 Agent 运行。
4. 任何非空输入都会展示同一受控案例结果，结果顶部明确标记 `Controlled demonstration`，避免暗示页面支持开放问题分析。

## 7. 响应式与可访问性

- 桌面端内容最大宽度约 `1180px`，正文行长保持在易读范围。
- `900px` 以下将 Demo 两列布局改为单列。
- `720px` 以下隐藏桌面锚点导航，Hero、Problem 和 Contributions 均改为单列。
- 所有按钮和输入使用可见 focus 样式；文字与背景保持足够对比度。
- 使用语义化 `header`、`main`、`section`、`form`、`table` 和 `footer`。
- 尊重 `prefers-reduced-motion`，只保留必要的滚动与透明度过渡。

## 8. 验证方案

### 8.1 自动化测试

使用 Vitest + React Testing Library 覆盖：

1. Hero 的项目名、标语和全部技术标签。
2. Problem、Architecture、Contributions 和 Footer 必须内容。
3. 空问题不运行并显示提示。
4. `Try Demo Question` 正确填入指定英文问题。
5. `Run Analysis` 后展示八类要求输出和 `0.90` Confidence Score。

### 8.2 构建与视觉验证

- 运行 `npm run build`。
- 在本地 Vite 页面验证桌面与手机宽度。
- 手动验证 Demo 问题填入、空输入、运行结果、顶部锚点和键盘 focus。
- 检查浏览器控制台无错误。

## 9. 非目标

- 不连接 Python、DuckDB、Streamlit 或任何远程 API。
- 不支持开放域问题、追问、文件上传或真实 SQL 执行。
- 不添加博客系统、个人网站路由、认证、分享或分析埋点。
- 不为装饰而添加三维、粒子、视差或大量动画。
