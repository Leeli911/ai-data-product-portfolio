from pathlib import Path

import pytest

from text2analytics_engine.intent.parser import parse_intent


PROJECT_DIR = Path(__file__).resolve().parents[1]
SPEC_PATH = PROJECT_DIR / "docs" / "business_question_specification_v1.md"


EXPECTED_GOLDEN_INTENTS = {
    "EN-01": {
        "task_type": "change_explanation",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "EN-02": {
        "task_type": "change_explanation",
        "metric": "metric_revenue",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "EN-03": {
        "task_type": "change_explanation",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "EN-04": {
        "task_type": "change_explanation",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "EN-05": {
        "task_type": "dimension_comparison",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "unsupported_reason": None,
    },
    "EN-06": {
        "task_type": "dimension_comparison",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "unsupported_reason": None,
    },
    "EN-07": {
        "task_type": "top_n_ranking",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "ranking": "ranking_top_n",
        "ranking_n": 3,
        "unsupported_reason": None,
    },
    "EN-08": {
        "task_type": "top_n_ranking",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "ranking": "ranking_bottom_n",
        "ranking_n": 5,
        "unsupported_reason": None,
    },
    "EN-09": {
        "task_type": "forecasting",
        "metric": "metric_gmv",
        "dimension": None,
        "time_window": None,
        "comparison_window": None,
        "unsupported_reason": "forecasting",
    },
    "EN-10": {
        "task_type": "causal_inference",
        "metric": "metric_gmv",
        "dimension": None,
        "time_window": None,
        "comparison_window": None,
        "unsupported_reason": "causal_inference",
    },
    "ZH-01": {
        "task_type": "change_explanation",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "ZH-02": {
        "task_type": "change_explanation",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "ZH-03": {
        "task_type": "change_explanation",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "ZH-04": {
        "task_type": "change_explanation",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": "comparison_week_over_week",
        "unsupported_reason": None,
    },
    "ZH-05": {
        "task_type": "dimension_comparison",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "unsupported_reason": None,
    },
    "ZH-06": {
        "task_type": "dimension_comparison",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "unsupported_reason": None,
    },
    "ZH-07": {
        "task_type": "top_n_ranking",
        "metric": "metric_gmv",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "ranking": "ranking_top_n",
        "ranking_n": 3,
        "unsupported_reason": None,
    },
    "ZH-08": {
        "task_type": "top_n_ranking",
        "metric": "metric_orders",
        "dimension": "dimension_district",
        "time_window": "time_window_this_week",
        "comparison_window": None,
        "ranking": "ranking_bottom_n",
        "ranking_n": 5,
        "unsupported_reason": None,
    },
    "ZH-09": {
        "task_type": "forecasting",
        "metric": "metric_gmv",
        "dimension": None,
        "time_window": None,
        "comparison_window": None,
        "unsupported_reason": "forecasting",
    },
    "ZH-10": {
        "task_type": "causal_inference",
        "metric": "metric_gmv",
        "dimension": None,
        "time_window": None,
        "comparison_window": None,
        "unsupported_reason": "causal_inference",
    },
}


def _parse_markdown_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _load_golden_questions():
    rows = []
    for line in SPEC_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("| EN-") or line.startswith("| ZH-"):
            question_id, question, expected_classification = (
                _parse_markdown_row(line)
            )
            rows.append(
                {
                    "id": question_id,
                    "question": question,
                    "expected_classification": expected_classification,
                }
            )
    return rows


GOLDEN_QUESTIONS = _load_golden_questions()


def test_spec_exposes_twenty_golden_questions():
    assert len(GOLDEN_QUESTIONS) == 20
    assert {item["id"] for item in GOLDEN_QUESTIONS} == set(
        EXPECTED_GOLDEN_INTENTS
    )


@pytest.mark.parametrize("golden_question", GOLDEN_QUESTIONS)
def test_parser_matches_golden_business_question_spec(golden_question):
    intent = parse_intent(golden_question["question"])
    expected = EXPECTED_GOLDEN_INTENTS[golden_question["id"]]

    assert intent.task_type == expected["task_type"]
    assert intent.metric == expected["metric"]
    assert intent.dimension == expected["dimension"]
    assert intent.time_window == expected["time_window"]
    assert intent.comparison_window == expected["comparison_window"]
    assert intent.unsupported_reason == expected["unsupported_reason"]
    assert intent.is_supported is (expected["unsupported_reason"] is None)

    if "ranking" in expected:
        assert intent.ranking == expected["ranking"]
        assert intent.ranking_n == expected["ranking_n"]


@pytest.mark.parametrize(
    ("question", "task_type", "reason"),
    [
        (
            "What should we do to recover GMV?",
            "recommendation",
            "recommendation",
        ),
        ("What about Haidian?", "follow_up", "follow_up"),
        (
            "Compare GMV with weather and competitor campaigns.",
            "cross_dataset",
            "cross_dataset",
        ),
    ],
)
def test_parser_rejects_non_golden_unsupported_categories(
    question,
    task_type,
    reason,
):
    intent = parse_intent(question)

    assert intent.task_type == task_type
    assert intent.is_supported is False
    assert intent.unsupported_reason == reason


def test_parser_output_does_not_include_downstream_artifacts():
    intent = parse_intent("Why did GMV drop in Chaoyang this week?")

    assert set(intent.model_dump()) == {
        "task_type",
        "is_supported",
        "metric",
        "dimension",
        "time_window",
        "comparison_window",
        "ranking",
        "ranking_n",
        "unsupported_reason",
    }
