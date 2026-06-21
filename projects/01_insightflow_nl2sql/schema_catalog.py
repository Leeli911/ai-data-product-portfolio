"""InsightFlow v2 的稳定业务 schema 定义。"""


TIME_WINDOW_POLICY = {
    "anchor": "max_data_date",
    "current_period_days": 7,
    "previous_period_days": 7,
    "current_period_definition": "数据集中最新日期及之前 6 天",
    "previous_period_definition": "本周之前连续 7 天",
}


SCHEMA_CATALOG = {
    "fact_orders": {
        "description": "按日期和区域记录本地生活业务的交易与用户指标。",
        "grain": "日期 × 区域",
        "primary_key": ["order_date", "district_id"],
        "foreign_keys": {
            "district_id": "dim_district.district_id",
        },
        "columns": {
            "order_date": {
                "description": "订单经营日期。",
                "semantic_type": "time",
                "aliases": ["日期", "下单日期", "经营日期"],
            },
            "district_id": {
                "description": "订单所属区域的稳定标识。",
                "semantic_type": "identifier",
                "aliases": ["区域ID", "行政区ID"],
            },
            "gmv": {
                "description": "订单交易金额，不扣除退款和优惠成本。",
                "semantic_type": "metric",
                "aliases": ["GMV", "交易额", "销售额"],
            },
            "orders": {
                "description": "完成交易的订单数量。",
                "semantic_type": "metric",
                "aliases": ["订单", "订单量"],
            },
            "active_users": {
                "description": "当日产生交易行为的活跃用户数。",
                "semantic_type": "metric",
                "aliases": ["用户", "用户数", "活跃用户"],
            },
            "peak_orders": {
                "description": "业务高峰时段内完成的订单数量。",
                "semantic_type": "metric",
                "aliases": ["高峰订单", "高峰期订单"],
            },
        },
    },
    "dim_district": {
        "description": "维护区域与城市的中英文名称及稳定标识。",
        "grain": "区域",
        "primary_key": ["district_id"],
        "foreign_keys": {},
        "columns": {
            "district_id": {
                "description": "区域的稳定主键。",
                "semantic_type": "identifier",
                "aliases": ["区域ID", "行政区ID"],
            },
            "district_name_zh": {
                "description": "区域中文名称。",
                "semantic_type": "dimension",
                "aliases": ["区域", "地区", "行政区"],
            },
            "district_name_en": {
                "description": "区域英文名称。",
                "semantic_type": "dimension",
                "aliases": ["区域英文名"],
            },
            "city_name_zh": {
                "description": "城市中文名称。",
                "semantic_type": "dimension",
                "aliases": ["城市", "市"],
            },
            "city_name_en": {
                "description": "城市英文名称。",
                "semantic_type": "dimension",
                "aliases": ["城市英文名"],
            },
        },
    },
    "fact_marketing_cost": {
        "description": "按日期和区域记录本地生活业务的优惠券投入。",
        "grain": "日期 × 区域",
        "primary_key": ["cost_date", "district_id"],
        "foreign_keys": {
            "district_id": "dim_district.district_id",
        },
        "columns": {
            "cost_date": {
                "description": "营销成本发生日期。",
                "semantic_type": "time",
                "aliases": ["日期", "成本日期", "投放日期"],
            },
            "district_id": {
                "description": "营销成本所属区域的稳定标识。",
                "semantic_type": "identifier",
                "aliases": ["区域ID", "行政区ID"],
            },
            "coupon_cost": {
                "description": "核销优惠券对应的营销成本。",
                "semantic_type": "metric",
                "aliases": ["优惠券成本", "券成本", "补贴成本"],
            },
        },
    },
}
