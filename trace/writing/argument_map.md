# 论证地图与证据定位

本图与正文中的 `% [段落编号]` 注释对应。段落编号只存在于源文件，不显示在 PDF。原仓库文件可从 `source_index.md` 的基线链接定位；本包聚合文件位于 `evidence/`。引文键与 `reference_metadata.json` 对应。

## 整体论证

研究问题从“语言包含心理信息”推进到“给定类别表征是否改善具体分数的估计”。三个问题分别由关联与误差、共享/独立配对比较、归因与留出扰动回答。讨论区分已观察结果、可能解释以及下一步能检验什么，不用技术流程顺序代替论文逻辑。

## 摘要

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| A01 | 概括设计、主要估计及其能够支持的测量主张。 | primary_metrics_excerpt.csv；primary_paired_comparisons.csv；nested_summary_transcribed.json；permutation_importance_summary.csv |
## 引言

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| I01 | 从个人主观体验出发界定测量问题及其不同成分。 | 文献支持与研究问题推导；不含本研究新增结果；引文：`diener1984`, `diener1985`, `watson1988`, `diener2018` |
| I02 | 说明研究语言的理由，并明确尚待回答的效度问题。 | 文献支持与研究问题推导；不含本研究新增结果；引文：`park2015` |
| I03 | 将词典表征作为需要检验的研究选择，而非中性的预处理。 | 文献支持与研究问题推导；不含本研究新增结果；引文：`tausczik2010`, `zhao2016` |
| I04 | 准确定位本研究的经验贡献，不混同不同人群或聚合层级。 | 文献支持与研究问题推导；不含本研究新增结果；引文：`jaidka2020`, `eichstaedt2021` |
| I05 | 从结局的多维结构引出共享输出比较。 | 文献支持与研究问题推导；不含本研究新增结果；引文：`caruana1997`, `kocev2007`, `yarkoni2017` |
| I06 | 明确三个可回答的问题及不同结果的证据作用。 | 文献支持与研究问题推导；不含本研究新增结果 |
## 方法

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| M01 | 区分原始招募记录与本次二次分析。 | 原仓库 docs/inputs/study_context.md（仅采集说明） |
| M02 | 说明参与者层面的分析单位与确定性的重复记录处理。 | 原仓库 results/primary/audit.json；docs/independent_data_review.md |
| M03 | 将伦理陈述归于实际来源，二次使用授权留待作者确认。 | 原采集说明与待作者核实的伦理文件 |
| M04 | 界定构念，并保留未经核实转换的存储分数单位。 | 原仓库 docs/inputs/data_dictionary.md；audit.json；引文：`diener1985`, `watson1988` |
| M05 | 描述给定表征及实际考察的特征定义问题。 | 原仓库 data_dictionary.md；study_context.md；audit.json |
| M06 | 依据已有时间证据界定回溯性的目标关系。 | 原仓库 audit.json；independent_data_review.md 的时间戳假设 |
| M07 | 说明回溯性数据中的前置计算计划和留出划分。 | 原仓库 docs/analysis_plan.md；configs/analysis.json |
| M08 | 解释预处理和结局缩放为何仅在训练折拟合。 | 原仓库 docs/analysis_plan.md；引文：`kapoor2023` |
| M09 | 介绍八类模型，以及共享和独立学习的具体含义。 | 原仓库 configs/analysis.json；selection_locked.json；引文：`breiman2001`, `geurts2006` |
| M10 | 说明选择指标及不同程序的参数选择方式。 | cv_model_ranking.csv；原仓库 selection_locked.json |
| M11 | 定义相关和误差的不确定性，以及不同多重检验范围。 | 原仓库 docs/analysis_plan.md；primary_paired_comparisons.csv |
| M12 | 界定稳健性检查，避免将其表述为新的独立验证。 | sensitivity_selected.csv；repeated_cv_reported.csv；原分析计划 |
| M13 | 区分 SHAP 与置换诊断的用途及各自使用的数据。 | shap_top10.csv；permutation_importance_summary.csv；原 interpretation_manifest.json；引文：`lundberg2020` |
| M14 | 保留后续优化的时间顺序及其有限证据地位。 | 原仓库 docs/exploratory_plan_v3.md；nested_summary_transcribed.json；引文：`cawley2010` |
## 结果

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| R01 | 描述结局结构及开发集选定的模型程序。 | table1_descriptives.csv；target_correlations.csv；cv_model_ranking.csv |
| R02 | 报告所选模型的相关及不确定性，不用显著性差异代替结局间比较。 | primary_metrics_excerpt.csv |
| R03 | 通过基线比较量化数值准确性，并与相关区分。 | primary_metrics_excerpt.csv（含多任务弹性网对照） |
| R04 | 按实际不确定性程序解释配对比较。 | primary_paired_comparisons.csv |
| R05 | 通过配对差值及其精度回答共享学习问题。 | primary_paired_comparisons.csv；原 selection_locked.json |
| R06 | 列出重要输入及其归因幅度，保留语义边界。 | shap_top10.csv |
| R07 | 具体展示模型内重要性与留出误差贡献需要分开解释。 | permutation_importance_summary.csv |
| R08 | 说明预定处理选择保留了什么，以及数值上有哪些变化。 | sensitivity_selected.csv；repeated_cv_reported.csv |
| R09 | 将探索性搜索结果置于嵌套表现和原有时间顺序之下。 | nested_summary_transcribed.json；exploratory_holdout_metrics.csv；exploratory_paired_comparisons.csv |
## 讨论

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| D01 | 将核心发现解释为从关联到分数准确性的实际转化幅度。 | R02–R05 的主结果综合 |
| D02 | 解释相关与 RMSE 的实际对照，不将其升级为新的模型差异检验。 | R03 的描述性比较；相关的正线性变换性质（数学解释） |
| D03 | 提出分成分的解释假设，并展开其他可能解释。 | R02；维度差异解释为待检验假设，不是已测机制；引文：`diener1984`, `diener1985` |
| D04 | 用探索性优化结果确定下一步比较，不宣称信息上限。 | R09；待开展的同样本表征比较；引文：`eichstaedt2021`, `kern2016` |
| D05 | 说明结局相关为什么不保证共享划分的收益。 | R05；原选择记录；重叠分区解释尚未直接检验；引文：`caruana1997`, `kocev2007` |
| D06 | 通过开发集归因与留出诊断的分离，限定心理解释。 | R06–R07；归因与输入扰动的概念区分；引文：`lundberg2020`, `janzing2020`, `shmueli2010` |
| D07 | 将类别观察转化为具体、可证伪的后续研究。 | R06–R07；候选词汇/语境核查方案；引文：`zhao2016` |
| D08 | 将时间对齐转化为可实施设计，并区分个体间和个体内目标。 | M06；前瞻窗口和个体内变化属于未来设计；引文：`eichstaedt2018` |
| D09 | 将效标核验、时间稳定性和其他验证证据对应到拟议分数。 | M04；原量表与语言派生分数的效度不能自动继承；引文：`watson1988`, `pavot1993`, `park2015` |
| D10 | 集中说明样本与推断边界，再指出下一阶段评估单位。 | M01/M07/M11；外部样本与条件性不确定性；引文：`varoquaux2018`, `kapoor2023` |
| D11 | 集中说明缺失输入妨碍哪些诊断，不将未验证视为验证失败。 | M04–M06；原独立数据审查 |
| D12 | 将应用价值联系到明确收益及参与者控制。 | R02–R05；特定用途下收益、误差与授权需另验证；引文：`eichstaedt2018` |
## 结论

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| C01 | 给出证据支持的回答及其下一步含义。 | 主分析结果综合，不添加新数值 |
## 声明

