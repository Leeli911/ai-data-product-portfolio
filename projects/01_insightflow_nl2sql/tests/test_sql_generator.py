from sql_generator import generate_sql


def test_generate_sql_for_chaoyang_gmv_query():
    """测试结构化意图是否能生成字段和筛选条件正确的 SQL。"""
    intent = {
        "metric": "gmv",
        "city": "Beijing",
        "district": "Chaoyang",
        "task": "root_cause_analysis",
        "time_range": "this_week",
    }

    sql = generate_sql(intent)

    assert "SELECT" in sql
    assert "SUM(gmv) AS gmv" in sql
    assert "FROM local_life_metrics" in sql
    assert "city = 'Beijing'" in sql
    assert "district = 'Chaoyang'" in sql
    assert "GROUP BY date, district" in sql


def test_generate_sql_for_orders_query():
    """测试订单指标是否会映射到 orders 聚合字段。"""
    intent = {
        "metric": "orders",
        "city": "Beijing",
        "district": "Haidian",
        "task": "root_cause_analysis",
        "time_range": "this_week",
    }

    sql = generate_sql(intent)

    assert "SUM(orders) AS orders" in sql
    assert "district = 'Haidian'" in sql
