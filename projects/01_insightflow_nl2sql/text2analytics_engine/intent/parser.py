"""Rule-based Intent Parser backed by canonical vocabulary documents."""

from text2analytics_engine.contracts import Intent
from text2analytics_engine.intent.rules import (
    contains_any,
    extract_ranking_n,
    lookup_comparison,
    lookup_dimension,
    lookup_metric,
    lookup_ranking,
    lookup_time_window,
)


FORECASTING_TERMS = (
    "forecast",
    "predict",
    "will",
    "next week",
    "future",
    "预测",
    "下周",
    "未来",
)
CAUSAL_TERMS = ("cause", "caused", "causal", "导致", "是否导致")
RECOMMENDATION_TERMS = (
    "what should",
    "recommend",
    "suggest",
    "建议",
    "应该怎么",
    "怎么做",
    "如何恢复",
)
FOLLOW_UP_TERMS = ("what about", "how about", "呢", "那")
CROSS_DATASET_TERMS = (
    "weather",
    "competitor",
    "inventory",
    "campaign",
    "天气",
    "竞品",
    "库存",
    "曝光",
)
CHANGE_TERMS = (
    "why",
    "change",
    "drop",
    "decline",
    "decrease",
    "increase",
    "下降",
    "下滑",
    "减少",
    "变化",
)
COMPARE_TERMS = ("compare", "across", "对比", "各")


def _unsupported_intent(question: str, task_type: str) -> Intent:
    """Create an unsupported intent while preserving recognized vocabulary."""
    return Intent(
        task_type=task_type,
        is_supported=False,
        metric=lookup_metric(question),
        dimension=lookup_dimension(question),
        time_window=lookup_time_window(question),
        comparison_window=lookup_comparison(question),
        unsupported_reason=task_type,
    )


def _contains_follow_up(question: str) -> bool:
    """Detect questions that depend on previous conversational context."""
    normalized = question.strip().lower()
    return (
        contains_any(question, FOLLOW_UP_TERMS)
        and len(normalized.split()) <= 4
    )


def _supported_intent(
    task_type: str,
    question: str,
    ranking: str | None = None,
    ranking_n: int | None = None,
) -> Intent:
    """Create a supported canonical intent."""
    normalized_question = question.lower()
    time_window = lookup_time_window(question)
    if (
        task_type == "change_explanation"
        and ("last week" in normalized_question or "上周" in question)
    ):
        time_window = "time_window_this_week"

    return Intent(
        task_type=task_type,
        is_supported=True,
        metric=lookup_metric(question),
        dimension=lookup_dimension(question),
        time_window=time_window,
        comparison_window=(
            lookup_comparison(question)
            if task_type == "change_explanation"
            else None
        ),
        ranking=ranking,
        ranking_n=ranking_n,
    )


def parse_intent(question: str) -> Intent:
    """Parse a business question into a canonical rule-based Intent."""
    if contains_any(question, FORECASTING_TERMS):
        return _unsupported_intent(question, "forecasting")
    if contains_any(question, CAUSAL_TERMS):
        return _unsupported_intent(question, "causal_inference")
    if contains_any(question, RECOMMENDATION_TERMS):
        return _unsupported_intent(question, "recommendation")
    if _contains_follow_up(question):
        return _unsupported_intent(question, "follow_up")
    if contains_any(question, CROSS_DATASET_TERMS):
        return _unsupported_intent(question, "cross_dataset")

    ranking = lookup_ranking(question)
    ranking_n = extract_ranking_n(question)
    if ranking and ranking_n:
        return _supported_intent(
            "top_n_ranking",
            question,
            ranking=ranking,
            ranking_n=ranking_n,
        )

    if contains_any(question, COMPARE_TERMS):
        return _supported_intent("dimension_comparison", question)

    if contains_any(question, CHANGE_TERMS):
        return _supported_intent("change_explanation", question)

    return _unsupported_intent(question, "unsupported")
