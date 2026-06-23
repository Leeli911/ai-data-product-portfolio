"""运行十个确定性案例并输出结构化 Evaluation 报告。"""

import json
from pathlib import Path

from contracts import (
    CAUSAL_TERMS,
    AnalyticsRequest,
    AnalyticsResponse,
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationDimensionResult,
    EvaluationReport,
    EvaluationRequest,
    EvaluationSummary,
)
from pipeline import run_analytics
from plan_validator import REQUIRED_STEP_IDS


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CASES_PATH = PROJECT_ROOT / "evaluation_cases.json"
DEFAULT_JSON_REPORT_PATH = PROJECT_ROOT / "evaluation_results.json"
DEFAULT_MARKDOWN_REPORT_PATH = PROJECT_ROOT / "evaluation_summary.md"
DIMENSION_NAMES = (
    "intent_correctness",
    "plan_coverage",
    "sql_groundedness",
    "sql_executability",
    "insight_groundedness",
    "uncertainty_clarity",
)


def load_evaluation_cases(
    path: Path = DEFAULT_CASES_PATH,
) -> EvaluationRequest:
    """从 JSON 加载并校验 Evaluation cases。"""
    raw_cases = json.loads(Path(path).read_text(encoding="utf-8"))
    return EvaluationRequest(
        cases=[EvaluationCase.model_validate(item) for item in raw_cases]
    )


def _result(
    dimension: str,
    passed: bool,
    details: list[str],
) -> EvaluationDimensionResult:
    """统一生成 0/1 维度分数和说明。"""
    return EvaluationDimensionResult(
        dimension=dimension,
        passed=passed,
        score=1.0 if passed else 0.0,
        details=details,
    )


def _classify_outcome(
    case: EvaluationCase,
    response: AnalyticsResponse,
) -> str:
    """把 Pipeline 状态转换为案例预期使用的结果类别。"""
    if response.status == "success":
        return "success"
    error_code = response.error.error_code if response.error else ""
    if error_code == "INTENT_AMBIGUOUS":
        return "ambiguous"
    if (
        case.category == "adversarial"
        and error_code == "INTENT_UNSUPPORTED"
    ):
        return "rejected"
    if error_code == "INTENT_UNSUPPORTED":
        return "unsupported"
    return "failed"


def _intent_correctness(
    case: EvaluationCase,
    response: AnalyticsResponse,
) -> EvaluationDimensionResult:
    """比较预期和实际 Intent 字段。"""
    if response.intent is None:
        return _result(
            "intent_correctness",
            False,
            ["Pipeline 未返回 IntentResult。"],
        )
    comparisons = {
        "intent_type": (
            case.expected_intent_type,
            response.intent.intent_type,
        ),
        "metric": (case.expected_metric, response.intent.metric),
        "district": (case.expected_district, response.intent.district),
        "time_range": (
            case.expected_time_range,
            response.intent.time_range,
        ),
    }
    mismatches = [
        f"{name}: expected={expected}, actual={actual}"
        for name, (expected, actual) in comparisons.items()
        if expected != actual
    ]
    return _result(
        "intent_correctness",
        not mismatches,
        mismatches or ["Intent 关键字段与预期一致。"],
    )


def _negative_stop_result(
    dimension: str,
    case: EvaluationCase,
    actual_outcome: str,
    artifact_absent: bool,
) -> EvaluationDimensionResult:
    """负向案例在预期边界停止时，不因缺少下游产物扣分。"""
    passed = (
        actual_outcome == case.expected_outcome
        and artifact_absent
    )
    if passed:
        details = [
            f"案例按预期返回 {actual_outcome}，未生成不应存在的下游产物。"
        ]
    else:
        details = [
            f"预期 {case.expected_outcome}，实际 {actual_outcome}，"
            f"下游产物为空={artifact_absent}。"
        ]
    return _result(dimension, passed, details)


