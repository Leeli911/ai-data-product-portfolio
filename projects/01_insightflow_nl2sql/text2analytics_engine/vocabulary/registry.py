"""Canonical Vocabulary runtime registry for Text2Analytics V2."""

import re
from functools import cached_property

from text2analytics_engine.vocabulary.models import (
    ComparisonTerm,
    DimensionTerm,
    MetricTerm,
    RankingTerm,
    TimeWindowTerm,
)


METRICS = (
    MetricTerm(
        metric_id="metric_gmv",
        display_name="GMV",
        aliases=("GMV", "revenue", "sales", "交易额", "销售额"),
        definition="Gross merchandise value observed in transaction records.",
        aggregation_type="aggregation_sum",
        unit="CNY",
    ),
    MetricTerm(
        metric_id="metric_revenue",
        display_name="Revenue",
        aliases=("revenue", "sales", "收入", "营收", "销售额"),
        definition=(
            "Revenue-like business amount. In the current local dataset it "
            "maps to GMV unless a separate revenue field is introduced."
        ),
        aggregation_type="aggregation_sum",
        unit="CNY",
    ),
    MetricTerm(
        metric_id="metric_orders",
        display_name="Orders",
        aliases=("orders", "order volume", "order count", "订单量", "订单数"),
        definition="Number of completed orders in the selected scope.",
        aggregation_type="aggregation_sum",
        unit="orders",
    ),
    MetricTerm(
        metric_id="metric_users",
        display_name="Active Users",
        aliases=("users", "active users", "活跃用户", "用户数"),
        definition=(
            "Number of users with observed transaction activity in the "
            "selected scope."
        ),
        aggregation_type="aggregation_sum",
        unit="users",
    ),
    MetricTerm(
        metric_id="metric_aov",
        display_name="Average Order Value",
        aliases=("AOV", "average order value", "客单价"),
        definition="Average monetary value per order, derived as GMV / orders.",
        aggregation_type="aggregation_average",
        unit="CNY/order",
    ),
    MetricTerm(
        metric_id="metric_peak_orders",
        display_name="Peak Orders",
        aliases=("peak orders", "peak-hour orders", "高峰订单", "高峰期订单"),
        definition="Number of orders completed during peak business hours.",
        aggregation_type="aggregation_sum",
        unit="orders",
    ),
    MetricTerm(
        metric_id="metric_coupon_cost",
        display_name="Coupon Cost",
        aliases=("coupon cost", "subsidy cost", "优惠券成本", "补贴成本"),
        definition="Observed coupon or subsidy cost in the selected scope.",
        aggregation_type="aggregation_sum",
        unit="CNY",
    ),
)


DIMENSIONS = (
    DimensionTerm(
        dimension_id="dimension_district",
        aliases=("district", "region", "area", "区域", "地区", "行政区"),
        supported_filters=("Chaoyang", "Haidian", "朝阳", "海淀"),
    ),
    DimensionTerm(
        dimension_id="dimension_region",
        aliases=("region", "market", "business region", "大区", "区域"),
        supported_filters=("North", "South", "East", "West", "华北", "华东", "华南"),
    ),
    DimensionTerm(
        dimension_id="dimension_store",
        aliases=("store", "shop", "merchant", "门店", "商家"),
        supported_filters=("store_id", "store_name"),
    ),
    DimensionTerm(
        dimension_id="dimension_category",
        aliases=("category", "product category", "品类", "类目"),
        supported_filters=("category_id", "category_name"),
    ),
    DimensionTerm(
        dimension_id="dimension_product",
        aliases=("product", "item", "SKU", "商品", "产品"),
        supported_filters=("product_id", "product_name"),
    ),
    DimensionTerm(
        dimension_id="dimension_city",
        aliases=("city", "城市"),
        supported_filters=("Beijing", "Shanghai", "北京", "上海"),
    ),
    DimensionTerm(
        dimension_id="dimension_period",
        aliases=("period", "time period", "周期", "时间段"),
        supported_filters=("current", "previous", "本期", "上期"),
    ),
)


TIME_WINDOWS = (
    TimeWindowTerm(
        time_window_id="time_window_this_week",
        aliases=("this week", "current week", "本周", "这周"),
        definition="Latest 7-day window available in the dataset.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_last_week",
        aliases=("last week", "previous week", "上周"),
        definition="The 7-day window immediately before this week.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_yesterday",
        aliases=("yesterday", "昨天"),
        definition="The latest available date minus one day, if daily data exists.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_latest_7_days",
        aliases=("latest 7 days", "recent 7 days", "最近 7 天"),
        definition="Dataset max date and previous 6 days.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_last_30_days",
        aliases=("last 30 days", "recent 30 days", "最近 30 天"),
        definition="Dataset max date and previous 29 days.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_this_month",
        aliases=("this month", "current month", "本月"),
        definition="Current month-like period inferred from dataset max date.",
    ),
    TimeWindowTerm(
        time_window_id="time_window_last_month",
        aliases=("last month", "previous month", "上月"),
        definition="Previous month-like period before this month.",
    ),
)


