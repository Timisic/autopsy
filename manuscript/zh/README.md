# 中文论文源稿

此目录保留 v3 的主稿、补充材料、标题页，以及配套 figures/ 和书目。`.tex` 是后续成稿的编辑源；现有 PDF 是 v3 基线。主图主表随文，无页眉。

从仓库根目录执行：

```sh
python3 scripts/repository.py build --language zh
```

命令将资源复制到新的 build/ 子目录后编译，保留原输入。使用 Tectonic / XeLaTeX 字体体系；中文采用 ctex/Fandol。参考文献内嵌于 LaTeX，无需 BibTeX/Biber。

编辑说明见 [成稿任务书](../../WRITING_HANDOFF.md)，环境与交付见 [复现说明](../../docs/reproduction.md)。
