"""Text2Analytics Phase 1 的类型化输入输出契约。"""

from typing import Literal

from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    """用户提交给分析流水线的业务问题。"""

    question: str
    dataset_id: str = "local_life_demo"


class IntentResult(BaseModel):
    """Intent Agent 对第一阶段问题的结构化理解。"""

    intent_type: Literal["drop_reason_analysis", "unsupported"]
    metric: str | None = None
    metric_label: str | None = None
    district: str | None = None
    time_range: str | None = None
    comparison_period: str | None = None
    ambiguities: list[str] = Field(default_factory=list)


class AnalysisStep(BaseModel):
    """一个可独立检查的分析步骤。"""

    step_id: str
    goal: str
    required_metrics: list[str]
    group_by: list[str]
    is_required: bool = True


class AnalysisPlan(BaseModel):
    """Planner Agent 输出的有序分析计划。"""

    intent: IntentResult
    steps: list[AnalysisStep]


class PlanValidationResult(BaseModel):
    """Plan Validator 对必需分析路径的检查结果。"""

    is_valid: bool
    missing_step_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
