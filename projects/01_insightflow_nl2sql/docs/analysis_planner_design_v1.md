# Text2Analytics V2 Analysis Planner Design v1

本文档定义 Module 4：Analysis Planner 的设计边界。

本阶段只设计 Planner，不实现 Python 代码，不生成 SQL，不执行 DuckDB，不做 Validation、Scoring 或 Engine Orchestration。

## 1. Planner Objective

Analysis Planner 的职责是把已经通过 Intent Parser 的 canonical Intent 转换为可审计的 AnalysisPlan。

Planner 不负责：

- 解析自然语言；
- 访问 DuckDB；
- 生成 SQL；
- 判断 SQL 是否安全；
- 生成 Facts、Interpretations、Limitations；
- 计算 Structural Completeness Score。

Planner 只回答：

```text
Given a canonical Intent, what analytical steps are required?
```

## 2. AnalysisPlan Data Structure

建议的 `AnalysisPlan` 结构如下：

| Field | Type | Required | Description |
|---|---|---:|---|
| `plan_id` | string | Yes | Stable plan identifier, derived from task type and version. |
| `task_type` | string | Yes | Canonical task type from Intent, e.g. `change_explanation`. |
| `objective` | string | Yes | Human-readable objective of the plan. |
| `ordered_steps` | list[AnalysisStep] | Yes | Ordered analytical steps that downstream modules execute or inspect. |
| `required_metrics` | list[string] | Yes | Canonical metric IDs required by the plan. |
| `required_dimensions` | list[string] | Yes | Canonical dimension IDs required by the plan. |
| `required_time_windows` | list[string] | Yes | Canonical time-window IDs required by the plan. |
| `expected_outputs` | list[string] | Yes | Output artifact categories expected after execution. |

Example shape:

```text
AnalysisPlan(
  plan_id="plan_change_explanation_v1",
  task_type="change_explanation",
  objective="Explain observed GMV change within a bounded comparison window.",
  ordered_steps=[...],
  required_metrics=["metric_gmv", "metric_orders", "metric_aov"],
  required_dimensions=["dimension_district", "dimension_period"],
  required_time_windows=["time_window_this_week"],
  expected_outputs=[
    "metric_change_summary",
    "decomposition_table",
    "bounded_interpretation_inputs"
  ]
)
```

## 3. Step Model

每个 planner step 是一个可单独检查的分析动作。

| Field | Type | Required | Description |
|---|---|---:|---|
| `step_id` | string | Yes | Stable step identifier. |
| `goal` | string | Yes | Human-readable analytical goal. |
| `required_inputs` | list[string] | Yes | Canonical IDs or prior artifacts required before the step can run. |
| `expected_artifacts` | list[string] | Yes | Artifacts this step should produce for later modules. |
| `validation_requirements` | list[string] | Yes | Conditions that must be checked before or after this step. |

Example shape:

```text
AnalysisStep(
  step_id="verify_metric_change",
  goal="Verify whether the target metric changed between current and comparison windows.",
  required_inputs=[
    "metric_gmv",
    "time_window_this_week",
    "comparison_week_over_week"
  ],
  expected_artifacts=[
    "metric_current_value",
    "metric_previous_value",
    "metric_change_rate"
  ],
  validation_requirements=[
    "metric_id_must_be_known",
    "comparison_window_must_exist",
    "current_and_previous_periods_required"
  ]
)
```

## 4. Plan Execution Rules

Planner 本身不执行步骤，但必须标注下游执行语义。

### 4.1 Required Steps

以下步骤必须执行，缺失时计划无效：

| Task type | Required steps |
|---|---|
| `change_explanation` | `verify_metric_change`, `decompose_metric_change`, `prepare_bounded_interpretation_inputs` |
| `dimension_comparison` | `compute_metric_by_dimension`, `compare_dimension_values` |
| `top_n_ranking` | `compute_metric_by_dimension`, `rank_dimension_values` |

### 4.2 Optional Steps

以下步骤允许在数据或 schema 不支持时跳过，但必须留下 limitation 输入：

| Optional step | Applies to | Skip condition |
|---|---|---|
| `inspect_supporting_signals` | `change_explanation` | Supporting metrics are unavailable in vocabulary or schema. |
| `check_secondary_dimensions` | `dimension_comparison` | Only one dimension is requested or supported. |
| `validate_ranking_ties` | `top_n_ranking` | Ranking output does not contain tied values near cutoff. |

