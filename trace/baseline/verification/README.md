# 核验记录的范围

`revision_v3/` 与 `reproduction.json` 是整理前 v3 的执行记录，不是当前 GitHub 克隆重新完成了训练或作者审阅。记录内部可能提到本地原始数据、Zotero 路径、旧 Markdown、源码 ZIP、渲染页或历史版本；这些材料不全在公开仓库。

- [v3 核验说明](revision_v3/acceptance.md)：原结果、探索性优化、文献和双语交付范围。
- [算术与保护检查](revision_v3/verification.json)：2,529 项检查、390 个保护文件、新模型重拟合结果。
- [双语对齐](revision_v3/bilingual_alignment.json)：对应 v3 文本。
- [独立源码编译](revision_v3/standalone_rebuild.json)：六份 v3 源稿从原 ZIP 解压编译。
- [既往主分析复现](reproduction.json)：仅相同输入与环境的计算复现。
- [仓库整理记录](repository_reorganization.md)：公开范围、原件保留与本次检查。

新增编辑或更换环境后，旧报告不能自动覆盖新稿。运行 `python3 scripts/repository.py check` 产生当前仓库检查，运行 `build` 验证新源码的编译；报告与输出留在 `build/`。视觉、引文原文与推论质量应另行核验。
