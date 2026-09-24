# autopsy · 微博主观幸福感研究

这是从提供的题名、研究方法和数据独立重建的研究与写作仓库。当前基线为 **2026-09-24 v3**：30 篇已核对文献、原主分析、后续探索性优化，以及中英文 LaTeX/PDF。下一阶段是重新组织论文论证并完成成稿。

**交给 GPT‑6 Pro 时，从 [WRITING_HANDOFF.md](WRITING_HANDOFF.md) 开始。** 该任务书包含阅读顺序、写作要求、结果入口和交付标准。仓库中的 `.tex` 是本轮写作的权威源文件。

## 阅读与编辑

| 内容 | 入口 |
|---|---|
| 英文主稿 | [LaTeX](manuscript/latex/manuscript.tex) · [基线 PDF](manuscript/latex/manuscript.pdf) |
| 中文主稿 | [LaTeX](manuscript/zh/manuscript.tex) · [基线 PDF](manuscript/zh/manuscript.pdf) |
| 补充方法与结果 | [英文](manuscript/latex/supplement.tex) · [中文](manuscript/zh/supplement.tex) |
| 待作者补充的声明 | [英文标题页](manuscript/latex/title_page.tex) · [中文标题页](manuscript/zh/title_page.tex) |
| 结果与变量说明 | [结果索引](results/README.md) · [数据说明](docs/inputs/data_dictionary.md) |
| 文献依据 | [论断与原文位置](literature/evidence_notes.md) · [来源索引](literature/evidence_index.json) |
| 运行与验证 | [复现说明](docs/reproduction.md) · [既往核验范围](verification/README.md) |
| 目录调整依据 | [架构说明](docs/architecture.md) · [研究术语](CONTEXT.md) |

## 当前结果

主分析纳入 1,037 名参与者、120 项聚合语言特征；开发集 933 人、留出集 104 人。开发阶段选出的共享随机森林在消极情绪、积极情绪和生活满意度上的留出相关分别约为 **0.247、0.284、0.152**。误差改善幅度有限。新增 22 配置的探索性流程未显示稳定改善，因此原主分析保留，后续结果分别报告。完整估计、区间和比较见 [结果表](tables/README.md)。

这是一项依据现有聚合特征的回顾性再分析。量表计分转换、原帖时间窗等信息仍有缺口；现有结果没有完成个体测量工具的全部效度验证。此前研究已发表，原目标论文未被检索、取得或引用。作者与投稿授权仍待确认。

## 三个工作入口

```sh
python3 scripts/repository.py check
python3 scripts/repository.py build --language all
python3 scripts/repository.py package
```

检查与打包仅需 Python 标准库；编译另需 Tectonic。输出进入本地 `build/`，保留输入稿件。打包包含公开源码及 v3 基线 PDF；新编译 PDF 从 `build/` 对应目录另附。首次编译可能下载字体和宏包。检查能确认资源、公开文件范围和冻结结果完整性；学术论证与版面仍需人工审阅。

编辑完成后运行检查、编译，核对新 PDF，再通过下载包或独立分支交付。直接修改 LaTeX；此前根据 Markdown/模板生成稿件的脚本已归档，避免覆盖新写作。

## 仓库范围

- `manuscript/`：两种语言的当前稿件、基线 PDF、图表和书目。
- `results/`、`tables/`：公开汇总统计、模型选择和探索性结果。
- `literature/`：30 篇文献的书目、来源、原文定位和版本说明。
- `scripts/`、`configs/`、`environment/`：保留的分析实现、固定参数与依赖，以及统一交接工具。
- `docs/`：输入背景、分析计划、期刊要求与复现说明。
- `verification/`：既往执行证据、冻结结果清单和本次仓库整理记录。

公开文件由 [publication.json](configs/publication.json) 明确列举。原始数据、UID、逐人预测、模型文件、文献全文、下载日志和旧构建副本不在 Git 中；本地原件与整理前完整备份均保留。公开源代码加汇总结果支持审阅，取得授权原始数据后才可重新拟合分析。

文献来源保留各自权利与访问条件，本仓库不重新分发第三方全文，也不授予参与者数据或原研究材料的使用权。未建立开源许可或新的投稿授权。
