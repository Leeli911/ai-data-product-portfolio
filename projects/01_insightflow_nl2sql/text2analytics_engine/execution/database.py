"""DuckDB database setup for Text2Analytics V2 execution tests."""

from pathlib import Path

import duckdb


DEFAULT_TRANSACTIONS_CSV = (
    Path(__file__).resolve().parents[2] / "mock_data_extended.csv"
)


def _quote_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def initialize_duckdb(
    transactions_csv: Path | str | None = None,
) -> duckdb.DuckDBPyConnection:
    """Initialize DuckDB and expose the local transaction CSV as a view."""
    csv_path = Path(transactions_csv or DEFAULT_TRANSACTIONS_CSV)
    if not csv_path.exists():
        raise FileNotFoundError(f"transactions CSV not found: {csv_path}")

    connection = duckdb.connect(database=":memory:")
    quoted_csv_path = _quote_path(csv_path)

    connection.execute(
        "CREATE OR REPLACE VIEW raw_local_life_transactions AS "
        f"SELECT * FROM read_csv_auto('{quoted_csv_path}')"
    )
    connection.execute(
        "CREATE OR REPLACE VIEW local_life_transactions AS "
        "SELECT "
        "CAST(date AS VARCHAR) AS period, "
        "CAST(date AS DATE) AS transaction_date, "
        "CAST(city AS VARCHAR) AS city, "
        "CAST(district AS VARCHAR) AS district, "
        "CAST(gmv AS DOUBLE) AS gmv, "
        "CAST(orders AS DOUBLE) AS orders, "
        "CAST(users AS DOUBLE) AS users, "
        "CAST(aov AS DOUBLE) AS aov, "
        "CAST(peak_orders AS DOUBLE) AS peak_orders, "
        "CAST(coupon_cost AS DOUBLE) AS coupon_cost "
        "FROM raw_local_life_transactions"
    )

    return connection
