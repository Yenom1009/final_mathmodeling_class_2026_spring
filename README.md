# 恐惧效应下的捕食者-猎物动力学建模

本项目构建无恐惧 M0、即时恐惧 M1、记忆恐惧 M2 和三级食物链扩展 M3，输出文献表、理论推导、参数扫描、图表和中文报告。

## 运行方法

推荐在本机已有环境中运行：

```bash
conda activate d2l
python -m src.run_all
```

通用环境可按以下方式安装：

```bash
pip install -r requirements.txt
python -m src.run_all
```

## 输出位置

- `results/`: 时间序列、`scan_k.csv`、`scan_k_alpha.csv`、代表性参数和理论边界。
- `figures/`: 12 张主要图，每张保存为 PNG 和 PDF。
- `literature/`: 文献综述表和重点文献结构化笔记。
- `report/`: 中文 `report.md`、`report.tex` 和一个可阅读的 `report.pdf`。

注意：本项目是机制模拟和定性分析，不声称对真实生态系统做精确预测。
