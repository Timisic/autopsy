# 来源、证据与本轮核验范围

基线为 [Timisic/autopsy 的指定提交](https://github.com/Timisic/autopsy/tree/51e1e780111c712e43e1202e2b9f305111f3eaf3/)。原研究已发表论文不在本次证据来源中；未为补齐背景或重建结果而搜索其题目、摘要或正文。

## 原研究材料与分析记录

研究设计只根据 [提供的采集说明](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/inputs/study_context.md)、[数据字典](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/inputs/data_dictionary.md)、[主分析计划](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/analysis_plan.md)、[独立数据审查](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/independent_data_review.md)、[探索性计划](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/exploratory_plan_v3.md) 和仓库已保存的审计、选择及结果记录撰写。原采集说明的伦理与授权信息只按其来源归属报告。

## 聚合文件的复制范围

| 本包文件（evidence/） | 原仓库位置 | 完整性与使用范围 |
|---|---|---|
| [primary_metrics_excerpt.csv](evidence/primary_metrics_excerpt.csv) | [results/primary/metrics.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/primary/metrics.csv) | 仅标题及前 24 条 primary 结果；不是完整原文件，不声称通过原整文件冻结哈希。 |
| [primary_paired_comparisons.csv](evidence/primary_paired_comparisons.csv) | [results/primary/paired_comparisons.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/primary/paired_comparisons.csv) | 完整复制；冻结 SHA-256 一致。 |
| [table1_descriptives.csv](evidence/table1_descriptives.csv) | [tables/table1_descriptives.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/tables/table1_descriptives.csv) | 完整复制；冻结 SHA-256 一致。 |
| [sensitivity_selected.csv](evidence/sensitivity_selected.csv) | [figures/figureS2_source.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/figures/figureS2_source.csv) | 完整复制该绘图源文件；Git blob SHA-1 一致；不是所有家族的敏感性全集。 |
| [exploratory_holdout_metrics.csv](evidence/exploratory_holdout_metrics.csv) | [results/exploratory_v3/holdout_metrics.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/exploratory_v3/holdout_metrics.csv) | 完整复制；冻结 SHA-256 一致。 |
| [exploratory_paired_comparisons.csv](evidence/exploratory_paired_comparisons.csv) | [results/exploratory_v3/paired_comparisons.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/exploratory_v3/paired_comparisons.csv) | 完整复制；冻结 SHA-256 一致；显示标签按 model_a/model_b 解释。 |
| [shap_top10.csv](evidence/shap_top10.csv) | [figures/figure4_source.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/figures/figure4_source.csv) | 完整复制该 top-10 绘图源表；Git blob SHA-1 一致；不是所有 120 特征的完整排名。 |
| [permutation_importance_summary.csv](evidence/permutation_importance_summary.csv) | [results/primary/interpretation/permutation_importance_summary.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/primary/interpretation/permutation_importance_summary.csv) | 完整复制；冻结 SHA-256 一致。 |
| [cv_model_ranking.csv](evidence/cv_model_ranking.csv) | [results/primary/cv_model_ranking.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/primary/cv_model_ranking.csv) | 完整复制；冻结 SHA-256 一致。 |
| [target_correlations.csv](evidence/target_correlations.csv) | [results/primary/target_correlations.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/primary/target_correlations.csv) | 完整复制；冻结 SHA-256 一致。 |
| [nested_outcome_summary.csv](evidence/nested_outcome_summary.csv) | [tables/tableS3_exploratory_nested.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/tables/tableS3_exploratory_nested.csv) | 完整复制；冻结 SHA-256 一致。 |
| [nested_summary_transcribed.json](evidence/nested_summary_transcribed.json) | [results/exploratory_v3/nested_summary.json](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/results/exploratory_v3/nested_summary.json) | 四个数值转录；JSON 序列化并非原件；另行检查相对变化算术。 |
| [repeated_cv_reported.csv](evidence/repeated_cv_reported.csv) | [manuscript/latex/supplement.tex](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/manuscript/latex/supplement.tex) | 按基线稿已经报告的四位小数转录；不冒充未获取的高精度原表。 |
| [exploratory_grid_transcribed.csv](evidence/exploratory_grid_transcribed.csv) | [tables/tableS4_exploratory_grid.csv](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/tables/tableS4_exploratory_grid.csv) | 保留全部 22 个候选及 CV 数值；参数改为可读显示标签，非逐字节原件。 |

本包没有原始帖子、问卷逐题反应、逐人记录、逐人预测或拟合模型对象。八项冻结 SHA-256 和两项 Git blob 检查只覆盖上表对应的完整复制文件，不覆盖整个仓库。摘录/转录不覆盖原件，图表生成不改变原统计估计。

## 学术引文与具体论断

所有条目均在 [原仓库证据记录](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/literature/evidence_notes.md) 中按作者、年份和题目定位。本轮通读了该记录的全部 30 项，并将正文压缩为 23 个有具体用途的来源。下表页码/段落定位除“本轮复核”四项外，均继承自仓库已有记录，**不表示本轮重新逐页阅读了所有全文**。本轮复核使用相应论文的作者版或正式期刊/会议原文；PDF 所需位置另查看页面图像。

| 引文键与发表年份 | 论断位置 | 本文用途与适用边界 | 本轮原文复核 |
|---|---|---|---|
| [`breiman2001`](https://doi.org/10.1023/A:1010933404324) · 2001 | 发表版 pp.25–27，regression forests | 随机树预测取平均；不证明本样本中的优越性。 | 否；沿用仓库证据定位 |
| [`caruana1997`](https://doi.org/10.1023/A:1007379606734) · 1997 | 作者版 p.3，§§1.3–1.4；p.11 | 共享表征提供归纳偏置；结局相关不保证共享树收益。 | 否；沿用仓库证据定位 |
| [`cawley2010`](https://jmlr.org/papers/v11/cawley10a.html) · 2010 | JMLR p.2080；模型选择与性能评估部分 | 有限样本中的选择性偏差；嵌套只覆盖给定候选搜索。 | 否；沿用仓库证据定位 |
| [`diener1984`](https://doi.org/10.1037/0033-2909.95.3.542) · 1984 | 发表版 pp.542–544 | 主观体验和评价的构念依据；不验证语言预测器。 | 否；沿用仓库证据定位 |
| [`diener1985`](https://doi.org/10.1207/s15327752jpa4901_13) · 1985 | 发表版 pp.71–72 | 五题 SWLS 的全局生活评价；不证明本数据计分转换。 | 否；沿用仓库证据定位 |
| [`diener2018`](https://doi.org/10.1525/collabra.115) · 2018 | PMC6329388，BioC passages 6、8、10、12 | 个体自身评价及多种验证证据；不确证本次施测版本。 | 否；沿用仓库证据定位 |
| [`eichstaedt2021`](https://doi.org/10.1037/met0000349) · 2021 | 发表版 pp.399、403、416 | 封闭和开放词汇表征的互补用途；不预设本数据收益。 | 否；沿用仓库证据定位 |
| [`eichstaedt2018`](https://doi.org/10.1073/pnas.1802331115) · 2018 | PDF pp.1–2、5；p.4 隐私讨论 | 抑郁医疗记录前的语言窗口；不等同于主观幸福感效标。 | 否；沿用仓库证据定位 |
| [`geurts2006`](https://doi.org/10.1007/s10994-006-6226-1) · 2006 | 作者版 pp.3–4，§2.1 | 分裂阈值随机化；不证明共享输出实现或优势。 | 否；沿用仓库证据定位 |
| [`jaidka2020`](https://doi.org/10.1073/pnas.1906364117) · 2020 | PDF pp.4–5；在线正文对县级及个体样本的比较 | 分析单位及地区、社会经济语境的影响；不转移数值效应量。 | [是：相关原文](https://www.pnas.org/doi/10.1073/pnas.1906364117) |
| [`janzing2020`](https://proceedings.mlr.press/v108/janzing20a.html) · 2020 | PMLR PDF pp.3–5，§3；p.4 输入干预讨论 | 算法输入变化与现实变量干预不同；不将归因变为心理因果效应。 | [是：相关原文](https://proceedings.mlr.press/v108/janzing20a/janzing20a.pdf) |
| [`kapoor2023`](https://doi.org/10.1016/j.patter.2023.100804) · 2023 | 发表版 pp.4–5；leakage taxonomy | 折外拟合预处理、重复/依赖观察和评估分布风险。 | 否；沿用仓库证据定位 |
| [`kern2016`](https://doi.org/10.1037/met0000091) · 2016 | PDF p.3 / 期刊 p.509 | 语言数量和聚合单位影响推断；不移植该文具体阈值。 | 否；沿用仓库证据定位 |
| [`kocev2007`](https://doi.org/10.1007/978-3-540-74958-5_61) · 2007 | 作者版 pp.3–4，§3 | 共同分裂和向量叶节点；不把本次比较推广至所有多任务架构。 | 否；沿用仓库证据定位 |
| [`lundberg2020`](https://doi.org/10.1038/s42256-019-0138-9) · 2020 | PMC7326367，passages 23–24、33–34、65–67、75–78 | 树结构归因及不同背景定义；模型归因不是现实因果作用。 | 否；沿用仓库证据定位 |
| [`park2015`](https://doi.org/10.1037/pspp0000020) · 2015 | Online First 作者 PDF pp.5–10、13；p.10 test–retest | 聚合、区分、知情者、外部效标和时间验证；不继承人格分数的效度。 | [是：相关原文](https://gregpark.io/assets/pdfs/automatic_personality_assessment_through_social_media_language.pdf) |
| [`pavot1993`](https://doi.org/10.1037/1040-3590.5.2.164) · 1993 | PDF p.6 / 期刊 p.169 | 时间稳定性和真实变化敏感性需区分。 | 否；沿用仓库证据定位 |
| [`shmueli2010`](https://doi.org/10.1214/10-STS330) · 2010 | 作者 PDF p.2，§§1.1–1.2 | 预测与解释的目标不同；有效预测不直接确立机制。 | 否；沿用仓库证据定位 |
| [`tausczik2010`](https://doi.org/10.1177/0261927X09351676) · 2010 | PDF p.7 / 期刊 p.30 | 词典对语境、反讽、习语的局限；不是本模型误差原因的实测结果。 | 否；沿用仓库证据定位 |
| [`varoquaux2018`](https://doi.org/10.1016/j.neuroimage.2017.06.061) · 2018 | 作者 PDF p.3 与 Appendix D | 有限样本和非独立 CV 折的不确定性；不转移神经影像中的数值误差界。 | 否；沿用仓库证据定位 |
| [`watson1988`](https://doi.org/10.1037/0022-3514.54.6.1063) · 1988 | 发表版 pp.1064–1065、1070 | 两个十题情绪分量表及不同报告时段；不确证本次中文条目。 | 否；沿用仓库证据定位 |
| [`yarkoni2017`](https://doi.org/10.1177/1745691617693393) · 2017 | 作者 PDF pp.11–13，Cross-Validation | 留出评价与开发期选择；测试集不参与优胜模型的再选择。 | 否；沿用仓库证据定位 |
| [`zhao2016`](https://doi.org/10.1371/journal.pone.0157947) · 2016 | Study 1/2、General Discussion；PDF pp.10–12 | 中文词典效度随类别和文本形式变化；词匹配不等于作者的心理状态。 | [是：相关原文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0157947) |

正式发表年份最晚为 2023 年，均早于 2024-08-01。Park 的作者 PDF 为 Online First 版本，文中使用正式 2015 年 JPSP 书目信息。原量表及其他样本的验证结果不被当作当前施测版本的验证。没有全文、扫描件或 OCR 衍生物被放入交付包。

## 期刊准备要求

格式准备参照仓库 [期刊要求记录](https://github.com/Timisic/autopsy/blob/51e1e780111c712e43e1202e2b9f305111f3eaf3/docs/journal_requirements.md)，该记录标注于 2026-09-23 核查。它要求摘要 150–200 词、六个关键词、作者—年份引用、独立标题页，并推荐原稿不超过 30 页。其正文间距、嵌入图表与传统末尾图表要求并不完全一致；本包沿用可读性优先的 1.2/1.3 倍行距及随文图表，不声称已满足投稿系统的全部最终格式检查。

本轮尝试重新访问期刊官方指南未取得可用页面，故未把 2026-09-23 的旧记录描述为本轮独立在线核验。尚未登录投稿系统、确认投稿资格或提交任何稿件。
