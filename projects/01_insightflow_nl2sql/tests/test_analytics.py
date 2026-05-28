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


def test_analyze_daily_data_by_latest_two_7_day_windows(tmp_path):
    """测试日粒度数据会按最近 7 天和前 7 天聚合分析。"""
    data_path = tmp_path / "daily_mock_data.csv"
    data_path.write_text(
        "\n".join(
            [
                "date,city,district,gmv,orders,users,aov,peak_orders,coupon_cost",
                "2026-05-06,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-07,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-08,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-09,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-10,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-11,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-12,Beijing,Chaoyang,100,10,8,10,3,10",
                "2026-05-13,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-14,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-15,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-16,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-17,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-18,Beijing,Chaoyang,90,9,8,10,3,10",
                "2026-05-19,Beijing,Chaoyang,90,9,8,10,3,10",
            ]
        ),
        encoding="utf-8",
    )
    intent = {
        "metric": "gmv",
        "city": "Beijing",
        "district": "Chaoyang",
        "task": "root_cause_analysis",
        "time_range": "this_week",
    }

    result = analyze_metrics(intent, data_path)

    assert result["this_week_gmv"] == 630
    assert result["last_week_gmv"] == 700
    assert result["gmv_change_rate"] == -10.0
