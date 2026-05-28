"""中文业务问题解析模块。"""


def detect_metric(query):
    """根据中文关键词识别用户关注的业务指标。"""
    if "GMV" in query or "gmv" in query or "销售额" in query:
        return "gmv"
    if "订单" in query or "订单量" in query:
        return "orders"
    if "用户" in query or "用户数" in query:
        return "users"
    if "客单价" in query:
        return "aov"
    return "unknown"


def detect_city(query):
    """根据中文关键词识别城市，默认只支持北京。"""
    if "北京" in query:
        return "Beijing"
    return "Beijing"


def detect_district(query):
    """根据中文关键词识别区域。"""
    if "朝阳" in query or "朝阳区" in query:
        return "Chaoyang"
    if "海淀" in query or "海淀区" in query:
        return "Haidian"
    return "unknown"


def detect_time_range(query):
    """根据中文关键词识别时间范围。"""
    if "本周" in query:
        return "this_week"
    if "上周" in query:
        return "last_week"
    return "unknown"


def detect_task(query):
    """根据问题表达识别分析任务类型。"""
    root_cause_keywords = ["为什么", "下降", "下滑", "上涨", "上升"]
    trend_keywords = ["变化", "趋势", "如何"]

    if any(keyword in query for keyword in root_cause_keywords):
        return "root_cause_analysis"
    if any(keyword in query for keyword in trend_keywords):
        return "trend_analysis"
    return "trend_analysis"


def parse_query(query):
    """将中文业务问题解析成结构化分析意图。"""
    return {
        "metric": detect_metric(query),
        "city": detect_city(query),
        "district": detect_district(query),
        "task": detect_task(query),
        "time_range": detect_time_range(query),
    }
