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

    st.set_page_config(page_title="InsightFlow", layout="wide")
    st.title("InsightFlow 智能问数与自动诊断")

    user_query = st.text_input(
        "请输入业务问题",
        "为什么北京朝阳区本周 GMV 下滑？",
    )

    if st.button("开始分析"):
        result = run_analysis_workflow(user_query)

        st.subheader("1. 结构化解析结果")
        st.json(result["parsed_intent"])

        st.subheader("2. 生成 SQL")
        st.code(result["generated_sql"], language="sql")

        st.subheader("3. 分析结果")
        st.json(result["analysis_result"])

        st.subheader("4. 业务诊断建议")
        st.write(result["business_diagnosis"])

        st.subheader("5. Parser 评测结果")
        st.json(evaluate_parser())


if __name__ == "__main__":
    main()
