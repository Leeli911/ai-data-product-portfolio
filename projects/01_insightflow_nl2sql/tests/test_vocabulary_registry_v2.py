from text2analytics_engine.vocabulary import VocabularyRegistry


def test_registry_resolves_metric_aliases_to_canonical_ids():
    registry = VocabularyRegistry.default()

    assert registry.lookup_metric("GMV") == "metric_gmv"
    assert registry.lookup_metric("revenue decline") == "metric_revenue"
    assert registry.lookup_metric("订单量减少") == "metric_orders"


def test_registry_resolves_dimension_aliases_to_canonical_ids():
    registry = VocabularyRegistry.default()

    assert registry.lookup_dimension("districts") == "dimension_district"
    assert registry.lookup_dimension("朝阳区") == "dimension_district"
    assert registry.lookup_dimension("商品") == "dimension_product"


def test_registry_resolves_time_window_aliases_to_canonical_ids():
    registry = VocabularyRegistry.default()

    assert registry.lookup_time_window("this week") == (
        "time_window_this_week"
    )
    assert registry.lookup_time_window("最近 30 天") == (
        "time_window_last_30_days"
    )
    assert registry.lookup_time_window("昨天") == "time_window_yesterday"


def test_registry_resolves_comparison_aliases_to_canonical_ids():
    registry = VocabularyRegistry.default()

    assert registry.lookup_comparison("week over week") == (
        "comparison_week_over_week"
    )
    assert registry.lookup_comparison("和上周相比") == (
        "comparison_week_over_week"
    )
    assert registry.lookup_comparison("同比") == (
        "comparison_year_over_year"
    )


def test_registry_resolves_ranking_aliases_to_canonical_ids():
    registry = VocabularyRegistry.default()

    assert registry.lookup_ranking("top 3 districts") == "ranking_top_n"
    assert registry.lookup_ranking("最高的 3 个区域") == "ranking_top_n"
    assert registry.lookup_ranking("bottom 5 districts") == (
        "ranking_bottom_n"
    )
    assert registry.lookup_ranking("最低的 5 个区域") == "ranking_bottom_n"


def test_registry_returns_none_for_unknown_lookup():
    registry = VocabularyRegistry.default()

    assert registry.lookup_metric("gross margin") is None
    assert registry.lookup_dimension("warehouse") is None
    assert registry.lookup_time_window("during the launch") is None
    assert registry.lookup_comparison("against control group") is None
    assert registry.lookup_ranking("middle performers") is None
