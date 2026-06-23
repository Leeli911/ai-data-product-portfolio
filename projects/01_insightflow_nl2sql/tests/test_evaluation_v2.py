import json

import pytest

from evaluation import (
    DEFAULT_CASES_PATH,
    DIMENSION_NAMES,
    load_evaluation_cases,
    run_evaluation,
    write_json_report,
    write_markdown_summary,
)


@pytest.fixture(scope="module")
def evaluation_request():
    """加载 Phase 5 的十个类型化案例。"""
    return load_evaluation_cases(DEFAULT_CASES_PATH)


@pytest.fixture(scope="module")
def evaluation_report(evaluation_request):
    """只运行一次真实 Pipeline Evaluation，供测试复用。"""
    return run_evaluation(evaluation_request)


def test_loads_exactly_ten_cases_in_required_categories(evaluation_request):
    """第一版必须保持 4+2+2+2 的最小案例结构。"""
    cases = evaluation_request.cases
    category_counts = {
        category: sum(case.category == category for case in cases)
        for category in {case.category for case in cases}
    }

    assert len(cases) == 10
    assert len({case.case_id for case in cases}) == 10
    assert category_counts == {
        "success": 4,
        "ambiguous": 2,
        "unsupported": 2,
        "adversarial": 2,
    }


def test_report_contains_six_structured_dimensions_per_case(evaluation_report):
    """每个案例都要保留各维度 pass、score 和 details。"""
    assert evaluation_report.summary.total_cases == 10
    assert len(evaluation_report.cases) == 10

    for case_result in evaluation_report.cases:
        assert {item.dimension for item in case_result.dimensions} == set(
            DIMENSION_NAMES
        )
        assert all(isinstance(item.passed, bool) for item in case_result.dimensions)
        assert all(0.0 <= item.score <= 1.0 for item in case_result.dimensions)
        assert all(item.details for item in case_result.dimensions)


def test_success_cases_pass_all_grounding_checks(evaluation_report):
    """黄金等价表达必须通过 Intent、Plan、SQL、结果和证据检查。"""
    success_results = [
        case for case in evaluation_report.cases
        if case.expected_outcome == "success"
    ]

    assert len(success_results) == 4
    assert all(case.actual_outcome == "success" for case in success_results)
    assert all(case.passed for case in success_results)
    assert all(
        dimension.passed
        for case in success_results
        for dimension in case.dimensions
    )


def test_negative_cases_pass_when_pipeline_stops_at_expected_boundary(
    evaluation_report,
):
    """负向案例没有 SQL 或 Insight 是正确行为，不应自动计为失败。"""
    negative_results = [
        case for case in evaluation_report.cases
        if case.expected_outcome != "success"
    ]

    assert len(negative_results) == 6
    assert all(case.actual_outcome == case.expected_outcome for case in negative_results)
    assert all(case.passed for case in negative_results)
    assert all(
        dimension.passed
        for case in negative_results
        for dimension in case.dimensions
    )


def test_writes_json_report_and_markdown_summary(
    tmp_path,
    evaluation_report,
):
    """Evaluation 必须同时提供机器可读与作品集可读产物。"""
    json_path = tmp_path / "evaluation_results.json"
    markdown_path = tmp_path / "evaluation_summary.md"

    write_json_report(evaluation_report, json_path)
    write_markdown_summary(evaluation_report, markdown_path)

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert loaded["summary"]["total_cases"] == 10
    assert len(loaded["cases"]) == 10
    assert "## Dimension Pass Rates" in markdown
    assert "## Case Results" in markdown
    assert "## Failed Cases" in markdown
    assert "intent_correctness" in markdown