Optional step 被跳过时，Planner 应保留：

```text
skipped_step_id
skip_reason
expected_limitation
```

但第一版可以先把这些内容放入 plan metadata 或 validation output，避免过早扩大 step model。

### 4.3 Termination Rules

以下情况应直接终止，不生成可执行计划：

1. Intent is unsupported.
2. `metric` is missing.
3. Required `dimension` is missing for comparison or ranking.
4. Required `time_window` is missing.
5. `change_explanation` lacks `comparison_window`.
6. Ranking task lacks `ranking` or positive `ranking_n`.
7. Intent uses a canonical ID not present in VocabularyRegistry.
8. Task type is outside Business Question Specification.

Termination output should be a structured planning failure, not a partial analysis plan.

## 5. Plan Validation Rules

Plan validation should be deterministic and vocabulary-aware.

### 5.1 Missing Metric

Condition:

```text
intent.metric is None
```

Handling:

```text
status = failed
error_code = PLAN_MISSING_METRIC
message = "Analysis plan requires a canonical metric ID."
```

No ordered steps should be emitted.

### 5.2 Missing Comparison

Condition:

```text
intent.task_type == "change_explanation"
and intent.comparison_window is None
```

Handling:

```text
status = failed
error_code = PLAN_MISSING_COMPARISON_WINDOW
message = "Change explanation requires a comparison window."
```

No ordered steps should be emitted.

### 5.3 Unknown Dimension

Condition:

```text
intent.dimension is not None
and intent.dimension not in VocabularyRegistry dimensions
```

Handling:

```text
status = failed
error_code = PLAN_UNKNOWN_DIMENSION
message = "Intent references a dimension outside the canonical vocabulary."
```

No ordered steps should be emitted.

### 5.4 Scope-out Question

Condition:

```text
intent.is_supported is False
or intent.task_type not in supported planner task types
```

Handling:

```text
status = failed
error_code = PLAN_SCOPE_UNSUPPORTED
message = "Planner only supports change explanation, dimension comparison, and top N ranking."
```

No ordered steps should be emitted.

### 5.5 Missing Ranking Fields

Condition:

```text
intent.task_type == "top_n_ranking"
and (intent.ranking is None or intent.ranking_n is None or intent.ranking_n <= 0)
```

Handling:

```text
status = failed
error_code = PLAN_MISSING_RANKING_FIELDS
message = "Top N ranking requires ranking direction and a positive N."
```

No ordered steps should be emitted.

## 6. Planner Example: change_explanation

Input Intent:

```text
Intent(
  task_type="change_explanation",
  is_supported=True,
  metric="metric_gmv",
  dimension="dimension_district",
  time_window="time_window_this_week",
  comparison_window="comparison_week_over_week"
)
```

Expected AnalysisPlan:

```text
plan_id="plan_change_explanation_v1"
task_type="change_explanation"
objective="Explain observed GMV change within a bounded comparison window."
required_metrics=[
  "metric_gmv",
  "metric_orders",
  "metric_aov"
]
required_dimensions=[
  "dimension_district",
  "dimension_period"
]
required_time_windows=[
  "time_window_this_week"
]
expected_outputs=[
  "metric_change_summary",
  "metric_decomposition",
  "bounded_interpretation_inputs",
  "limitation_inputs"
]
ordered_steps=[
  {
    step_id="verify_metric_change",
    goal="Verify GMV change between current and comparison windows.",
    required_inputs=[
      "metric_gmv",
      "time_window_this_week",
      "comparison_week_over_week"
    ],
    expected_artifacts=[
      "current_metric_value",
      "previous_metric_value",
      "change_rate"
    ],
    validation_requirements=[
      "metric_id_must_be_known",
      "comparison_window_must_exist",
      "current_and_previous_periods_required"
    ]
  },
  {
    step_id="decompose_metric_change",
    goal="Decompose GMV movement using observable supporting metrics.",
    required_inputs=[
      "metric_gmv",
      "metric_orders",
      "metric_aov"
    ],
    expected_artifacts=[
      "decomposition_metrics",
      "decomposition_change_rates"
    ],
    validation_requirements=[
      "supporting_metrics_must_be_known",
      "decomposition_must_use_observed_metrics"
    ]
  },
  {
    step_id="prepare_bounded_interpretation_inputs",
    goal="Prepare evidence inputs for bounded, non-causal interpretation.",
    required_inputs=[
      "metric_change_summary",
      "metric_decomposition"
    ],
    expected_artifacts=[
      "fact_candidates",
      "interpretation_boundaries",
      "limitation_candidates"
    ],
    validation_requirements=[
      "interpretations_must_bind_to_facts",
      "causal_claims_not_allowed"
    ]
  }
]
```

