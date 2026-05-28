from pathlib import Path

from evaluator import evaluate_parser


BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "benchmark_queries.csv"


def test_evaluate_parser_returns_accuracy_metrics():
    """测试 parser 评测结果是否包含稳定的准确率字段。"""
    result = evaluate_parser(BENCHMARK_PATH)

    assert result["total_queries"] == 5
    assert result["metric_accuracy"] == 1.0
    assert result["district_accuracy"] == 1.0
    assert result["task_accuracy"] == 1.0
    assert result["overall_accuracy"] == 1.0
