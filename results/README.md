# 结果入口

| 研究问题 | 文件 |
|---|---|
| 样本处理、缺口及单位 | [主分析审计](primary/audit.json) |
| 主分析全部情景/模型/结局 | [metrics.csv](primary/metrics.csv) |
| 原模型与基线、共享与独立比较 | [paired_comparisons.csv](primary/paired_comparisons.csv) |
| 开发阶段模型选择 | [选择记录](primary/selection_locked.json) · [交叉验证排名](primary/cv_model_ranking.csv) |
| 特征对拟合预测的贡献 | [SHAP 排名](primary/interpretation/shap_ranking.csv) · [置换诊断](primary/interpretation/permutation_importance_summary.csv) |
| 探索性开发集表现 | [嵌套汇总](exploratory_v3/nested_summary.json) · [分折指标](exploratory_v3/nested_fold_metrics.csv) |
| 探索性留出表现与比较 | [holdout_metrics.csv](exploratory_v3/holdout_metrics.csv) · [paired_comparisons.csv](exploratory_v3/paired_comparisons.csv) |

`SWB_nn` 为消极情绪，`SWB_pp` 为积极情绪，`SWB_avg` 为生活满意度。RMSE 保留存储分数单位。原留出集已用于主分析，后续优化均为探索性。嵌套汇总中的归一化误差与留出集原单位 RMSE 不可直接比较。

主分析比较字段 `delta_rmse_a_minus_b` 表示第一模型减第二模型，负值表示第一模型误差较低。逐点 bootstrap 区间、置换检验及 Holm 校正的覆盖范围以 [分析计划](../docs/analysis_plan.md) 和 [补充方法](../manuscript/latex/supplement.tex) 为准。

Git 中只包含汇总结果。此工作区可能另有被忽略的模型、划分、预测和清洗表；它们是本地受限材料，公开克隆中不存在。