## 7. Planner Example: dimension_comparison

Input Intent:

```text
Intent(
  task_type="dimension_comparison",
  is_supported=True,
  metric="metric_gmv",
  dimension="dimension_district",
  time_window="time_window_this_week"
)
```

Expected AnalysisPlan:

```text
plan_id="plan_dimension_comparison_v1"
task_type="dimension_comparison"
objective="Compare GMV across district values in the selected time window."
required_metrics=[
  "metric_gmv"
]
required_dimensions=[
  "dimension_district"
]
required_time_windows=[
  "time_window_this_week"
]
expected_outputs=[
  "dimension_metric_table",
  "dimension_comparison_summary",
  "limitation_inputs"
]
ordered_steps=[
  {
    step_id="compute_metric_by_dimension",
    goal="Compute GMV for each district in the selected time window.",
    required_inputs=[
      "metric_gmv",
      "dimension_district",
      "time_window_this_week"
    ],
    expected_artifacts=[
      "dimension_metric_table"
    ],
    validation_requirements=[
      "metric_id_must_be_known",
      "dimension_id_must_be_known",
      "time_window_must_exist"
    ]
  },
  {
    step_id="compare_dimension_values",
    goal="Compare metric values across district rows without causal claims.",
    required_inputs=[
      "dimension_metric_table"
    ],
    expected_artifacts=[
      "dimension_comparison_summary",
      "fact_candidates"
    ],
    validation_requirements=[
      "comparison_must_use_observed_values",
      "comparison_requires_at_least_two_dimension_values"
    ]
  }
]
```

## 8. Planner Example: top_n_ranking

Input Intent:

```text
Intent(
  task_type="top_n_ranking",
  is_supported=True,
  metric="metric_orders",
  dimension="dimension_district",
  time_window="time_window_this_week",
  ranking="ranking_bottom_n",
  ranking_n=5
)
```

Expected AnalysisPlan:

```text
plan_id="plan_top_n_ranking_v1"
task_type="top_n_ranking"
objective="Rank districts by order volume in the selected time window."
required_metrics=[
  "metric_orders"
]
required_dimensions=[
  "dimension_district"
]
required_time_windows=[
  "time_window_this_week"
]
expected_outputs=[
  "ranked_dimension_table",
  "ranking_summary",
  "limitation_inputs"
]
ordered_steps=[
  {
    step_id="compute_metric_by_dimension",
    goal="Compute order volume for each district in the selected time window.",
    required_inputs=[
      "metric_orders",
      "dimension_district",
      "time_window_this_week"
    ],
    expected_artifacts=[
      "dimension_metric_table"
    ],
    validation_requirements=[
      "metric_id_must_be_known",
      "dimension_id_must_be_known",
      "time_window_must_exist"
    ]
  },
  {
    step_id="rank_dimension_values",
    goal="Sort dimension values by the selected metric and return bottom 5.",
    required_inputs=[
      "dimension_metric_table",
      "ranking_bottom_n",
      "ranking_n=5"
    ],
    expected_artifacts=[
      "ranked_dimension_table",
      "ranking_summary"
    ],
    validation_requirements=[
      "ranking_direction_must_be_known",
      "ranking_n_must_be_positive",
      "ranking_requires_metric_and_dimension"
    ]
  }
]
```

## 9. Module 4 Implementation Boundary

When implementation starts, Module 4 should create only Planner-specific runtime and tests.

Allowed implementation files:

```text
text2analytics_engine/planning/__init__.py
text2analytics_engine/planning/planner.py
text2analytics_engine/planning/templates.py
tests/test_analysis_planner_v2.py
```

Do not implement SQL, DuckDB, Validation Gates, Scoring, or Engine orchestration in Module 4.
