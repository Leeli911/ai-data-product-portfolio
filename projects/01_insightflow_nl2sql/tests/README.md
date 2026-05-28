# InsightFlow 单元测试说明

## 测试目标

本目录用于存放 `projects/01_insightflow_nl2sql` 的单元测试。

后续每个业务模块都必须先写测试，再写实现，确保智能问数 workflow 的关键环节可验证。

## 测试范围

| 测试文件 | 测试对象 | 预期结果 |
|---|---|---|
| `test_parser.py` | 中文问题解析 | 能识别指标、城市、区域、任务和时间 |
| `test_sql_generator.py` | SQL 生成 | SQL 包含正确字段、表名和筛选条件 |
| `test_analytics.py` | 数据分析 | 能计算本周、上周、环比变化和主因 |
| `test_evaluator.py` | 评测逻辑 | 能输出各项准确率 |
| `test_app_smoke.py` | 主流程冒烟测试 | 核心流程能串联运行 |

## Parser 测试预期

输入：

```text
为什么北京朝阳区本周 GMV 下滑？
```

预期：

```python
{
    "metric": "gmv",
    "city": "Beijing",
    "district": "Chaoyang",
    "task": "root_cause_analysis",
    "time_range": "this_week"
}
```

## SQL 生成测试预期

输入：Parser 输出的结构化 intent。

预期 SQL 至少包含：

```text
SELECT
SUM(gmv)
local_life_metrics
city = 'Beijing'
district = 'Chaoyang'
```

## Analytics 测试预期

输入：确定的 mock 数据样本。

预期：

1. 能返回本周 GMV。
2. 能返回上周 GMV。
3. 能返回 GMV 环比变化率。
4. 当订单下降是主要变化时，`main_driver` 应为 `orders`。
5. 诊断文案必须能被数据支持，不能过度推断。

## Evaluator 测试预期

评测结果字段固定为：

```text
prompt_version
metric_accuracy
district_accuracy
task_accuracy
overall_accuracy
```

准确率统一使用 `0` 到 `1` 的小数。

## 执行命令

后续实现测试文件后，在项目目录执行：

```bash
pytest
```

只运行某个测试文件：

```bash
pytest tests/test_parser.py
```

