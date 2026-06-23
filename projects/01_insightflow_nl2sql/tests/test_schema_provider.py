from schema_provider import build_schema_snapshot


def test_snapshot_matches_existing_schema_catalog():
    """SQL 模块只能读取 Catalog 中已声明的三张表和字段。"""
    snapshot = build_schema_snapshot()
    tables = {table.name: table for table in snapshot.tables}

    assert set(tables) == {
        "fact_orders",
        "dim_district",
        "fact_marketing_cost",
    }
    fact_orders_columns = {
        column.name: column.semantic_type
        for column in tables["fact_orders"].columns
    }
    assert fact_orders_columns == {
        "order_date": "time",
        "district_id": "identifier",
        "gmv": "metric",
        "orders": "metric",
        "active_users": "metric",
        "peak_orders": "metric",
    }


def test_snapshot_exposes_known_tables_and_columns_as_sets():
    """Snapshot 提供简单只读集合，供 SQL Validator 复用。"""
    snapshot = build_schema_snapshot()

    assert snapshot.table_names == {
        "fact_orders",
        "dim_district",
        "fact_marketing_cost",
    }
    assert "coupon_cost" in snapshot.column_names
    assert "profit" not in snapshot.column_names
