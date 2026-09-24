# 仓库整理与写作入口

本次整理针对 GPT‑6 Pro 的成稿交接。旧目录同时存在当前 LaTeX、过期 Word/PDF、逐段译文、版本补丁、重复 ZIP、渲染缓存与私人数据，难以判断哪个文件有效。主要改动是确立权威稿件、聚合证据及可执行入口，保留原科学计算。

## 已实施：成稿与交付 module

- **interface**：`WRITING_HANDOFF.md` 给出写作流程；`scripts/repository.py` 提供 `check`、`build`、`package`。
- **seam**：已冻结分析与可修改稿件之间；数值证据通过结果文件读取，写作在 LaTeX 上进行。
- **depth / leverage**：接收模型只需一个任务入口和三个命令，就能定位证据、核对依赖、编译两种语言并打包。
- **locality**：公开范围与冻结结果集中在 `configs/publication.json`，所有打包与检查共用它。
- **adapter**：英文和中文各有实际独立的 LaTeX 目录；同一个编译流程接受语言目录配置，无额外渲染抽象。

**deletion test**：移走重复 ZIP、旧 Word/PDF、OCR 缓存和过期生成器后，研究计算与当前 LaTeX 编译行为仍然保留。此前的 Markdown/模板会覆盖新写作，因此它们与生成脚本一起移入本地归档。

## 保留的目录

`results/primary`、`results/exploratory_v3`、`configs` 与 `scripts` 的分析路径保持稳定；分析脚本的同级导入和根目录定位不变。`manuscript/latex` 与 `manuscript/zh` 保留原相对图路径。没有为文件夹命名重新运行或修改科学结果。

用户提供的三份输入说明集中到 `docs/inputs/`。主稿、补充材料、标题页的 `.tex` 是当前写作权威源；原 PDF 是对应的 v3 阅读基线。新编译输出在 `build/`，与输入分开。

## 发布与本地保留

GitHub 仓库公开，只发布明确列举的文件。逐人记录在本地原分析路径保留，历史/构建/全文材料可恢复地归档；整理前另有逐文件 SHA-256 核对的完整备份。原始全文的链接和论断定位进入公开文献索引，全文本身留在本地。

本次没有进行模型算法重构。双语旧 Markdown renderer 的合并对当前成稿任务收益有限；三个交付命令直接使用 LaTeX，避免重新引入一条会覆盖手工写作的生成链。
