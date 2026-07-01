"""Vocabulary-backed lookup helpers for the rule-based Intent Parser."""

import re

from text2analytics_engine.vocabulary import (
    DEFAULT_VOCABULARY_REGISTRY,
    contains_phrase,
)


def lookup_metric(question: str) -> str | None:
    """Return a canonical metric ID from the runtime vocabulary registry."""
    return DEFAULT_VOCABULARY_REGISTRY.lookup_metric(question)


def lookup_dimension(question: str) -> str | None:
    """Return a canonical dimension ID from the runtime vocabulary registry."""
    return DEFAULT_VOCABULARY_REGISTRY.lookup_dimension(question)


def lookup_time_window(question: str) -> str | None:
    """Return a canonical time-window ID from the runtime vocabulary registry."""
    return DEFAULT_VOCABULARY_REGISTRY.lookup_time_window(question)


def lookup_comparison(question: str) -> str | None:
    """Return a canonical comparison ID from the runtime vocabulary registry."""
    comparison = DEFAULT_VOCABULARY_REGISTRY.lookup_comparison(question)
    if comparison:
        return comparison
    if lookup_time_window(question) == "time_window_this_week":
        return "comparison_week_over_week"
    return None


def lookup_ranking(question: str) -> str | None:
    """Return a canonical ranking ID from the runtime vocabulary registry."""
    return DEFAULT_VOCABULARY_REGISTRY.lookup_ranking(question)


def extract_ranking_n(question: str) -> int | None:
    """Extract a positive integer N for top/bottom questions."""
    match = re.search(r"\b(\d+)\b", question)
    if match:
        value = int(match.group(1))
        return value if value > 0 else None
    return None


def contains_any(question: str, phrases: tuple[str, ...]) -> bool:
    """Return whether any phrase appears in a question."""
    return any(contains_phrase(question, phrase) for phrase in phrases)
