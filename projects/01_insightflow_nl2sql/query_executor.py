"""仅执行 SQL Validator 通过的 DuckDB 查询。"""

from pathlib import Path

import duckdb

from contracts import QueryExecutionResult, ValidatedQuery


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"
DEMO_TABLES = ("fact_orders", "dim_district", "fact_marketing_cost")


def _open_demo_connection(data_dir: Path):
    """将三张本地 CSV 注册为内存 DuckDB 视图。"""
    connection = duckdb.connect(":memory:")
    for table_name in DEMO_TABLES:
        csv_path = str(
            (data_dir / f"{table_name}.csv").resolve()
        ).replace("'", "''")
        connection.execute(
            f"CREATE VIEW {table_name} AS "
            f"SELECT * FROM read_csv_auto('{csv_path}')"
        )
    return connection


def execute_query(
    query: ValidatedQuery,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> QueryExecutionResult:
    """执行一条已验证 SQL，并返回可序列化的结构化结果。"""
    if not isinstance(query, ValidatedQuery):
        raise TypeError("execute_query 只接受 ValidatedQuery")

    connection = _open_demo_connection(Path(data_dir))
    try:
        cursor = connection.execute(query.sql)
        columns = [description[0] for description in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]
        return QueryExecutionResult(
            step_id=query.step_id,
            columns=columns,
            rows=rows,
            row_count=len(rows),
        )
    finally:
        connection.close()
