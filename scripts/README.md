# 脚本入口

`repository.py` 是公开仓库的检查、直接 LaTeX 编译和打包入口。它只处理明确声明的公开文件，编译输出写入 build/。

以下分析脚本保留原实现与同级导入关系，复现时需要授权原始数据及对应本地输出：

| 脚本 | 输入与行为 |
|---|---|
| analyze.py | 根 data.csv、固定配置；审计、模型选择与评估，运行时显式传入新的 --out |
| optimize_v3.py | 原数据、原主分析划分及预测；有限预算探索性优化 |
| verify_reproduction.py | 原与重跑的逐人输出；计算一致性比较 |
| interpret.py | 主分析模型、训练特征、预测；TreeSHAP 与置换诊断 |
| make_figures.py | 主分析及逐人输出；生成图表和结果表 |
| export_exploratory_tables.py | 已保存探索性结果；导出补充表 |

旧 Word/Markdown/译文生成器、版本补丁与依赖本机缓存的审查工具已归档。编辑阶段直接修改 LaTeX。不要使用旧生成器覆盖 Pro 改写后的文本。
