"""生成本地生活业务 mock 数据。"""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "city",
    "district",
    "gmv",
    "orders",
    "users",
    "aov",
    "peak_orders",
    "coupon_cost",
]


DISTRICT_CONFIGS = [
    {
        "city": "Beijing",
        "district": "Chaoyang",
        "base_orders": 1000,
        "base_users": 820,
        "base_aov": 100,
        "current_week_order_factor": 0.9,
    },
    {
        "city": "Beijing",
        "district": "Haidian",
        "base_orders": 1100,
        "base_users": 900,
        "base_aov": 81,
        "current_week_order_factor": 1.05,
    },
    {
        "city": "Beijing",
        "district": "Fengtai",
        "base_orders": 760,
        "base_users": 610,
        "base_aov": 88,
        "current_week_order_factor": 1.0,
    },
    {
        "city": "Shanghai",
        "district": "Pudong",
        "base_orders": 1250,
        "base_users": 980,
        "base_aov": 95,
        "current_week_order_factor": 1.03,
    },
]


DISTRICT_DIMENSION_ROWS = [
    {
        "district_id": "BJ_CHAOYANG",
        "district_name_zh": "朝阳区",
        "district_name_en": "Chaoyang",
        "city_name_zh": "北京市",
        "city_name_en": "Beijing",
    },
    {
        "district_id": "BJ_HAIDIAN",
        "district_name_zh": "海淀区",
        "district_name_en": "Haidian",
        "city_name_zh": "北京市",
        "city_name_en": "Beijing",
    },
    {
        "district_id": "BJ_FENGTAI",
        "district_name_zh": "丰台区",
        "district_name_en": "Fengtai",
        "city_name_zh": "北京市",
        "city_name_en": "Beijing",
    },
    {
        "district_id": "SH_PUDONG",
        "district_name_zh": "浦东新区",
        "district_name_en": "Pudong",
        "city_name_zh": "上海市",
        "city_name_en": "Shanghai",
    },
]


def get_day_factor(day_index):
    """生成简单的工作日和周末波动系数。"""
    weekday = day_index % 7
    if weekday in [5, 6]:
        return 1.08
    return 1.0


def get_current_week_factor(day_index, total_days, base_factor):
    """最近 7 天使用指定业务变化系数。"""
    if day_index >= total_days - 7:
        return base_factor
    return 1.0


def build_daily_row(current_date, day_index, total_days, config):
    """根据区域配置生成单日经营指标。"""
    day_factor = get_day_factor(day_index)
    trend_factor = 1 + day_index * 0.001
    current_week_factor = get_current_week_factor(
        day_index,
        total_days,
        config["current_week_order_factor"],
    )

    orders = int(config["base_orders"] * day_factor * trend_factor * current_week_factor)
    users = int(config["base_users"] * day_factor * trend_factor)
    aov = round(config["base_aov"] * (1 + (day_index % 5) * 0.002), 1)
    gmv = int(round(orders * aov, 0))
    peak_orders = int(orders * 0.31)
    coupon_cost = int(gmv * 0.1)

    return {
        "date": current_date.isoformat(),
        "city": config["city"],
        "district": config["district"],
        "gmv": gmv,
        "orders": orders,
        "users": users,
        "aov": aov,
        "peak_orders": peak_orders,
        "coupon_cost": coupon_cost,
    }


def generate_mock_data(days=56, start_date=date(2026, 4, 1)):
    """生成可重复的多城市、多区域、日粒度 mock 数据。"""
    rows = []
    for day_index in range(days):
        current_date = start_date + timedelta(days=day_index)
        for config in DISTRICT_CONFIGS:
            rows.append(build_daily_row(current_date, day_index, days, config))

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def save_mock_data(output_path, days=56):
    """将生成的数据保存为 CSV 文件。"""
    df = generate_mock_data(days=days)
    df.to_csv(output_path, index=False)
    return output_path


def build_v2_tables(source_df=None):
    """将现有单表 mock 数据拆分为三张 v2 业务表。"""
    if source_df is None:
        source_df = generate_mock_data()

    dim_district = pd.DataFrame(DISTRICT_DIMENSION_ROWS)
    district_lookup = dim_district[
        ["district_id", "district_name_en", "city_name_en"]
    ]
    enriched_df = source_df.merge(
        district_lookup,
        left_on=["district", "city"],
        right_on=["district_name_en", "city_name_en"],
        how="left",
        validate="many_to_one",
    )

    if enriched_df["district_id"].isna().any():
        raise ValueError("存在无法映射到 dim_district 的区域")

    fact_orders = enriched_df[
        ["date", "district_id", "gmv", "orders", "users", "peak_orders"]
    ].rename(
        columns={
            "date": "order_date",
            "users": "active_users",
        }
    )
    fact_marketing_cost = enriched_df[
        ["date", "district_id", "coupon_cost"]
    ].rename(columns={"date": "cost_date"})

    return {
        "fact_orders": fact_orders,
        "dim_district": dim_district,
        "fact_marketing_cost": fact_marketing_cost,
    }


def save_v2_tables(output_dir, days=56):
    """生成并保存三张 InsightFlow v2 mock 业务表。"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = build_v2_tables(generate_mock_data(days=days))

    for table_name, table_df in tables.items():
        table_df.to_csv(output_dir / f"{table_name}.csv", index=False)

    return tables


if __name__ == "__main__":
    save_mock_data("mock_data_extended.csv")
