"""根据黄金分析计划生成确定性的 DuckDB 候选 SQL。"""

from contracts import GeneratedQuery, SQLGenerationRequest, SQLGenerationResult


VERIFY_GMV_SQL = """
WITH bounds AS (
    SELECT MAX(order_date::DATE) AS max_date
    FROM fact_orders
), period_orders AS (
    SELECT
        CASE
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '6 days' AND b.max_date
                THEN 'current'
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date - INTERVAL '7 days'
                THEN 'previous'
        END AS period,
        o.gmv
    FROM fact_orders AS o
    CROSS JOIN bounds AS b
    JOIN dim_district AS d ON o.district_id = d.district_id
    WHERE d.district_name_en = 'Chaoyang'
      AND o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date
)
SELECT
    period,
    CAST(SUM(gmv) AS DOUBLE) AS gmv
FROM period_orders
GROUP BY period
ORDER BY period;
""".strip()


DECOMPOSE_GMV_SQL = """
WITH bounds AS (
    SELECT MAX(order_date::DATE) AS max_date
    FROM fact_orders
), period_orders AS (
    SELECT
        CASE
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '6 days' AND b.max_date
                THEN 'current'
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date - INTERVAL '7 days'
                THEN 'previous'
        END AS period,
        o.gmv,
        o.orders,
        o.active_users
    FROM fact_orders AS o
    CROSS JOIN bounds AS b
    JOIN dim_district AS d ON o.district_id = d.district_id
    WHERE d.district_name_en = 'Chaoyang'
      AND o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date
)
SELECT
    period,
    CAST(SUM(gmv) AS DOUBLE) AS gmv,
    CAST(SUM(orders) AS DOUBLE) AS orders,
    CAST(SUM(active_users) AS DOUBLE) AS active_users,
    CAST(SUM(gmv) AS DOUBLE) / NULLIF(CAST(SUM(orders) AS DOUBLE), 0) AS aov
FROM period_orders
GROUP BY period
ORDER BY period;
""".strip()


SUPPORTING_SIGNALS_SQL = """
WITH bounds AS (
    SELECT MAX(order_date::DATE) AS max_date
    FROM fact_orders
), order_signals AS (
    SELECT
        CASE
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '6 days' AND b.max_date
                THEN 'current'
            WHEN o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date - INTERVAL '7 days'
                THEN 'previous'
        END AS period,
        CAST(SUM(o.peak_orders) AS DOUBLE) AS peak_orders
    FROM fact_orders AS o
    CROSS JOIN bounds AS b
    JOIN dim_district AS d ON o.district_id = d.district_id
    WHERE d.district_name_en = 'Chaoyang'
      AND o.order_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date
    GROUP BY period
), marketing_signals AS (
    SELECT
        CASE
            WHEN m.cost_date::DATE BETWEEN b.max_date - INTERVAL '6 days' AND b.max_date
                THEN 'current'
            WHEN m.cost_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date - INTERVAL '7 days'
                THEN 'previous'
        END AS period,
        CAST(SUM(m.coupon_cost) AS DOUBLE) AS coupon_cost
    FROM fact_marketing_cost AS m
    CROSS JOIN bounds AS b
    JOIN dim_district AS d ON m.district_id = d.district_id
    WHERE d.district_name_en = 'Chaoyang'
      AND m.cost_date::DATE BETWEEN b.max_date - INTERVAL '13 days' AND b.max_date
    GROUP BY period
)
SELECT
    o.period,
    o.peak_orders,
    m.coupon_cost
FROM order_signals AS o
JOIN marketing_signals AS m ON o.period = m.period
ORDER BY o.period;
""".strip()


QUERY_DEFINITIONS = {
    "verify_gmv_change": (
        "比较本周与上周 GMV",
        VERIFY_GMV_SQL,
        {"fact_orders", "dim_district"},
    ),
    "decompose_gmv": (
        "拆解订单量、活跃用户和客单价",
        DECOMPOSE_GMV_SQL,
        {"fact_orders", "dim_district"},
    ),
    "check_supporting_signals": (
        "检查高峰订单和优惠券成本",
        SUPPORTING_SIGNALS_SQL,
        {"fact_orders", "dim_district", "fact_marketing_cost"},
    ),
}


def generate_queries(request: SQLGenerationRequest) -> SQLGenerationResult:
    """为每个已知计划步骤生成一条候选查询。"""
    queries = []
    for step in request.plan.steps:
        if step.step_id not in QUERY_DEFINITIONS:
            raise ValueError(f"不支持的分析步骤：{step.step_id}")

        purpose, sql, required_tables = QUERY_DEFINITIONS[step.step_id]
        missing_tables = required_tables - request.schema_snapshot.table_names
        if missing_tables:
            missing_text = ", ".join(sorted(missing_tables))
            raise ValueError(f"Schema Snapshot 缺少表：{missing_text}")

        queries.append(
            GeneratedQuery(
                step_id=step.step_id,
                purpose=purpose,
                sql=sql,
            )
        )

    return SQLGenerationResult(queries=queries)