| 段落 | 段落功能 | 证据与推论边界 |
|---|---|---|
| X01 | 区分公开代码和聚合结果，以及受限的参与者层面输入。 | 原仓库 README、results/README.md 和公开文件清单 |
| X02 | 保留作者应承担的责任，不虚构声明内容。 | 原采集说明、任务书与待作者提供事项 |
| X03 | 区分既往计算协助、本轮写作协助与尚待完成的人类审批。 | 原稿 AI 声明及本轮实际执行记录 |

## 图表与研究问题的连接

| 项目 | 内容 | 回答的问题 |
|---|---|---|
| 正文图 1 | 去重、每人一条记录、开发/留出划分 | 哪些观察构成评估单位，如何避免同一人跨分区？ |
| 正文表 1–2 | 样本分数与模型表现 | 与自我报告相关到何种程度，分数误差有多大？ |
| 正文表 3、图 2 | 配对 RMSE 差值及区间 | 相对均值、相对独立模型的收益是否得到支持？ |
| 正文表 4；补充表 S5–S6 | SHAP 与全部选定特征的置换诊断 | 哪些特征影响拟合预测，影响是否转化为留出误差变化？ |
| 补充表 S1–S4 | 完整主模型比较、设置和敏感性 | 主要选择及指定处理方式是否能被检查？ |
| 补充表 S7–S10 | 嵌套开发、完整搜索、重复留出评价 | 后续优化提供了什么探索性证据？ |
