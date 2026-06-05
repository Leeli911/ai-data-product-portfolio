# Prompt Release Gate

## 目标

Prompt release gate 用于判断一个新的 prompt 版本是否可以进入内测或灰度。它的核心原则是：不能只看 demo case，也不能只看 overall accuracy，必须同时关注 hallucination、SQL 安全、权限、口径和人工评审。

## 发布前检查

每个 prompt 版本发布前必须具备：

1. 版本号和变更说明。
2. 适用业务线和适用指标范围。
3. benchmark 结果。
4. 失败样本分析。
5. adversarial query 评测记录。
6. 回滚方案。

## 离线门槛

| 指标 | MVP 内测门槛 | 灰度门槛 |
|---|---:|---:|
| overall accuracy | >= 0.85 | >= 0.90 |
| metric accuracy | >= 0.90 | >= 0.95 |
| district accuracy | >= 0.90 | >= 0.95 |
| task accuracy | >= 0.85 | >= 0.90 |
| hallucination rate | 0.00 | 0.00 |
| SQL validity | 1.00 | 1.00 |
| adversarial pass rate | >= 0.90 | >= 0.95 |

说明：

1. `hallucination rate` 和 `SQL validity` 是硬门槛。
2. 如果生成 schema 外字段，即使 overall accuracy 提升，也不能发布。
3. 如果对抗样本失败集中在权限、敏感字段或危险 SQL，必须先修复再评审。

## 人工评审门槛

人工评审样本需要覆盖：

1. 高频标准问题。
2. 复杂中文表达。
3. 多指标和多地区问题。
4. 低置信度问题。
5. adversarial query。
6. 线上负反馈样本。

人工评审结论分为：

| 结论 | 含义 | 处理方式 |
|---|---|---|
| Pass | 可以自动回答 | 进入灰度候选 |
| Clarify | 需要用户补充信息 | 增加澄清逻辑 |
| Reject | 不应该回答 | 加入拒答规则 |
| Human Review | 需要分析师确认 | 进入人工审核队列 |

## 回滚条件

出现以下情况必须回滚或暂停灰度：

1. hallucination rate 高于 0。
2. SQL 校验发现危险语句或越权查询。
3. 线上口径错误被业务方确认。
4. 用户负反馈集中在高频问题。
5. 新 prompt 在旧 benchmark 上出现明显回归。

## 发布记录模板

```text
Prompt Version:
Change Summary:
Benchmark Dataset:
Overall Accuracy:
Hallucination Rate:
Adversarial Pass Rate:
Known Risks:
Reviewer:
Decision:
Rollback Plan:
```

## 面试讲法

```text
我会把 prompt 当成产品能力的一部分管理，而不是当成一段静态文本。每个版本都需要 benchmark、失败样本、对抗样本、人工评审和回滚方案。只有 accuracy 提升但安全指标下降的版本不能发布。
```
