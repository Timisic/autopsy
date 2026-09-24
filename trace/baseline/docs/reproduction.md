# 编译、检查与分析复现

## 从 GitHub 克隆后可直接完成

```sh
git clone git@github.com:Timisic/autopsy.git
cd autopsy
python3 scripts/repository.py check
python3 scripts/repository.py build --language all
python3 scripts/repository.py package
```

`check` 使用标准库，核对公开文件、冻结汇总结果、数据列、图表资源与书目年份。`build` 需要 PATH 中的 Tectonic，把所需源文件复制到新的 `build/` 目录并编译六份文档；它不会修改输入。首次编译可能联网下载 TeX 宏包和字体。`package` 只收录公开清单中的源码与 v3 基线 PDF，不递归打包本地目录。新编译 PDF 应从相应 build/ 子目录另附；该命令不会将新 PDF 自动替换进基线目录。

源稿中的参考文献目前直接写在 `.tex`；随附 `.bib`/CSL 是书目依据，更新 `.bib` 不会自动改写正文引用。两种语言均为独立 LaTeX 文档；英语目录名沿用 `latex`。

新稿应同时更新文内引用、文后书目和相关图表说明，并在编译后检查所有页面。仓库自检并不代替数字逐项核对、引用原文检查或视觉审阅。已有 PDF 为 v3 基线；本次或后续编译 PDF 请从 `build/` 获取。

## 取得授权数据后的重拟合

公开仓库不含逐人数据。在得到数据保管方授权后，将原始文件放在项目根目录 `data.csv`（Git 忽略），并核对与既往执行记录中的输入 SHA-256。建立分析环境：

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r environment/requirements.lock.txt
.venv/bin/python scripts/analyze.py --out results/new_reproduction --phase all
```

为每次运行指定一个新的输出目录。分析脚本保留旧默认值，省略 `--out` 会指向主分析目录，所以复现时必须显式指定新目录。脚本按原方案训练、选择和评估；没有原始输入时不能重拟合。公开参数和汇总结果也不足以重建逐人数据。

若同时取得原主分析的受限逐人预测与划分文件，可运行：

```sh
.venv/bin/python scripts/verify_reproduction.py --reference results/primary --candidate results/new_reproduction
```

该比较依赖本地受限文件。仅公开克隆不能运行它；已有 [复现报告](../verification/reproduction.json) 是旧输入与旧环境上的执行证据。探索性优化的原实现见 `scripts/optimize_v3.py`，还依赖原始主分析划分和预测。解释与绘图脚本同样需要已拟合模型或逐人输出。完整旧流程与所有原输入在本地整理前备份保留。

## 发布新文件

在 `configs/publication.json` 的 `files` 中明确增加路径，并在 `.gitignore` 中加入对应放行项。只为新增证据记录新的冻结清单；既有结果的哈希用于确认它们未被写作修改。运行 `check`，暂存后再运行 `check --staged`，确认本地数据或全文没有进入提交。