def _plan_coverage(
    case: EvaluationCase,
    response: AnalyticsResponse,
    actual_outcome: str,
) -> EvaluationDimensionResult:
    """成功案例检查三步计划，负向案例检查是否正确停止。"""
    if case.expected_outcome != "success":
        return _negative_stop_result(
            "plan_coverage",
            case,
            actual_outcome,
            response.plan is None,
        )
    actual_steps = (
        {step.step_id for step in response.plan.steps}
        if response.plan
        else set()
    )
    missing = set(REQUIRED_STEP_IDS) - actual_steps
    return _result(
        "plan_coverage",
        not missing,
        (
            ["Plan 覆盖三条必需分析路径。"]
            if not missing
            else [f"缺少分析步骤：{', '.join(sorted(missing))}"]
        ),
    )


def _sql_groundedness(
    case: EvaluationCase,
    response: AnalyticsResponse,
    actual_outcome: str,
) -> EvaluationDimensionResult:
    """成功案例检查独立 Validator，负向案例检查没有生成 SQL。"""
    if case.expected_outcome != "success":
        return _negative_stop_result(
            "sql_groundedness",
            case,
            actual_outcome,
            not response.generated_queries and not response.sql_validations,
        )
    passed = (
        bool(response.generated_queries)
        and len(response.generated_queries) == len(response.sql_validations)
        and all(item.is_valid for item in response.sql_validations)
    )
    details = (
        ["所有候选 SQL 均通过独立 Schema Validator。"]
        if passed
        else ["存在未校验、校验失败或数量不一致的 SQL。"]
    )
    return _result("sql_groundedness", passed, details)


def _sql_executability(
    case: EvaluationCase,
    response: AnalyticsResponse,
    actual_outcome: str,
) -> EvaluationDimensionResult:
    """成功案例检查真实结果非空，负向案例检查没有执行查询。"""
    if case.expected_outcome != "success":
        return _negative_stop_result(
            "sql_executability",
            case,
            actual_outcome,
            not response.query_results,
        )
    passed = (
        len(response.query_results) == len(response.generated_queries)
        and bool(response.query_results)
        and all(result.row_count > 0 for result in response.query_results)
    )
    details = (
        ["所有必需查询均在 DuckDB 返回非空结果。"]
        if passed
        else ["存在缺失、失败或空查询结果。"]
    )
    return _result("sql_executability", passed, details)


def _insight_groundedness(
    case: EvaluationCase,
    response: AnalyticsResponse,
    actual_outcome: str,
) -> EvaluationDimensionResult:
    """检查 Interpretation 的 Fact 引用和非因果措辞。"""
    if case.expected_outcome != "success":
        return _negative_stop_result(
            "insight_groundedness",
            case,
            actual_outcome,
            response.insight is None,
        )
    if response.insight is None:
        return _result(
            "insight_groundedness",
            False,
            ["成功案例未返回 InsightResult。"],
        )
    fact_ids = {fact.fact_id for fact in response.insight.facts}
    links_valid = bool(response.insight.interpretations) and all(
        bool(item.supporting_fact_ids)
        and set(item.supporting_fact_ids) <= fact_ids
        for item in response.insight.interpretations
    )
    causal_hits = [
        term
        for item in response.insight.interpretations
        for term in CAUSAL_TERMS
        if term in item.statement
    ]
    passed = bool(fact_ids) and links_valid and not causal_hits
    details = (
        ["所有 Interpretation 均绑定有效 Fact，且没有因果措辞。"]
        if passed
        else [f"Fact 绑定有效={links_valid}，因果禁词={causal_hits}。"]
    )
    return _result("insight_groundedness", passed, details)


def _uncertainty_clarity(
    case: EvaluationCase,
    response: AnalyticsResponse,
    actual_outcome: str,
) -> EvaluationDimensionResult:
    """检查相关性边界和缺失外部数据是否明确。"""
    if case.expected_outcome != "success":
        return _negative_stop_result(
            "uncertainty_clarity",
            case,
            actual_outcome,
            response.insight is None,
        )
    if response.insight is None:
        return _result(
            "uncertainty_clarity",
            False,
            ["成功案例未返回 Limitation。"],
        )
    statements = " ".join(
        limitation.statement for limitation in response.insight.limitations
    )
    has_correlation_boundary = (
        "相关性" in statements and "不能证明因果" in statements
    )
    has_missing_data = any(
        limitation.missing_data
        for limitation in response.insight.limitations
    )
    passed = has_correlation_boundary and has_missing_data
    details = (
        ["Limitation 同时说明相关性边界和缺失外部数据。"]
        if passed
        else [
            f"相关性边界={has_correlation_boundary}，"
            f"缺失数据说明={has_missing_data}。"
        ]
    )
    return _result("uncertainty_clarity", passed, details)


