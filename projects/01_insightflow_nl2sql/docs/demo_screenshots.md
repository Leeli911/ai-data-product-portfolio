# Demo 截图说明

本文件用于规划 InsightFlow 在 GitHub README、项目介绍和面试展示中的截图素材。

## 截图清单

| 编号 | 截图内容 | 推荐文件名 | 展示重点 |
|---|---|---|---|
| 1 | 首页输入界面 | `screenshot_01_home.png` | 产品标题、默认问题和四模块结构 |
| 2 | Parser 输出 | `screenshot_02_parser.png` | 中文问题被解析为结构化 intent |
| 3 | SQL 输出 | `screenshot_03_sql.png` | Generated SQL 展示 NL2SQL 能力 |
| 4 | Diagnosis 输出 | `screenshot_04_diagnosis.png` | GMV、环比、主因和业务诊断 |
| 5 | Benchmark 结果 | `screenshot_05_benchmark.png` | parser 评测结果和准确率指标 |

## 命名规范

截图统一使用小写英文和两位编号：

```text
screenshot_01_home.png
screenshot_02_parser.png
screenshot_03_sql.png
screenshot_04_diagnosis.png
screenshot_05_benchmark.png
```

## 推荐保存路径

建议后续把截图放在：

```text
projects/01_insightflow_nl2sql/assets/screenshots/
```

## 截图步骤

1. 启动 Streamlit：

```bash
cd projects/01_insightflow_nl2sql
streamlit run app.py
```

2. 使用默认问题：

```text
为什么北京朝阳区本周 GMV 下滑？
```

3. 点击 `开始分析`。
4. 按截图清单依次截取首页、parser、SQL、diagnosis 和 benchmark 区域。
5. 截图后在 README 中增加图片展示区域。

## 截图质量要求

1. 截图中不要出现浏览器无关区域。
2. 保留清晰的模块标题。
3. SQL、JSON 和诊断文案必须可读。
4. 首页截图应能在 30 秒内说明项目价值。
