# Text2Analytics Portfolio Page

这是 Text2Analytics 的独立个人作品集项目页，面向 PhD admissions committee、ML / AI research reviewers 和 Tech recruiter。页面使用 React + Vite + Vanilla CSS，不依赖后端、路由系统、状态管理库或 UI 组件库。

## 运行方式

```bash
npm install
npm run dev
```

然后打开 Vite 在终端中输出的本地地址。

## 测试与构建

```bash
npm test
npm run build
```

## 页面内容

- Hero：项目定位、研究问题和技术栈。
- Problem：Text2SQL 的局限与 structured analytics pipeline 的必要性。
- System Demo：Intent、Analysis Plan、SQL Query、Query Result、Validation Gates、Facts、Interpretations、Limitations 和 Structural Completeness Score。
- Architecture：Business Question 到 Confidence 的完整链路。
- Key Contributions：证据拆分、不确定性表达、链路验证和 Schema-grounded SQL。
- Live Demo：自动填入固定问题并滚动到 Demo。

## Deterministic Demo 边界

System Demo 只从 `src/App.jsx` 中的本地常量读取结果。任何非空输入都返回同一份受控结果，不连接 Python、DuckDB、Streamlit、API 或其他后端。

这个交互用于展示可检查的分析链路，不表示页面支持开放域问答或生产级分析。

## 项目价值

页面将 Text2Analytics 从“一个能生成 SQL 的 Demo”重新表达为“一个研究可验证分析链路的受控原型”，强调事实、解释、限制和证据完整度之间的边界。
