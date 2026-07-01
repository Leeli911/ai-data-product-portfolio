"""Canonical Vocabulary runtime for Text2Analytics V2."""

from text2analytics_engine.vocabulary.registry import (
    DEFAULT_VOCABULARY_REGISTRY,
    VocabularyRegistry,
    contains_phrase,
)

__all__ = [
    "DEFAULT_VOCABULARY_REGISTRY",
    "VocabularyRegistry",
    "contains_phrase",
]
