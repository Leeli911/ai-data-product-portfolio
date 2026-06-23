from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import run_analysis_workflow
from contracts import AnalyticsResponse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"
README_PATH = PROJECT_ROOT / "README.md"


def test_run_analysis_workflow_returns_typed_pipeline_response():
    """页面入口只调用 Pipeline，并返回完整 AnalyticsResponse。"""
    result = run_analysis_workflow("为什么北京朝阳区本周 GMV 下滑？")

    assert isinstance(result, AnalyticsResponse)
    assert result.status == "success"
    assert len(result.generated_queries) == 3
    assert len(result.query_results) == 3
    assert len(result.insight.facts) == 6
    assert result.confidence.score == 0.90


def test_app_source_is_presentation_only():
    """Streamlit 文件不得重新实现旧分析逻辑或业务计算。"""
    source = APP_PATH.read_text(encoding="utf-8")
    forbidden_details = [
        "from analytics import",
        "from evaluator import",
        "from parser import",
        "from sql_generator import",
        "calculate_change_rate",
        "SUM(",
        "BASE_CONFIDENCE",
    ]

    assert "from pipeline import run_analytics" in source
    assert not any(detail in source for detail in forbidden_details)


def test_streamlit_displays_complete_golden_path():
    """点击分析后应展示用户要求的九层黄金链路。"""
    app = AppTest.from_file(str(APP_PATH)).run(timeout=15)
    app.button[0].click().run(timeout=30)

    assert not app.exception
    headings = {item.value for item in app.header}
    assert {
        "1. Question",
        "2. Intent Understanding",
        "3. Analysis Plan",
        "4. SQL Queries",
        "5. Query Results",
        "6. Facts",
        "7. Interpretations",
        "8. Limitations",
        "9. Confidence",
    } <= headings
    assert any("0.90" in item.value for item in app.metric)


def test_streamlit_displays_structured_failed_response():
    """超范围问题应在页面明确展示失败阶段、代码和说明。"""
    app = AppTest.from_file(str(APP_PATH)).run(timeout=15)
    app.text_input[0].input("分析北京朝阳区本周转化漏斗")
    app.button[0].click().run(timeout=15)

    assert not app.exception
    assert app.error
    error_text = app.error[0].value
    assert "INTENT_UNSUPPORTED" in error_text
    assert "intent" in error_text


def test_readme_has_research_portfolio_structure_and_evaluation_caveat():
    """README 必须完整包装研究价值，同时禁止夸大 100% 结果。"""
    readme = README_PATH.read_text(encoding="utf-8")
    required_headings = [
        "# Text2Analytics: An Evidence-based Analytics System for Decision Support",
        "## Why Text2SQL Is Not Enough",
        "## Project Motivation",
        "## System Architecture",
        "## Golden Use Case",
        "## Type-safe Pipeline",
        "## Schema Grounding and SQL Guardrails",
        "## Fact / Interpretation / Limitation",
        "## Confidence as Evidence Completeness",
        "## Evaluation Framework",
        "## Limitations",
        "## Research Relevance",
        "## Reproducibility",
    ]

    assert all(heading in readme for heading in required_headings)
    assert "controlled deterministic evaluation" in readme
    assert "100% 通过率不代表系统可以泛化到任意业务问题" in readme
    assert "一个黄金场景和少量等价表达" in readme
    assert "更多数据集、更宽的问题类型和更真实的用户评测" in readme
