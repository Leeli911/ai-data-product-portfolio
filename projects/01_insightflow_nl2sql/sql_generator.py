"""SQL 生成模块。"""


def generate_sql(intent):
    """根据结构化分析意图生成逻辑合理的 SQL 字符串。"""
    metric = intent["metric"]
    city = intent["city"]
    district = intent["district"]

    sql = f"""
SELECT date, district, SUM({metric}) AS {metric}
FROM local_life_metrics
WHERE city = '{city}'
  AND district = '{district}'
GROUP BY date, district
ORDER BY date;
""".strip()

    return sql
