"""Prompt 版本评测模块。

本模块不调用真实 LLM，而是用规则模拟不同 prompt 版本的解析效果。
目标是展示 Prompt Engineering 和 Evaluation Framework 的设计思路。
"""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_PATH = PROJECT_ROOT / "benchmark_queries.csv"
DEFAULT_RESULTS_PATH = PROJECT_ROOT / "results.csv"

PROMPT_VERSIONS = ["V1", "V2", "V3"]
RESULT_FIELDS = [
    "prompt_version",
    "metric_accuracy",
    "district_accuracy",
    "task_accuracy",
    "overall_accuracy",
    "hallucination_rate",
]

ALLOWED_METRICS = {"gmv", "orders", "users", "aov", "peak_orders", "coupon_cost"}
ALLOWED_DISTRICTS = {"Chaoyang", "Haidian", "Fengtai", "Pudong", "unknown"}
ALLOWED_TASKS = {
    "root_cause_analysis",
    "trend_analysis",
    "comparison_analysis",
    "impact_analysis",
}


def load_benchmark(path):
    """读取 benchmark query 文件。"""
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def contains_any(query, keywords):
    """判断 query 是否包含任意关键词。"""
    return any(keyword in query for keyword in keywords)


def detect_metric_v1(query):
    """模拟基础 prompt 对指标的识别能力。"""
    if "GMV" in query or "gmv" in query:
        return "gmv"
    if "订单" in query:
        return "orders"
    if "用户" in query:
        return "users"
    if "客单价" in query:
        return "aov"
    if "优惠券" in query:
        return "coupon"
    if "高峰" in query:
        return "peak"
    return "unknown_metric"


def detect_district_v1(query):
    """模拟基础 prompt 对地区的识别能力。"""
    if "朝阳" in query:
        return "Chaoyang"
    if "海淀" in query:
        return "Haidian"
    if "丰台" in query:
        return "FengtaiDistrict"
    if "浦东" in query:
        return "PudongNewArea"
    return "Beijing"


def detect_task_v1(query):
    """模拟基础 prompt 对任务类型的识别能力。"""
    if contains_any(query, ["哪个", "相比", "最高", "最多", "差距"]):
        return "ranking"
    if contains_any(query, ["是否", "影响", "导致", "拉动"]):
        return "impact"
    if contains_any(query, ["为什么", "原因", "下滑", "下降", "上涨", "上升"]):
        return "root_cause_analysis"
    if contains_any(query, ["变化", "趋势", "如何", "表现"]):
        return "trend_analysis"
    return "analysis"


def detect_metric_v2(query):
    """模拟 schema grounding 后的指标识别。"""
    if "GMV" in query or "gmv" in query or "销售额" in query:
        return "gmv"
    if "订单" in query:
        return "orders"
    if "用户" in query:
        return "users"
    if "客单价" in query:
        return "aov"
    if "优惠券" in query:
        return "coupon_cost"
    if "高峰" in query:
        return "peak_orders"
    return "gmv"


def detect_district_v2(query):
    """模拟 schema grounding 后的地区识别。"""
    if "朝阳" in query:
        return "Chaoyang"
    if "海淀" in query:
        return "Haidian"
    if "丰台" in query:
        return "Fengtai"
    if "浦东" in query:
        return "Pudong"
    return "unknown"


def detect_task_v2(query):
    """模拟 schema grounding 后的任务识别。"""
    if contains_any(query, ["哪个", "相比", "最高", "最多", "差距"]):
        return "comparison_analysis"
    if contains_any(query, ["为什么", "原因", "下滑", "下降", "上涨", "上升"]):
        return "root_cause_analysis"
    if contains_any(query, ["变化", "趋势", "如何", "表现"]):
        return "trend_analysis"
    if contains_any(query, ["是否", "影响", "导致", "拉动"]):
        return "root_cause_analysis"
    return "trend_analysis"


def detect_metric_v3(query):
    """模拟 few-shot 后对复杂表达和同义词的识别。"""
    if "优惠券" in query:
        return "coupon_cost"
    if "晚高峰" in query or "高峰期" in query or "高峰" in query:
        return "peak_orders"
    if "客单价" in query:
        return "aov"
    if "用户" in query:
        return "users"
    if "订单" in query:
        return "orders"
    if "GMV" in query or "gmv" in query or "销售额" in query:
        return "gmv"
    return "gmv"