def _evaluate_case(case: EvaluationCase) -> EvaluationCaseResult:
    """运行一个案例并生成六维结构化结果。"""
    response = run_analytics(AnalyticsRequest(question=case.question))
    actual_outcome = _classify_outcome(case, response)
    dimensions = [
        _intent_correctness(case, response),
        _plan_coverage(case, response, actual_outcome),
        _sql_groundedness(case, response, actual_outcome),
        _sql_executability(case, response, actual_outcome),
        _insight_groundedness(case, response, actual_outcome),
        _uncertainty_clarity(case, response, actual_outcome),
    ]
    passed = (
        actual_outcome == case.expected_outcome
        and all(dimension.passed for dimension in dimensions)
    )
    return EvaluationCaseResult(
        case_id=case.case_id,
        question=case.question,
        expected_outcome=case.expected_outcome,
        actual_outcome=actual_outcome,
        dimensions=dimensions,
        passed=passed,
    )


def run_evaluation(request: EvaluationRequest) -> EvaluationReport:
    """运行全部案例并聚合案例与维度通过率。"""
    case_results = [_evaluate_case(case) for case in request.cases]
    total_cases = len(case_results)
    passed_cases = sum(case.passed for case in case_results)
    dimension_pass_rates = {
        dimension: round(
            sum(
                next(
                    item.passed
                    for item in case.dimensions
                    if item.dimension == dimension
                )
                for case in case_results
            )
            / total_cases
            * 100,
            1,
        )
        for dimension in DIMENSION_NAMES
    }
    return EvaluationReport(
        summary=EvaluationSummary(
            total_cases=total_cases,
            passed_cases=passed_cases,
            case_pass_rate=round(passed_cases / total_cases * 100, 1),
            dimension_pass_rates=dimension_pass_rates,
        ),
        cases=case_results,
    )


def write_json_report(report: EvaluationReport, path: Path) -> None:
    """输出完整机器可读 JSON report。"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def write_markdown_summary(report: EvaluationReport, path: Path) -> None:
    """输出包含通过率、案例结果和失败原因的 Markdown summary。"""
    lines = [
        "# Text2Analytics Evaluation Summary",
        "",
        f"- Total cases: {report.summary.total_cases}",
        f"- Passed cases: {report.summary.passed_cases}",
        f"- Case pass rate: {report.summary.case_pass_rate:.1f}%",
        "",
        "## Dimension Pass Rates",
        "",
        "| Dimension | Pass Rate |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {dimension} | {pass_rate:.1f}% |"
        for dimension, pass_rate in report.summary.dimension_pass_rates.items()
    )
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| Case | Expected | Actual | Passed |",
            "|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {case.case_id} | {case.expected_outcome} | "
        f"{case.actual_outcome} | {'yes' if case.passed else 'no'} |"
        for case in report.cases
    )
    lines.extend(["", "## Failed Cases", ""])
    failed_cases = [case for case in report.cases if not case.passed]
    if not failed_cases:
        lines.append("无。")
    else:
        for case in failed_cases:
            lines.append(f"### {case.case_id}")
            lines.append("")
            for dimension in case.dimensions:
                if not dimension.passed:
                    lines.append(
                        f"- {dimension.dimension}: {'; '.join(dimension.details)}"
                    )
            lines.append("")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """运行默认十案例并生成两份报告。"""
    report = run_evaluation(load_evaluation_cases())
    write_json_report(report, DEFAULT_JSON_REPORT_PATH)
    write_markdown_summary(report, DEFAULT_MARKDOWN_REPORT_PATH)
    print(
        f"Evaluation complete: {report.summary.passed_cases}/"
        f"{report.summary.total_cases} cases passed"
    )


if __name__ == "__main__":
    main()
