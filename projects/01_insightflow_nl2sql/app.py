"""InsightFlow Streamlit 应用入口。"""

from analytics import analyze_metrics
from evaluator import evaluate_parser
from parser import parse_query
from sql_generator import generate_sql


def run_analysis_workflow(query):
    """串联问题解析、SQL 生成、数据分析和业务诊断。"""
    parsed_intent = parse_query(query)
    generated_sql = generate_sql(parsed_intent)
    analysis_result = analyze_metrics(parsed_intent)
    business_diagnosis = f"业务诊断：{analysis_result['diagnosis']}"

    return {
        "parsed_intent": parsed_intent,
        "generated_sql": generated_sql,
        "analysis_result": analysis_result,
        "business_diagnosis": business_diagnosis,
    }


def main():
    """启动 Streamlit 页面并展示完整分析流程。"""
    import streamlit as st

    st.set_page_config(
        page_title="InsightFlow",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("InsightFlow")
    st.caption("AI-Powered Intelligent Analytics Copilot")
    st.write("模拟 AI 数据产品中的智能问数与自动归因分析 workflow")

    st.divider()

    st.header("模块1：用户输入问题")
    left_col, right_col = st.columns([2, 1])
    with left_col:
        user_query = st.text_input(
            "业务问题",
            "为什么北京朝阳区本周 GMV 下滑？",
            help="输入一个中文经营分析问题，系统会模拟完成 intent parsing、SQL 生成和归因诊断。",
        )
    with right_col:
        st.metric("Demo 数据范围", "北京 / 朝阳区")
        st.metric("分析粒度", "本周 vs 上周")

    should_run = st.button("开始分析", type="primary", use_container_width=True)

    if should_run:
        result = run_analysis_workflow(user_query)

        st.divider()

        st.header("模块2：Intent Parsing")
        st.write("将中文业务问题解析为结构化分析意图，明确指标、城市、区域、任务类型和时间范围。")
        st.json(result["parsed_intent"])

        st.header("模块3：Generated SQL")
        st.write("根据结构化 intent 生成可读的 SQL，展示自然语言到取数逻辑的转换过程。")
        st.code(result["generated_sql"], language="sql")

        st.header("模块4：Analysis & Diagnosis")
        metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
        analysis = result["analysis_result"]
        metric_col_1.metric("本周 GMV", f"{analysis['this_week_gmv']:,}")
        metric_col_2.metric("上周 GMV", f"{analysis['last_week_gmv']:,}")
        metric_col_3.metric("GMV 环比", f"{analysis['gmv_change_rate']}%")

        st.subheader("分析结果")
        st.json(analysis)

        st.subheader("业务诊断")
        st.info(result["business_diagnosis"])

        with st.expander("Parser Benchmark 结果"):
            st.json(evaluate_parser())


if __name__ == "__main__":
    main()
