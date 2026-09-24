# 微博主观幸福感研究 · 双语成稿

本仓库的当前版本用于阅读和编辑论文。英文稿位于 `en/`，中文稿位于 `zh/`；两种语言均包含正文、补充材料、独立标题页及完整编译资源。

| 文档 | 英文 | 中文 |
|---|---|---|
| 正文 PDF | [en/manuscript.pdf](en/manuscript.pdf) | [zh/manuscript.pdf](zh/manuscript.pdf) |
| 补充材料 PDF | [en/supplement.pdf](en/supplement.pdf) | [zh/supplement.pdf](zh/supplement.pdf) |
| 标题页与声明 PDF | [en/title_page.pdf](en/title_page.pdf) | [zh/title_page.pdf](zh/title_page.pdf) |
| 正文源码 | [en/manuscript.tex](en/manuscript.tex) | [zh/manuscript.tex](zh/manuscript.tex) |

## 编辑与编译

在对应语言目录中编辑 `manuscript.tex`、`supplement.tex` 或 `title_page.tex`。参考文献位于 `references.tex` 与 `references_supplement.tex`，表格位于 `tables/`，图形位于 `figures/`，版式设置位于 `preamble.tex`。每种语言的编译输入均在自身目录中。

需要 XeLaTeX、常用 LaTeX 宏包和中文 CTeX/Fandol。优先使用 Liberation Serif；未安装时回退到 TeX Gyre Termes，字体变化可能影响分页。仓库不附字体文件。

```bash
bash build.sh       # 编译两种语言的六份 PDF
bash build.sh en    # 仅英文
bash build.sh zh    # 仅中文
```

编译中间文件写入被 Git 忽略的 `.build/`，成功后的 PDF 更新到 `en/` 和 `zh/`。也可进入单个语言目录，用 XeLaTeX 连续编译所需主文件三遍，直至交叉引用稳定。

## 记录与研究状态

修改说明、论证地图和核验记录位于 [trace/](trace/README.md)。冻结分析结果、原始分析代码及输入说明归档于 `trace/baseline/`；该目录是历史证据快照，不参与论文编译。旧稿、旧图和完整旧工作树仍可从 Git 历史恢复。

成稿措辞复核及验证见 [trace/manuscript_audit.md](trace/manuscript_audit.md)；冻结分析证据与论文编辑分别维护。当前成稿仍待负责作者审定；伦理及二次使用授权、计分依据、作者声明和与既有发表工作的关系均须由作者核实。公开仓库不包含逐人数据、原始帖子、模型文件、第三方全文或字体文件。

Debian/Ubuntu 最小环境依赖：`texlive-xetex texlive-latex-extra texlive-lang-chinese texlive-fonts-recommended fonts-liberation`。其中 `texlive-fonts-recommended` 提供超链接所需的字体度量。
