"""生成本地生活业务 mock 数据。"""

from datetime import date, timedelta

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


if __name__ == "__main__":
    save_mock_data("mock_data_extended.csv")
