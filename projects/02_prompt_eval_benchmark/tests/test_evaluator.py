from pathlib import Path
import csv
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from evaluator import (  # noqa: E402
    evaluate_all_versions,
    evaluate_prompt_version,
    load_benchmark,
    simulate_prompt_output,
)


BENCHMARK_PATH = PROJECT_ROOT / "benchmark_queries.csv"
RESULT_FIELDS = {
    "prompt_version",
    "metric_accuracy",
    "district_accuracy",
    "task_accuracy",
    "overall_accuracy",
    "hallucination_rate",
}


def test_load_benchmark_reads_at_least_20_queries():
    """测试 benchmark 文件至少包含 20 条中文业务问题。"""
    rows = load_benchmark(BENCHMARK_PATH)

    assert len(rows) >= 20
    assert {"query", "expected_metric", "expected_district", "expected_task"}.issubset(
        rows[0].keys()
    )


def test_simulate_prompt_output_returns_required_fields():
    """测试模拟 prompt 输出必须包含 metric、district、task。"""
    output = simulate_prompt_output("为什么北京朝阳区本周 GMV 下滑？", "V3")

    assert set(output.keys()) == {"metric", "district", "task"}


def test_all_prompt_versions_return_result_fields_and_valid_rates():
    """测试 V1、V2、V3 都能输出完整评测指标，且指标范围在 0 到 1。"""
    rows = load_benchmark(BENCHMARK_PATH)

    for version in ["V1", "V2", "V3"]:
        result = evaluate_prompt_version(rows, version)

        assert RESULT_FIELDS.issubset(result.keys())
        assert result["prompt_version"] == version

        for field in RESULT_FIELDS - {"prompt_version"}:
            assert 0 <= result[field] <= 1


def test_v3_accuracy_and_hallucination_are_not_worse_than_v1():
    """测试 V3 相比 V1 至少不降低整体准确率，且不增加 hallucination。"""
    rows = load_benchmark(BENCHMARK_PATH)
    v1_result = evaluate_prompt_version(rows, "V1")
    v3_result = evaluate_prompt_version(rows, "V3")

    assert v3_result["overall_accuracy"] >= v1_result["overall_accuracy"]
    assert v3_result["hallucination_rate"] <= v1_result["hallucination_rate"]


def test_evaluate_all_versions_generates_results_csv(tmp_path):
    """测试 evaluate_all_versions 能由程序生成包含三版 prompt 的 results.csv。"""
    output_path = tmp_path / "results.csv"

    results = evaluate_all_versions(BENCHMARK_PATH, output_path)

    assert output_path.exists()
    assert [row["prompt_version"] for row in results] == ["V1", "V2", "V3"]

    with output_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        saved_rows = list(reader)

    assert reader.fieldnames == [
        "prompt_version",
        "metric_accuracy",
        "district_accuracy",
        "task_accuracy",
        "overall_accuracy",
        "hallucination_rate",
    ]
    assert len(saved_rows) == 3
