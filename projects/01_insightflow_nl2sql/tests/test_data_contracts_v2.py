from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

EXPECTED_COLUMNS = {
    "fact_orders": [
        "order_date",
        "district_id",
        "gmv",
        "orders",
        "active_users",
        "peak_orders",
    ],
    "dim_district": [
        "district_id",
        "district_name_zh",
        "district_name_en",
        "city_name_zh",
        "city_name_en",
    ],
    "fact_marketing_cost": [
        "cost_date",
        "district_id",
        "coupon_cost",
    ],
}


def load_v2_tables():
    """读取三张 v2 mock 表，供数据契约测试复用。"""
    tables = {}
    for table_name in EXPECTED_COLUMNS:
        table_path = DATA_DIR / f"{table_name}.csv"
        assert table_path.exists(), f"缺少 v2 mock 表：{table_path.name}"
        tables[table_name] = pd.read_csv(table_path)
    return tables


def test_v2_csv_files_exist_and_have_exact_columns():
    """三张业务表必须存在，且字段顺序与数据模型约定完全一致。"""
    tables = load_v2_tables()

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        assert list(tables[table_name].columns) == expected_columns


def test_v2_primary_keys_are_unique():
    """维表主键和两张事实表的日期区域组合主键不能重复。"""
    tables = load_v2_tables()

    assert tables["dim_district"]["district_id"].is_unique
    assert not tables["fact_orders"].duplicated(
        subset=["order_date", "district_id"]
    ).any()
    assert not tables["fact_marketing_cost"].duplicated(
        subset=["cost_date", "district_id"]
    ).any()


def test_fact_table_foreign_keys_exist_in_district_dimension():
    """两张事实表中的每个区域都必须能关联到区域维表。"""
    tables = load_v2_tables()
    district_ids = set(tables["dim_district"]["district_id"])

    assert set(tables["fact_orders"]["district_id"]) <= district_ids
    assert set(tables["fact_marketing_cost"]["district_id"]) <= district_ids


def test_fact_tables_share_a_continuous_date_range_of_at_least_14_days():
    """两张事实表应覆盖相同且连续的日期，保证周环比可以复现。"""
    tables = load_v2_tables()
    order_dates = pd.to_datetime(tables["fact_orders"]["order_date"])
    cost_dates = pd.to_datetime(tables["fact_marketing_cost"]["cost_date"])
    unique_order_dates = pd.DatetimeIndex(order_dates.unique()).sort_values()
    unique_cost_dates = pd.DatetimeIndex(cost_dates.unique()).sort_values()
    expected_dates = pd.date_range(
        start=unique_order_dates.min(),
        end=unique_order_dates.max(),
        freq="D",
    )

    assert unique_order_dates.equals(unique_cost_dates)
    assert unique_order_dates.equals(expected_dates)
    assert len(unique_order_dates) >= 14


def test_v2_metrics_are_valid_and_aov_can_be_recalculated():
    """经营指标必须非负，且订单量不能为零，以支持客单价复算。"""
    tables = load_v2_tables()
    orders = tables["fact_orders"]
    marketing = tables["fact_marketing_cost"]

    assert (orders["orders"] > 0).all()
    assert (orders[["gmv", "orders", "active_users", "peak_orders"]] >= 0).all().all()
    assert (marketing["coupon_cost"] >= 0).all()

    recalculated_aov = orders["gmv"] / orders["orders"]
    assert recalculated_aov.notna().all()
    assert (recalculated_aov > 0).all()


def test_schema_catalog_defines_business_contracts_and_time_policy():
    """Catalog 应保存稳定业务语义和固定的最近七天时间口径。"""
    from schema_catalog import SCHEMA_CATALOG, TIME_WINDOW_POLICY

    assert set(SCHEMA_CATALOG) == set(EXPECTED_COLUMNS)

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        table_definition = SCHEMA_CATALOG[table_name]
        assert table_definition["description"]
        assert table_definition["primary_key"]
        assert set(table_definition["columns"]) == set(expected_columns)

        for column_name in expected_columns:
            column_definition = table_definition["columns"][column_name]
            assert column_definition["description"]
            assert column_definition["semantic_type"] in {
                "metric",
                "dimension",
                "identifier",
                "time",
            }
            assert isinstance(column_definition["aliases"], list)

    assert SCHEMA_CATALOG["fact_orders"]["foreign_keys"] == {
        "district_id": "dim_district.district_id"
    }
    assert SCHEMA_CATALOG["fact_marketing_cost"]["foreign_keys"] == {
        "district_id": "dim_district.district_id"
    }
    assert SCHEMA_CATALOG["dim_district"]["foreign_keys"] == {}

    assert TIME_WINDOW_POLICY == {
        "anchor": "max_data_date",
        "current_period_days": 7,
        "previous_period_days": 7,
        "current_period_definition": "数据集中最新日期及之前 6 天",
        "previous_period_definition": "本周之前连续 7 天",
    }
