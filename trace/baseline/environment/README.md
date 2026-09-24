# 环境

仓库检查与打包使用 Python 3.10+ 标准库。LaTeX 编译需 PATH 中的 Tectonic；当前源稿使用 fontspec、TeX Gyre Termes，中文另用 ctex/Fandol。首次编译可能下载字体与宏包。

分析使用 Python 3.12 和 [锁定依赖](requirements.lock.txt)。既往实际版本见 [执行记录](../results/primary/run_manifest.json)。这些依赖用于授权原始数据上的重拟合，不是阅读或编译论文的前提。

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r environment/requirements.lock.txt
```

不同数值库或系统可能引起浮点差异。旧环境的复现误差容许值是 1e-12；新运行应记录自己的环境及差异。完整步骤见 [复现说明](../docs/reproduction.md)。