def detect_district_v3(query):
    """模拟 few-shot 后对多地区 query 的识别，优先选择先出现的地区。"""
    district_keywords = [
        ("朝阳", "Chaoyang"),
        ("海淀", "Haidian"),
        ("丰台", "Fengtai"),
        ("浦东", "Pudong"),
    ]
    matches = []

    for keyword, district in district_keywords:
        index = query.find(keyword)
        if index >= 0:
            matches.append((index, district))

    if not matches:
        return "unknown"

    matches.sort(key=lambda item: item[0])
    return matches[0][1]


def detect_task_v3(query):
    """模拟 few-shot 后对任务类型的识别。"""
    if contains_any(query, ["是否", "影响", "导致", "拉动"]):
        return "impact_analysis"
    if contains_any(query, ["哪个", "相比", "最高", "最多", "差距"]):
        return "comparison_analysis"
    if contains_any(query, ["为什么", "原因", "下滑", "下降", "上涨", "上升"]):
        return "root_cause_analysis"
    if contains_any(query, ["变化", "趋势", "如何", "表现"]):
        return "trend_analysis"
    return "trend_analysis"


def simulate_prompt_output(query, prompt_version):
    """模拟不同 prompt 版本对 query 的结构化解析输出。"""
    if prompt_version == "V1":
        return {
            "metric": detect_metric_v1(query),
            "district": detect_district_v1(query),
            "task": detect_task_v1(query),
        }

    if prompt_version == "V2":
        return {
            "metric": detect_metric_v2(query),
            "district": detect_district_v2(query),
            "task": detect_task_v2(query),
        }

    if prompt_version == "V3":
        return {
            "metric": detect_metric_v3(query),
            "district": detect_district_v3(query),
            "task": detect_task_v3(query),
        }

    raise ValueError(f"Unsupported prompt version: {prompt_version}")


def is_hallucinated(prediction):
    """判断解析结果是否出现 schema 外的字段。"""
    return (
        prediction["metric"] not in ALLOWED_METRICS
        or prediction["district"] not in ALLOWED_DISTRICTS
        or prediction["task"] not in ALLOWED_TASKS
    )


def calculate_accuracy(correct_count, total_count):
    """计算准确率，统一返回 0 到 1 的小数。"""
    if total_count == 0:
        return 0.0
    return round(correct_count / total_count, 3)


def evaluate_prompt_version(rows, prompt_version):
    """评估单个 prompt 版本的解析准确率和 hallucination rate。"""
    total_count = len(rows)
    metric_correct = 0
    district_correct = 0
    task_correct = 0
    overall_correct = 0
    hallucination_count = 0

    for row in rows:
        prediction = simulate_prompt_output(row["query"], prompt_version)

        metric_ok = prediction["metric"] == row["expected_metric"]
        district_ok = prediction["district"] == row["expected_district"]
        task_ok = prediction["task"] == row["expected_task"]

        metric_correct += int(metric_ok)
        district_correct += int(district_ok)
        task_correct += int(task_ok)
        overall_correct += int(metric_ok and district_ok and task_ok)
        hallucination_count += int(is_hallucinated(prediction))

    return {
        "prompt_version": prompt_version,
        "metric_accuracy": calculate_accuracy(metric_correct, total_count),
        "district_accuracy": calculate_accuracy(district_correct, total_count),
        "task_accuracy": calculate_accuracy(task_correct, total_count),
        "overall_accuracy": calculate_accuracy(overall_correct, total_count),
        "hallucination_rate": calculate_accuracy(hallucination_count, total_count),
    }


def write_results(results, output_path):
    """将评测结果写入 results.csv。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


def evaluate_all_versions(benchmark_path=DEFAULT_BENCHMARK_PATH, output_path=DEFAULT_RESULTS_PATH):
    """评估 V1、V2、V3 并生成 results.csv。"""
    rows = load_benchmark(benchmark_path)
    results = [evaluate_prompt_version(rows, version) for version in PROMPT_VERSIONS]
    write_results(results, output_path)
    return results


if __name__ == "__main__":
    generated_results = evaluate_all_versions()
    for result in generated_results:
        print(result)
