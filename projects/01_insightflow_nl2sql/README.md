# InsightFlow 智能问数与自动诊断

## 项目定位

InsightFlow 是一个面向 AI 数据产品经理作品集的智能问数 demo。

它模拟业务同学输入中文经营问题后，系统自动完成：

1. 问题解析
2. SQL 生成
3. 数据分析
4. 业务诊断
5. 基础评测

本项目不接真实大模型 API，先用规则和模板模拟 AI workflow，重点展示产品理解、分析流程和评测思维。

## 目标场景

典型用户问题：

```text
为什么北京朝阳区本周 GMV 下滑？
```

系统预期输出：

1. Parsed Intent：结构化解析结果
2. Generated SQL：自动生成的 SQL
3. Analysis Result：本周、上周和环比变化
4. Business Diagnosis：业务诊断建议

## 后续模块规划

| 模块 | 文件 | 说明 |
|---|---|---|
| 问题解析 | `parser.py` | 将中文问题解析为结构化 intent |
| SQL 生成 | `sql_generator.py` | 根据 intent 生成 SQL 字符串 |
| 数据分析 | `analytics.py` | 用 pandas 分析 mock 数据 |
| 评测逻辑 | `evaluator.py` | 计算解析和输出准确率 |
| 页面展示 | `app.py` | 使用 Streamlit 展示完整流程 |
| 模拟数据 | `mock_data.csv` | 本地生活或外卖业务数据 |

## TDD 开发顺序

后续实现时按以下顺序推进：

1. 写 `tests/test_parser.py`，明确中文问题解析预期。
2. 实现 `parser.py`。
3. 写 `tests/test_sql_generator.py`，明确 SQL 生成预期。
4. 实现 `sql_generator.py`。
5. 写 `tests/test_analytics.py`，明确环比和主因分析预期。
6. 创建 `mock_data.csv` 并实现 `analytics.py`。
7. 写 `tests/test_evaluator.py` 并实现 `evaluator.py`。
8. 最后整合 `app.py`。

## 未来运行方式

第二阶段实现代码后，运行 Streamlit demo：

```bash
cd projects/01_insightflow_nl2sql
pip install -r requirements.txt
streamlit run app.py
```

运行单元测试：

```bash
cd projects/01_insightflow_nl2sql
pytest
```

## 面试讲法

可以这样介绍：

> InsightFlow 是我设计的一个智能问数与自动诊断原型。它把用户的中文业务问题拆成语义解析、SQL 生成、数据计算和业务解释四个环节。这个设计的重点不是炫技，而是展示 AI 数据产品应该如何划分模型能力和确定性计算能力，并通过单元测试和评测指标保证每个环节可验证、可迭代。

