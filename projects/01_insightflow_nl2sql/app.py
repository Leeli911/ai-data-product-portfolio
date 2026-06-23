"""Text2Analytics Streamlit 展示入口。"""

from contracts import AnalyticsRequest, AnalyticsResponse
from pipeline import run_analytics


DEFAULT_QUESTION = "为什么北京朝阳区本周 GMV 下滑？"


def run_analysis_workflow(query: str) -> AnalyticsResponse:
    """把页面输入转换为类型化请求，并交给 Pipeline 处理。"""
    return run_analytics(AnalyticsRequest(question=query))


def _render_failed_response(st, response: AnalyticsResponse) -> None:
    """展示失败阶段、错误代码和已完成阶段。"""
    error = response.error
    if error is None:
        st.error("unknown | UNKNOWN_ERROR: Pipeline 未返回错误详情。")
        return

    st.error(
        f"{error.failed_stage} | {error.error_code}: {error.message}"
    )
    st.caption(
        "Completed stages: "
        + (" → ".join(response.completed_stages) or "none")
    )
    if response.intent is not None:
        st.subheader("Intent at failure")
        st.json(response.intent.model_dump())


def _render_intent(st, response: AnalyticsResponse) -> None:
    st.header("2. Intent Understanding")
    st.json(response.intent.model_dump())


def _render_plan(st, response: AnalyticsResponse) -> None:
    st.header("3. Analysis Plan")
    plan_rows = [
        {
            "step_id": step.step_id,
            "goal": step.goal,
            "required_metrics": ", ".join(step.required_metrics),
            "group_by": ", ".join(step.group_by),
        }
        for step in response.plan.steps
    ]
    st.dataframe(plan_rows, use_container_width=True, hide_index=True)


def _render_queries(st, response: AnalyticsResponse) -> None:
    st.header("4. SQL Queries")
    for query, validation in zip(
        response.generated_queries,
        response.sql_validations,
        strict=True,
    ):
        st.subheader(query.purpose)
        st.caption(
            f"step_id={query.step_id} | validated={validation.is_valid}"
        )
        st.code(query.sql, language="sql")


def _render_results(st, response: AnalyticsResponse) -> None:
    st.header("5. Query Results")
    for result in response.query_results:
        st.subheader(result.step_id)
        st.caption(f"Rows: {result.row_count}")
        st.dataframe(result.rows, use_container_width=True, hide_index=True)


def _render_facts(st, response: AnalyticsResponse) -> None:
    st.header("6. Facts")
    fact_rows = [
        {
            "metric": fact.metric_label,
            "current": fact.current_value,
            "previous": fact.previous_value,
            "change_rate": fact.change_rate,
            "unit": fact.unit,
            "source_step_id": fact.source_step_id,
            "statement": fact.statement,
        }
        for fact in response.insight.facts
    ]
    st.dataframe(fact_rows, use_container_width=True, hide_index=True)


def _render_interpretations(st, response: AnalyticsResponse) -> None:
    st.header("7. Interpretations")
    for interpretation in response.insight.interpretations:
        st.subheader(interpretation.reasoning_type)
        st.write(interpretation.statement)
        st.caption(
            "Evidence: " + ", ".join(interpretation.supporting_fact_ids)
        )


def _render_limitations(st, response: AnalyticsResponse) -> None:
    st.header("8. Limitations")
    for limitation in response.insight.limitations:
        st.warning(limitation.statement)
        st.caption(f"Impact: {limitation.impact}")
        if limitation.missing_data:
            st.caption("Missing data: " + ", ".join(limitation.missing_data))


def _render_confidence(st, response: AnalyticsResponse) -> None:
    st.header("9. Confidence")
    st.metric(
        "Evidence completeness",
        f"{response.confidence.score:.2f}",
    )
    st.caption(
        "This score describes evidence completeness, not the probability "
        "that the conclusion is true."
    )
    factor_rows = [
        {
            "name": factor.name,
            "impact": factor.impact,
            "reason": factor.reason,
        }
        for factor in response.confidence.factors
    ]
    st.dataframe(factor_rows, use_container_width=True, hide_index=True)


def _render_success_response(st, response: AnalyticsResponse) -> None:
    """按黄金链路顺序展示成功响应的全部证据层。"""
    _render_intent(st, response)
    _render_plan(st, response)
    _render_queries(st, response)
    _render_results(st, response)
    _render_facts(st, response)
    _render_interpretations(st, response)
    _render_limitations(st, response)
    _render_confidence(st, response)


def main() -> None:
    """启动只负责输入和结果展示的 Streamlit 页面。"""
    import streamlit as st

    st.set_page_config(
        page_title="Text2Analytics",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.title("Text2Analytics")
    st.caption("An Evidence-based Analytics System for Decision Support")
    st.write(
        "A deterministic research-portfolio MVP that makes analytical "
        "planning, SQL, evidence, uncertainty, and confidence inspectable."
    )

    st.header("1. Question")
    question = st.text_input(
        "Business question",
        DEFAULT_QUESTION,
        help="Phase 1 supports one controlled GMV-drop scenario and close paraphrases.",
    )
    should_run = st.button(
        "Run evidence-based analysis",
        type="primary",
        use_container_width=True,
    )

    if not should_run:
        st.info("Submit the default golden question to inspect the full pipeline.")
        return

    response = run_analysis_workflow(question)
    st.caption(f"Status: {response.status}")
    if response.status != "success":
        _render_failed_response(st, response)
        return

    _render_success_response(st, response)


if __name__ == "__main__":
    main()
