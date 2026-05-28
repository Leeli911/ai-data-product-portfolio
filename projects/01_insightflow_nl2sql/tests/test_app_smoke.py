from app import run_analysis_workflow


def test_run_analysis_workflow_smoke():
    """测试主流程能从中文问题串联到 SQL 和诊断结果。"""
    result = run_analysis_workflow("为什么北京朝阳区本周 GMV 下滑？")

    assert result["parsed_intent"]["metric"] == "gmv"
    assert "SELECT" in result["generated_sql"]
    assert result["analysis_result"]["main_driver"] == "orders"
    assert "业务诊断" in result["business_diagnosis"]
