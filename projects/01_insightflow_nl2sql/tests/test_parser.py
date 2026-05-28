from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from parser import parse_query


def test_parse_chaoyang_gmv_drop_query():
    """测试典型 GMV 下滑问题是否能解析为归因分析意图。"""
    query = "为什么北京朝阳区本周 GMV 下滑？"

    result = parse_query(query)

    assert result["metric"] == "gmv"
    assert result["city"] == "Beijing"
    assert result["district"] == "Chaoyang"
    assert result["task"] == "root_cause_analysis"
    assert result["time_range"] == "this_week"


def test_parse_haidian_orders_rise_query():
    """测试订单上涨问题是否能识别指标、区域和归因分析任务。"""
    query = "海淀区订单为什么上涨？"

    result = parse_query(query)

    assert result["metric"] == "orders"
    assert result["district"] == "Haidian"
    assert result["task"] == "root_cause_analysis"


def test_parse_this_week_users_trend_query():
    """测试用户数变化问题是否能识别为趋势分析任务。"""
    query = "本周用户数变化如何？"

    result = parse_query(query)

    assert result["metric"] == "users"
    assert result["time_range"] == "this_week"
    assert result["task"] == "trend_analysis"
