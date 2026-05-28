"""数据分析和业务诊断模块。"""

from pathlib import Path

import pandas as pd


DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "mock_data.csv"


DISTRICT_LABELS = {
    "Chaoyang": "朝阳区",
    "Haidian": "海淀区",
}


DRIVER_LABELS = {
    "orders": "订单量",
    "users": "用户数",
    "aov": "客单价",
    "peak_orders": "高峰期订单",
    "coupon_cost": "优惠券成本",
}


def calculate_change_rate(current_value, previous_value):
    """计算环比变化率，返回百分比数值。"""
    if previous_value == 0:
        return 0.0
    return round((current_value - previous_value) / previous_value * 100, 1)


def get_weekly_data(df, city, district):
    """按最新日期和上一期日期取出目标城市、区域的两周数据。"""
    target_df = df[(df["city"] == city) & (df["district"] == district)].copy()
    target_df = target_df.sort_values("date")

    if len(target_df) < 2:
        raise ValueError("目标城市和区域至少需要两周数据")

    previous_data = target_df.iloc[-2]
    current_data = target_df.iloc[-1]
    return previous_data, current_data


def find_main_driver(change_rates):
    """从多个指标变化率中找出变化幅度最大的因素。"""
    driver_candidates = {
        "orders": abs(change_rates["orders_change_rate"]),
        "users": abs(change_rates["users_change_rate"]),
        "aov": abs(change_rates["aov_change_rate"]),
        "peak_orders": abs(change_rates["peak_orders_change_rate"]),
        "coupon_cost": abs(change_rates["coupon_cost_change_rate"]),
    }
    return max(driver_candidates, key=driver_candidates.get)


def build_diagnosis(district, gmv_change_rate, main_driver):
    """根据分析结果生成业务诊断说明。"""
    district_label = DISTRICT_LABELS.get(district, district)
    driver_label = DRIVER_LABELS.get(main_driver, main_driver)

    if gmv_change_rate < 0:
        direction = "下降"
    elif gmv_change_rate > 0:
        direction = "上升"
    else:
        direction = "基本持平"

    if main_driver == "orders" and gmv_change_rate < 0:
        reason = "主要原因是订单量下降"
    else:
        reason = f"主要变化因素是{driver_label}"

    return f"{district_label}本周 GMV 环比{direction} {abs(gmv_change_rate)}%，{reason}。"


def analyze_metrics(intent, data_path=DEFAULT_DATA_PATH):
    """读取 mock 数据，计算本周、上周、环比变化和主要影响因素。"""
    df = pd.read_csv(data_path)
    previous_data, current_data = get_weekly_data(df, intent["city"], intent["district"])

    this_week_gmv = int(current_data["gmv"])
    last_week_gmv = int(previous_data["gmv"])
    this_week_orders = int(current_data["orders"])
    last_week_orders = int(previous_data["orders"])

    change_rates = {
        "gmv_change_rate": calculate_change_rate(this_week_gmv, last_week_gmv),
        "orders_change_rate": calculate_change_rate(this_week_orders, last_week_orders),
        "users_change_rate": calculate_change_rate(current_data["users"], previous_data["users"]),
        "aov_change_rate": calculate_change_rate(current_data["aov"], previous_data["aov"]),
        "peak_orders_change_rate": calculate_change_rate(
            current_data["peak_orders"],
            previous_data["peak_orders"],
        ),
        "coupon_cost_change_rate": calculate_change_rate(
            current_data["coupon_cost"],
            previous_data["coupon_cost"],
        ),
    }
    main_driver = find_main_driver(change_rates)

    return {
        "this_week_gmv": this_week_gmv,
        "last_week_gmv": last_week_gmv,
        "gmv_change_rate": change_rates["gmv_change_rate"],
        "this_week_orders": this_week_orders,
        "last_week_orders": last_week_orders,
        "orders_change_rate": change_rates["orders_change_rate"],
        "users_change_rate": change_rates["users_change_rate"],
        "aov_change_rate": change_rates["aov_change_rate"],
        "peak_orders_change_rate": change_rates["peak_orders_change_rate"],
        "coupon_cost_change_rate": change_rates["coupon_cost_change_rate"],
        "main_driver": main_driver,
        "diagnosis": build_diagnosis(
            intent["district"],
            change_rates["gmv_change_rate"],
            main_driver,
        ),
    }