COMPARISONS = (
    ComparisonTerm(
        comparison_id="comparison_week_over_week",
        aliases=(
            "WoW",
            "week over week",
            "compared with last week",
            "和上周相比",
            "环比上周",
            "周环比",
        ),
        definition=(
            "Compare a current 7-day or week-like window with the immediately "
            "previous comparable window."
        ),
    ),
    ComparisonTerm(
        comparison_id="comparison_month_over_month",
        aliases=("MoM", "month over month", "compared with last month", "月环比"),
        definition=(
            "Compare a current month-like window with the previous month-like "
            "window."
        ),
    ),
    ComparisonTerm(
        comparison_id="comparison_year_over_year",
        aliases=("YoY", "year over year", "compared with last year", "同比"),
        definition=(
            "Compare a current period with the same period in the previous year."
        ),
    ),
    ComparisonTerm(
        comparison_id="comparison_previous_period",
        aliases=("previous period", "prior period", "环比", "与上一期相比"),
        definition=(
            "Compare current period with the immediately previous comparable "
            "period."
        ),
    ),
    ComparisonTerm(
        comparison_id="comparison_current_vs_previous",
        aliases=("current vs previous", "本期对比上期"),
        definition="Generic current period versus previous period comparison.",
    ),
)


RANKINGS = (
    RankingTerm(
        ranking_id="ranking_top_n",
        aliases=("top N", "top", "highest", "largest", "最高", "最大", "前 N", "前"),
        definition="Return the N dimension values with the largest metric values.",
    ),
    RankingTerm(
        ranking_id="ranking_bottom_n",
        aliases=(
            "bottom N",
            "bottom",
            "lowest",
            "smallest",
            "最低",
            "最小",
            "后 N",
            "后",
        ),
        definition="Return the N dimension values with the smallest metric values.",
    ),
)


class VocabularyRegistry:
    """In-memory canonical vocabulary registry."""

    def __init__(
        self,
        metrics: tuple[MetricTerm, ...],
        dimensions: tuple[DimensionTerm, ...],
        time_windows: tuple[TimeWindowTerm, ...],
        comparisons: tuple[ComparisonTerm, ...],
        rankings: tuple[RankingTerm, ...],
    ):
        self.metrics = metrics
        self.dimensions = dimensions
        self.time_windows = time_windows
        self.comparisons = comparisons
        self.rankings = rankings

    @classmethod
    def default(cls):
        """Create the default Text2Analytics V2 vocabulary registry."""
        return cls(
            metrics=METRICS,
            dimensions=DIMENSIONS,
            time_windows=TIME_WINDOWS,
            comparisons=COMPARISONS,
            rankings=RANKINGS,
        )

    @cached_property
    def metric_ids(self) -> set[str]:
        """Return all canonical metric IDs."""
        return {item.metric_id for item in self.metrics}

    def lookup_metric(self, question: str) -> str | None:
        """Look up a canonical metric ID from aliases or display name."""
        return _choose_term(
            question,
            [
                (metric.metric_id, (metric.display_name, *metric.aliases))
                for metric in self.metrics
            ],
        )

    def lookup_dimension(self, question: str) -> str | None:
        """Look up a canonical dimension ID from aliases or filters."""
        return _choose_term(
            question,
            [
                (
                    dimension.dimension_id,
                    (*dimension.aliases, *dimension.supported_filters),
                )
                for dimension in self.dimensions
            ],
        )

    def lookup_time_window(self, question: str) -> str | None:
        """Look up a canonical time-window ID from aliases."""
        return _choose_term(
            question,
            [
                (time_window.time_window_id, time_window.aliases)
                for time_window in self.time_windows
            ],
        )

    def lookup_comparison(self, question: str) -> str | None:
        """Look up a canonical comparison ID from aliases."""
        return _choose_term(
            question,
            [
                (comparison.comparison_id, comparison.aliases)
                for comparison in self.comparisons
            ],
        )

    def lookup_ranking(self, question: str) -> str | None:
        """Look up a canonical ranking ID from aliases."""
        return _choose_term(
            question,
            [
                (ranking.ranking_id, ranking.aliases)
                for ranking in self.rankings
            ],
        )


def _is_ascii_phrase(value: str) -> bool:
    return all(ord(char) < 128 for char in value)


def contains_phrase(text: str, phrase: str) -> bool:
    """Match English phrases by word-ish boundary and Chinese by substring."""
    normalized_text = text.lower()
    normalized_phrase = phrase.lower().strip()
    if not normalized_phrase:
        return False

    if _is_ascii_phrase(normalized_phrase):
        flexible_phrase = re.escape(normalized_phrase).replace("\\ ", r"\s+")
        plural_suffix = "s?" if normalized_phrase.isalpha() else ""
        pattern = rf"(?<![a-z0-9]){flexible_phrase}{plural_suffix}(?![a-z0-9])"
        return re.search(pattern, normalized_text) is not None

    return normalized_phrase in normalized_text


def _choose_term(
    question: str,
    candidates: list[tuple[str, tuple[str, ...]]],
) -> str | None:
    """Choose the best canonical ID from ordered candidates."""
    best_score = -1
    best_id = None
    for canonical_id, aliases in candidates:
        matched_aliases = [
            alias for alias in aliases if contains_phrase(question, alias)
        ]
        if not matched_aliases:
            continue

        id_tokens = canonical_id.replace("_", " ").lower()
        score = max(
            len(alias) + (100 if alias.lower() in id_tokens else 0)
            for alias in matched_aliases
        )
        if score > best_score:
            best_score = score
            best_id = canonical_id

    return best_id


DEFAULT_VOCABULARY_REGISTRY = VocabularyRegistry.default()
