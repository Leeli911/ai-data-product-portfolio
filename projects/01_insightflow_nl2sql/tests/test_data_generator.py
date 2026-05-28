from data_generator import generate_mock_data


def test_generate_mock_data_has_expected_shape():
    """测试生成器能产出稳定字段和足够多的日粒度样本。"""
    df = generate_mock_data(days=14)

    assert len(df) == 56
    assert list(df.columns) == [
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


def test_generate_mock_data_keeps_chaoyang_recent_gmv_drop():
    """测试合成数据中朝阳区最近 7 天 GMV 低于前 7 天。"""
    df = generate_mock_data(days=14)
    chaoyang_df = df[df["district"] == "Chaoyang"].sort_values("date")

    previous_gmv = chaoyang_df.iloc[:7]["gmv"].sum()
    current_gmv = chaoyang_df.iloc[7:]["gmv"].sum()

    assert current_gmv < previous_gmv
