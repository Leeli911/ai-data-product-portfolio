# InsightFlow 智能问数与自动诊断

## 项目定位

InsightFlow 是一个面向 AI 数据产品方向的智能问数 demo。

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

## 已实现模块

| 模块 | 文件 | 说明 |
|---|---|---|
| 问题解析 | `parser.py` | 将中文问题解析为结构化 intent |
| SQL 生成 | `sql_generator.py` | 根据 intent 生成 SQL 字符串 |
| 数据分析 | `analytics.py` | 用 pandas 分析 mock 数据 |
| 评测逻辑 | `evaluator.py` | 计算 parser 准确率 |
| 页面展示 | `app.py` | 使用 Streamlit 展示完整流程 |
| 模拟数据 | `mock_data.csv` | 本地生活或外卖业务数据 |
| 扩展数据 | `mock_data_extended.csv` | 由生成器产出的日粒度大样本数据 |
| 数据生成 | `data_generator.py` | 生成多城市、多区域、日粒度经营数据 |
| 评测数据 | `benchmark_queries.csv` | 用于评估 parser 的业务问题集 |

## 数据字段

`mock_data.csv` 使用本地生活业务数据结构：

```text
date, city, district, gmv, orders, users, aov, peak_orders, coupon_cost
```

当前 mock 数据包含北京朝阳区和海淀区两期数据，可体现朝阳区 GMV 环比下滑、海淀区订单上涨等经营变化。

如需生成更多 demo 数据：

```bash
cd projects/01_insightflow_nl2sql
python data_generator.py
```

生成结果会写入：

```text
mock_data_extended.csv
```

## TDD 测试覆盖

当前已覆盖：

1. `tests/test_parser.py`：中文问题解析。
2. `tests/test_sql_generator.py`：SQL 字段、表名和筛选条件。
3. `tests/test_analytics.py`：GMV、订单、环比变化和主因判断。
4. `tests/test_evaluator.py`：parser benchmark 准确率。
5. `tests/test_app_smoke.py`：主流程冒烟测试。

## 运行方式

安装依赖：

```bash
cd projects/01_insightflow_nl2sql
pip install -r requirements.txt
```

运行 Streamlit demo：

```bash
streamlit run app.py
```

运行单元测试：

```bash
cd projects/01_insightflow_nl2sql
pytest
```

## 项目价值

InsightFlow 将中文业务问题拆成语义解析、SQL 生成、数据计算和业务解释四个环节。

这个设计强调两点：

1. AI 负责理解问题、生成结构化意图和组织解释，不直接替代确定性计算。
2. 数据计算由 SQL 或 pandas 完成，并通过单元测试和评测指标保证每个环节可验证、可迭代。
