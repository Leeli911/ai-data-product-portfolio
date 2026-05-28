"""Parser 评测模块。"""

from pathlib import Path

import pandas as pd

from parser import parse_query


DEFAULT_BENCHMARK_PATH = Path(__file__).resolve().parent / "benchmark_queries.csv"


def calculate_accuracy(correct_count, total_count):
    """计算准确率，统一返回 0 到 1 的小数。"""
    if total_count == 0:
        return 0.0
    return round(correct_count / total_count, 3)


def evaluate_parser(benchmark_path=DEFAULT_BENCHMARK_PATH):
    """读取 benchmark 文件，计算 parser 的各项准确率。"""
    df = pd.read_csv(benchmark_path)

    total_count = len(df)
    metric_correct = 0
    district_correct = 0
    task_correct = 0
    overall_correct = 0

    for _, row in df.iterrows():
        parsed = parse_query(row["query"])

        metric_ok = parsed["metric"] == row["expected_metric"]
        district_ok = parsed["district"] == row["expected_district"]
        task_ok = parsed["task"] == row["expected_task"]

        metric_correct += int(metric_ok)
        district_correct += int(district_ok)
        task_correct += int(task_ok)
        overall_correct += int(metric_ok and district_ok and task_ok)

    return {
        "total_queries": total_count,
        "metric_accuracy": calculate_accuracy(metric_correct, total_count),
        "district_accuracy": calculate_accuracy(district_correct, total_count),
        "task_accuracy": calculate_accuracy(task_correct, total_count),
        "overall_accuracy": calculate_accuracy(overall_correct, total_count),
    }


if __name__ == "__main__":
    print(evaluate_parser())
