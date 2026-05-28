from pathlib import Path

from analytics import analyze_metrics


DATA_PATH = Path(__file__).resolve().parents[1] / "mock_data.csv"


def test_analyze_chaoyang_gmv_drop():
    """测试朝阳区 GMV 下滑时，分析结果能返回环比和主因。"""
    intent = {
        "metric": "gmv",
        "city": "Beijing",
        "district": "Chaoyang",
        "task": "root_cause_analysis",
        "time_range": "this_week",
    }

    result = analyze_metrics(intent, DATA_PATH)

    assert result["this_week_gmv"] == 630000
    assert result["last_week_gmv"] == 700000
    assert result["gmv_change_rate"] == -10.0
    assert result["main_driver"] == "orders"
    assert "朝阳区" in result["diagnosis"]
    assert "订单量下降" in result["diagnosis"]


def test_analyze_haidian_orders_rise():
    """测试海淀区订单上涨问题也能得到基础分析结果。"""
    intent = {
        "metric": "orders",
        "city": "Beijing",
        "district": "Haidian",
        "task": "root_cause_analysis",
        "time_range": "this_week",
    }

    result = analyze_metrics(intent, DATA_PATH)

    assert result["this_week_orders"] == 8050
    assert result["last_week_orders"] == 7700
    assert result["orders_change_rate"] == 4.5
    assert result["main_driver"] in ["orders", "users", "aov", "peak_orders", "coupon_cost"]
