# TDD 测试指南

## 为什么要做 TDD

这个作品集面向 AI 数据产品经理岗位，不只是展示一个能跑的 demo，也要展示对效果评估、质量控制和迭代闭环的理解。

TDD 的价值是：

1. 先定义业务问题的预期结果，再写实现。
2. 避免自然语言解析逻辑越写越乱。
3. 让每次修改都有可验证结果。
4. 面试时可以说明自己不仅会设计 workflow，也知道如何评估 workflow。

## 测试框架

统一使用 `pytest`。

后续项目依赖中需要包含：

```text
pytest
```

## 标准开发流程

每个功能模块按以下顺序开发：

1. 先写测试文件。
2. 在测试中写清楚输入、预期输出和业务含义。
3. 运行测试，确认测试失败。
4. 编写最小实现代码。
5. 再次运行测试，确认测试通过。
6. 更新 README，补充运行方式和项目说明。

## 测试文件命名

测试文件统一放在项目目录下的 `tests/` 目录。

示例：

```text
projects/01_insightflow_nl2sql/tests/test_parser.py
projects/01_insightflow_nl2sql/tests/test_sql_generator.py
projects/01_insightflow_nl2sql/tests/test_analytics.py
projects/01_insightflow_nl2sql/tests/test_evaluator.py
```

## 预期结果写法

每个测试都要回答三个问题：

1. 输入是什么。
2. 预期输出是什么。
3. 这个预期对应什么业务含义。

示例：

```python
def test_parse_chaoyang_gmv_drop_query():
    query = "为什么北京朝阳区本周 GMV 下滑？"

    result = parse_query(query)

    assert result["metric"] == "gmv"
    assert result["city"] == "Beijing"
    assert result["district"] == "Chaoyang"
    assert result["task"] == "root_cause_analysis"
    assert result["time_range"] == "this_week"
```

这个测试的业务含义是：用户提出一个典型的经营分析问题后，系统应该能识别指标、城市、区域、任务类型和时间范围。

## 第一项目测试范围

`projects/01_insightflow_nl2sql` 至少覆盖以下单元测试：

| 测试文件 | 测试对象 | 预期能力 |
|---|---|---|
| `test_parser.py` | `parser.py` | 解析中文业务问题 |
| `test_sql_generator.py` | `sql_generator.py` | 生成逻辑合理的 SQL |
| `test_analytics.py` | `analytics.py` | 计算环比变化和主因 |
| `test_evaluator.py` | `evaluator.py` | 输出评测准确率 |
| `test_app_smoke.py` | 核心流程 | 验证主流程能串起来 |

## Parser 单测预期

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

## SQL 生成单测预期

输入上面的结构化 intent。

预期 SQL 包含：

```text
SELECT
SUM(gmv)
local_life_metrics
city = 'Beijing'
district = 'Chaoyang'
```

SQL 不要求真实连接数据库执行，但必须逻辑合理、字段正确、过滤条件正确。

## Analytics 单测预期

输入：包含两周北京朝阳区数据的 `mock_data.csv`。

预期结果包含：

```python
{
    "this_week_gmv": 0,
    "last_week_gmv": 0,
    "gmv_change_rate": 0,
    "main_driver": "orders",
    "diagnosis": "..."
}
```

实际数值以后由 mock 数据决定。测试中应该使用确定的数据样本，避免随机数导致结果不稳定。

## Evaluator 单测预期

输入：20 条 benchmark queries。

预期输出字段：

```text
prompt_version
metric_accuracy
district_accuracy
task_accuracy
overall_accuracy
```

准确率统一使用 `0` 到 `1` 的小数，方便后续绘图和比较。

## 常用测试命令

第一阶段结构检查：

```bash
find . -maxdepth 4 -type f | sort
```

运行某个项目的全部测试：

```bash
cd projects/01_insightflow_nl2sql
pytest
```

只运行某个模块测试：

```bash
pytest tests/test_parser.py
pytest tests/test_sql_generator.py
pytest tests/test_analytics.py
```

查看更详细的失败信息：

```bash
pytest -vv
```

## 测试失败时如何处理

1. 先看失败的断言，确认是预期错了还是实现错了。
2. 如果业务预期不合理，先改测试并说明原因。
3. 如果实现不符合预期，优先修改实现。
4. 不要删除测试来规避失败。
5. 不要为了单个测试写明显脱离业务语境的硬编码。

## 每轮交付说明模板

每轮完成后，需要说明：

```text
本轮修改：
- 修改了哪些文件

验证方式：
- 执行了什么命令
- 结果是否通过

下一步：
- 建议继续开发哪个模块
```
