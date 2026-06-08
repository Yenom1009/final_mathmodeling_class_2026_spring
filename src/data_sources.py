"""Static project text: literature notes, configs, README, and report."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pandas as pd


LITERATURE_ROWS = [
    ("P0", "Lima & Dill", 1990, "Behavioral decisions made under the risk of predation", "Canadian Journal of Zoology", "10.1139/z90-092"),
    ("P0", "Preisser & Bolnick", 2008, "The Many Faces of Fear", "PLOS ONE", "10.1371/journal.pone.0002465"),
    ("P0", "Zanette et al.", 2011, "Perceived Predation Risk Reduces the Number of Offspring Songbirds Produce per Year", "Science", "10.1126/science.1210908"),
    ("P0", "Wang, Zanette & Zou", 2016, "Modelling the fear effect in predator-prey interactions", "Journal of Mathematical Biology", "10.1007/s00285-016-0989-1"),
    ("P0", "Liu et al.", 2021, "Dynamics of a Predator-Prey Model with Fear Effect and Time Delay", "Complexity", "10.1155/2021/9184193"),
    ("P0", "Yang & Jin", 2022, "Dynamics in a predator-prey model with memory effect in predator and fear effect in prey", "Electronic Research Archive", "10.3934/era.2022069"),
    ("P1", "Kundu et al.", 2018, "Impact of Fear Effect in a Discrete-Time Predator-Prey System", "Bulletin of the Calcutta Mathematical Society", "title search"),
    ("P1", "Shi & Hu", 2024, "一类带有恐惧效应时滞的捕食者-猎物系统的动力学", "应用数学学报", "10.20142/j.cnki.amas.202401083"),
    ("P1", "Wang & Zou", 2017, "Modeling the Fear Effect in Predator-Prey Interactions with Adaptive Avoidance of Predators", "Bulletin of Mathematical Biology", "10.1007/s11538-017-0287-0"),
    ("P1", "Panday et al.", 2018, "Stability and Bifurcation Analysis of a Three-Species Food Chain Model with Fear", "International Journal of Bifurcation and Chaos", "10.1142/S0218127418500098"),
    ("P2", "Zhao, Yu & Li", 2025, "Dynamics analysis of a predator-prey model incorporating fear effect in prey species", "AIMS Mathematics", "10.3934/math.2025563"),
]


def write_literature_files(root: Path) -> None:
    literature = root / "literature"
    literature.mkdir(parents=True, exist_ok=True)
    table_lines = [
        "# Literature Table",
        "",
        "| Priority | Authors | Year | Title | Source | DOI / note | Use in project |",
        "|---|---:|---:|---|---|---|---|",
    ]
    use_map = {
        "Lima & Dill": "Behavioral foundation for risk-sensitive foraging and reproduction decisions.",
        "Preisser & Bolnick": "Non-consumptive effect pathways: behavior, physiology, survival, fecundity.",
        "Zanette et al.": "Empirical 40% reproduction reduction used only for scale calibration.",
        "Wang, Zanette & Zou": "Main fear-function and Holling-II mathematical reference.",
        "Liu et al.": "Delay/Holling-II parameter set and k-bifurcation narrative.",
        "Yang & Jin": "Memory-effect motivation; simplified here from PDE spatial memory to ODE risk memory.",
        "Kundu et al.": "Discrete-time comparison and Lyapunov/bifurcation style.",
        "Shi & Hu": "Chinese report structure for positivity, boundedness and Hopf discussion.",
        "Wang & Zou": "Adaptive avoidance extension, not placed in the main model.",
        "Panday et al.": "Tritrophic extension with fear at two trophic links.",
        "Zhao, Yu & Li": "Recent spatial/Turing extension, future-work context.",
    }
    for priority, authors, year, title, source, doi in LITERATURE_ROWS:
        table_lines.append(f"| {priority} | {authors} | {year} | {title} | {source} | {doi} | {use_map[authors]} |")
    (literature / "literature_table.md").write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    note_templates = {
        "wang2016_fear_model.md": dedent(
            r"""
            # Wang, Zanette & Zou (2016): Fear Model

            1. 原始模型方程
               文中先给出一般形式 `u' = r0 u f(k,v) - d u - a u^2 - g(u)v`, `v' = c g(u)v - m v`。Holling II 情形取 `g(u)=p u/(1+q u)`，并使用 `f(k,v)=1/(1+kv)`。
            2. 变量和参数表
               `u` 为猎物，`v` 为捕食者；`r0` 出生率，`d` 自然死亡，`a` 种内竞争，`p` 捕食强度，`q` 处理时间或饱和参数，`c` 转化效率，`m` 捕食者死亡率，`k` 恐惧强度。
            3. 恐惧项写法
               恐惧通过单调下降函数 `f(k,v)` 乘在猎物繁殖项上，经典形式是 `1/(1+kv)`。
            4. 记忆/时滞/扩散项写法
               本文没有显式记忆、时滞或扩散，属于 ODE 即时恐惧模型。
            5. 平衡点和稳定性结论
               线性功能反应下恐惧不改变主要动力学；Holling II 下恐惧会改变正平衡稳定性。
            6. Hopf 或分岔结论
               高恐惧可稳定系统并排除周期解，较低恐惧可出现 Hopf 分岔、多重极限环和双稳态。
            7. 数值模拟参数
               文中展示了 `p=0.5, q=0.6, m=0.05, c=0.4` 等组合以及多种 `k` 扫描；本项目不逐字复现其全部图，而复用其恐惧函数和 Hopf 叙事。
            8. 哪些内容可复用于本项目
               主模型的恐惧函数、Holling II 捕食项、正平衡和稳定性分析框架。
            9. 需要谨慎对待或不能直接照搬的地方
               论文变量符号与本项目不同；本文的记忆变量 `z` 是新增机制，不应说成 Wang 2016 已经包含记忆。
            """
        ),
        "liu2021_delay_model.md": dedent(
            r"""
            # Liu et al. (2021): Fear and Time Delay

            1. 原始模型方程
               论文使用 Holling II 捕食、恐惧降低猎物繁殖，并在捕食者增长中引入妊娠时滞和延迟存活因子。
            2. 变量和参数表
               常用参数为 `r=0.1, d1=0.01, d2=0.01, p=0.5, h=0.6, eta=0.4, d3=0.22`，这些作为本项目文献参数组 A。
            3. 恐惧项写法
               采用类似 `1/(1+kx)` 或 `1/(1+k y)` 的生殖折减项；本项目采用 `1/(1+kz)`。
            4. 记忆/时滞/扩散项写法
               原文重点是妊娠时滞 `tau`，不是本文的 ODE 记忆变量；若扩展 DDE，可测试 `tau=0.1,0.2,0.4`。
            5. 平衡点和稳定性结论
               给出正性、有界性、平衡点条件以及局部稳定性。
            6. Hopf 或分岔结论
               时滞和恐惧强度可诱发或抑制 Hopf 分岔；高恐惧在其参数组下有稳定作用。
            7. 数值模拟参数
               本项目直接测试上述参数组并用 `k` 扫描借鉴其分岔图形式。
            8. 哪些内容可复用于本项目
               参数量级、Holling II 结构、`k` 分岔图和“高恐惧稳定”现象。
            9. 需要谨慎对待或不能直接照搬的地方
               本项目没有实现 DDE 主模型，不能把本文结果说成时滞模型复现。
            """
        ),
        "yang2022_memory_model.md": dedent(
            r"""
            # Yang & Jin (2022): Memory and Fear

            1. 原始模型方程
               论文将捕食者空间记忆和猎物恐惧引入扩散型捕食者-猎物 PDE。
            2. 变量和参数表
               变量是空间-时间下的猎物和捕食者密度；关键参数包括扩散、记忆扩散系数、恐惧参数和时滞。
            3. 恐惧项写法
               猎物繁殖或增长受捕食风险恐惧函数影响。
            4. 记忆/时滞/扩散项写法
               记忆以空间记忆/非局部扩散形式进入捕食者运动，而不是本文的 `z'=alpha(y-z)`。
            5. 平衡点和稳定性结论
               分析共存平衡的局部稳定性。
            6. Hopf 或分岔结论
               讨论 Hopf 分岔；数值结果显示记忆扩散不利于稳定，恐惧在不同参数下可稳定也可失稳。
            7. 数值模拟参数
               原文参数服务于 PDE 图案和稳定域，本项目只借鉴定性结论。
            8. 哪些内容可复用于本项目
               记忆会改变线性化特征值并影响稳定性的思想。
            9. 需要谨慎对待或不能直接照搬的地方
               本文 ODE 记忆风险变量是机制化简，不能宣称复现 Yang & Jin 的空间记忆模型。
            """
        ),
        "panday2018_tritrophic.md": dedent(
            r"""
            # Panday et al. (2018): Tritrophic Food Chain with Fear

            1. 原始模型方程
               论文研究三物种食物链，底层猎物受中间捕食者恐惧影响，中间捕食者受顶级捕食者恐惧影响。
            2. 变量和参数表
               变量对应底层猎物、中间捕食者、顶级捕食者；参数包含两层捕食强度、转化效率、死亡率和恐惧强度。
            3. 恐惧项写法
               两个营养级上分别设置恐惧折减函数。
            4. 记忆/时滞/扩散项写法
               主体是 ODE 食物链，不作为本文记忆模型来源。
            5. 平衡点和稳定性结论
               给出多个边界和平衡态的稳定性条件。
            6. Hopf 或分岔结论
               分析分岔，展示恐惧可能使复杂或混沌动力学趋于稳定。
            7. 数值模拟参数
               本项目不逐图复现，采用简化三营养级模型做扩展。
            8. 哪些内容可复用于本项目
               `k1,k2` 两层恐惧扫描与食物链稳定性讨论。
            9. 需要谨慎对待或不能直接照搬的地方
               三级模型不是主模型，报告中不做完整理论证明。
            """
        ),
        "kundu2018_discrete.md": dedent(
            r"""
            # Kundu et al. (2018): Discrete-Time Fear System

            1. 原始模型方程
               该文将连续恐惧捕食者-猎物模型离散化，讨论离散迭代下的稳定和复杂行为。
            2. 变量和参数表
               变量仍为猎物和捕食者密度；参数包括增长、捕食、转化、死亡和恐惧强度。
            3. 恐惧项写法
               沿用恐惧降低猎物繁殖的思想。
            4. 记忆/时滞/扩散项写法
               属于离散时间模型，不含本文 ODE 记忆变量。
            5. 平衡点和稳定性结论
               分析不动点稳定性。
            6. Hopf 或分岔结论
               用 `k` 分岔图和最大 Lyapunov 指数描述离散系统复杂性。
            7. 数值模拟参数
               可借鉴其分岔图表达方式。
            8. 哪些内容可复用于本项目
               对比说明连续时间模型并不是唯一选择。
            9. 需要谨慎对待或不能直接照搬的地方
               本项目变量连续，不能把离散混沌结论直接用于 ODE。
            """
        ),
        "zhao2025_spatial.md": dedent(
            r"""
            # Zhao, Yu & Li (2025): Spatial Fear Model

            1. 原始模型方程
               论文研究含恐惧效应的捕食者-猎物模型，并扩展到空间扩散形式。
            2. 变量和参数表
               变量为猎物和捕食者密度；参数包括恐惧、捕食、扩散和稳定性相关参数。
            3. 恐惧项写法
               恐惧作用于猎物增长或繁殖。
            4. 记忆/时滞/扩散项写法
               包含 PDE 扩散，不包含本文 ODE 记忆风险变量。
            5. 平衡点和稳定性结论
               给出 ODE 正平衡稳定性和 PDE 稳定/失稳条件。
            6. Hopf 或分岔结论
               研究空间均匀 Hopf 分岔和 Turing 不稳定。
            7. 数值模拟参数
               适合作为空间扩展参考。
            8. 哪些内容可复用于本项目
               讨论部分说明未来可加入空间扩散与图案形成。
            9. 需要谨慎对待或不能直接照搬的地方
               本项目主模型假设空间均匀，因此不声称解释 Turing 图案。
            """
        ),
    }
    for filename, content in note_templates.items():
        (literature / filename).write_text(content.strip() + "\n", encoding="utf-8")


def write_references_bib(root: Path) -> None:
    bib = dedent(
        r"""
        @article{lima1990behavioral,
          title={Behavioral decisions made under the risk of predation: a review and prospectus},
          author={Lima, Steven L. and Dill, Lawrence M.},
          journal={Canadian Journal of Zoology},
          volume={68},
          number={4},
          pages={619--640},
          year={1990},
          doi={10.1139/z90-092}
        }

        @article{preisser2008many,
          title={The Many Faces of Fear: Comparing the Pathways and Impacts of Nonconsumptive Predator Effects on Prey Populations},
          author={Preisser, Evan L. and Bolnick, Daniel I.},
          journal={PLOS ONE},
          volume={3},
          number={6},
          pages={e2465},
          year={2008},
          doi={10.1371/journal.pone.0002465}
        }

        @article{zanette2011perceived,
          title={Perceived predation risk reduces the number of offspring songbirds produce per year},
          author={Zanette, Liana Y. and White, Aija F. and Allen, Marek C. and Clinchy, Michael},
          journal={Science},
          volume={334},
          number={6061},
          pages={1398--1401},
          year={2011},
          doi={10.1126/science.1210908}
        }

        @article{wang2016modelling,
          title={Modelling the fear effect in predator-prey interactions},
          author={Wang, Xiaoying and Zanette, Liana and Zou, Xingfu},
          journal={Journal of Mathematical Biology},
          volume={73},
          pages={1179--1204},
          year={2016},
          doi={10.1007/s00285-016-0989-1}
        }

        @article{liu2021dynamics,
          title={Dynamics of a Predator-Prey Model with Fear Effect and Time Delay},
          author={Liu, Junli and Lv, Pan and Liu, Bairu and Zhang, Tailei and Martinez, Eulalia},
          journal={Complexity},
          volume={2021},
          pages={9184193},
          year={2021},
          doi={10.1155/2021/9184193}
        }

        @article{yang2022dynamics,
          title={Dynamics in a predator-prey model with memory effect in predator and fear effect in prey},
          author={Yang, Ruizhi and Jin, Dan},
          journal={Electronic Research Archive},
          volume={30},
          number={4},
          pages={1322--1339},
          year={2022},
          doi={10.3934/era.2022069}
        }

        @article{kundu2018impact,
          title={Impact of Fear Effect in a Discrete-Time Predator-Prey System},
          author={Kundu, S. and Pal, N. and Samanta, S.},
          journal={Bulletin of the Calcutta Mathematical Society},
          year={2018}
        }

        @article{shi2024delay,
          title={一类带有恐惧效应时滞的捕食者-猎物系统的动力学},
          author={石仟 and 胡宗萍},
          journal={应用数学学报},
          year={2024},
          doi={10.20142/j.cnki.amas.202401083}
        }

        @article{wang2017adaptive,
          title={Modeling the Fear Effect in Predator-Prey Interactions with Adaptive Avoidance of Predators},
          author={Wang, Xiaoying and Zou, Xingfu},
          journal={Bulletin of Mathematical Biology},
          year={2017},
          doi={10.1007/s11538-017-0287-0}
        }

        @article{panday2018stability,
          title={Stability and Bifurcation Analysis of a Three-Species Food Chain Model with Fear},
          author={Panday, Pijush and Pal, Nikhil and Samanta, Sudip and Chattopadhyay, Joydev},
          journal={International Journal of Bifurcation and Chaos},
          volume={28},
          year={2018},
          doi={10.1142/S0218127418500098}
        }

        @article{zhao2025dynamics,
          title={Dynamics analysis of a predator-prey model incorporating fear effect in prey species},
          author={Zhao, Xiaoyan and Yu, Liangru and Li, Xue-Zhi},
          journal={AIMS Mathematics},
          volume={10},
          number={5},
          pages={12464--12492},
          year={2025},
          doi={10.3934/math.2025563}
        }
        """
    ).strip()
    (root / "references.bib").write_text(bib + "\n", encoding="utf-8")


def write_configs(root: Path) -> None:
    configs = root / "configs"
    configs.mkdir(exist_ok=True)
    (configs / "baseline_literature.yaml").write_text(
        dedent(
            """
            r: 0.1
            d1: 0.01
            d2: 0.01
            p_pred: 0.5
            h_handle: 0.6
            eta: 0.4
            d3: 0.22
            x0: 4.0
            y0: 0.5
            z0: 0.5
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (configs / "baseline_user_current.yaml").write_text(
        dedent(
            """
            # Original compatibility values: r=0.5, K=100, c=0.8, a=10, eta=0.5, d=0.3.
            # Converted to p*x*y/(1+h*x): p_pred=c/a=0.08, h_handle=1/a=0.1.
            r: 0.5
            d1: 0.0
            d2: 0.005
            p_pred: 0.08
            h_handle: 0.1
            eta: 0.5
            d3: 0.3
            x0: 30.0
            y0: 10.0
            z0: 10.0
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (configs / "search_ranges.yaml").write_text(
        dedent(
            """
            k_grid: [0, 20, 101]
            alpha_grid_log10: [-2, 0.69897, 65]
            random_ranges:
              r: [0.05, 2.0]
              d1: [0.0, 0.5]
              d2: [0.001, 0.2]
              p_pred: [0.05, 2.0]
              h_handle: [0.0, 1.0]
              eta: [0.05, 1.0]
              d3: [0.01, 1.0]
              k_fear: [0.0, 20.0]
              alpha_mem: [0.01, 5.0]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (configs / "tritrophic.yaml").write_text(
        dedent(
            """
            r: 0.8
            dX: 0.05
            aX: 0.01
            p1: 0.6
            h1: 0.08
            eta1: 0.45
            dY: 0.12
            p2: 0.45
            h2: 0.1
            eta2: 0.35
            dZ: 0.08
            k1: 0.4
            k2: 0.3
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def write_readme(root: Path) -> None:
    (root / "README.md").write_text(
        dedent(
            """
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
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def write_requirements(root: Path) -> None:
    (root / "requirements.txt").write_text("numpy\npandas\nscipy\nmatplotlib\nPyYAML\n", encoding="utf-8")


def write_report(root: Path, scan_k: pd.DataFrame, reps: pd.DataFrame, class_counts: pd.Series) -> None:
    report_dir = root / "report"
    report_dir.mkdir(exist_ok=True)
    y0 = scan_k.iloc[0]["y_mean"]
    y_end = scan_k.iloc[-1]["y_mean"]
    amp0 = scan_k.iloc[0]["y_amp"]
    amp_end = scan_k.iloc[-1]["y_amp"]
    counts_text = "，".join(f"{idx}: {int(val)}" for idx, val in class_counts.items())
    reps_text = "\n".join(
        f"- {row.case_id}: k={row.k_fear:.3g}, alpha={row.alpha_mem:.3g}, class={row['class']}, y_mean={row.y_mean:.4g}, y_amp={row.y_amp:.4g}"
        for _, row in reps.iterrows()
    )
    md = dedent(
        f"""
        # 恐惧效应与记忆反馈下捕食者-猎物系统的动力学建模与稳定性分析

        ## 摘要

        本文在经典捕食者-猎物模型基础上引入非消耗性的恐惧效应，并用风险记忆变量描述猎物对历史捕食压力的平滑感知。主模型按 M0 无恐惧、M1 即时恐惧、M2 记忆恐惧三层递进建立，三级食物链作为扩展模块。理论分析给出正性、有界性、共存平衡、Jacobian 和 Routh-Hurwitz 稳定条件；数值部分通过 k 扫描、k-alpha 二参数热力图、理论边界对照和恐惧函数鲁棒性比较研究系统行为。

        ## 1. 问题背景

        捕食者不只通过捕食直接减少猎物数量，也会通过风险信号改变猎物觅食、繁殖和活动区域。Lima 与 Dill 的综述说明动物会在生态时间尺度上评估捕食风险；Preisser 与 Bolnick 将这类影响概括为非消耗效应；Zanette 等的鸣禽实验证明，仅感知捕食风险即可使年后代数量下降约 40%。因此，数学建模时有必要把“捕食者数量 -> 感知风险 -> 繁殖下降 -> 种群动力学改变”作为独立机制写入模型。

        ## 2. 文献综述

        Wang、Zanette 与 Zou (2016) 是本文最重要的数学来源，其模型用 `f(k,y)=1/(1+ky)` 降低猎物出生率，并证明 Holling II 捕食下恐惧可改变 Hopf 分岔和稳定性。Liu 等 (2021) 在 Holling II 与恐惧基础上加入妊娠时滞，给出可借鉴的参数组和 k 分岔图。Yang 与 Jin (2022) 研究的是 PDE 空间记忆和猎物恐惧，本文只借鉴“记忆改变稳定性”的思想，将其化简为 ODE 风险记忆变量。Panday 等 (2018) 提供三级食物链中双重恐惧效应的扩展思路。Zhao、Yu 与 Li (2025) 的扩散与 Turing 结果作为未来空间扩展参考。

        ## 3. 模型假设与符号说明

        基本假设为：系统封闭；空间均匀；时间连续；猎物无捕食者时有出生、自然死亡和种内竞争；捕食者依赖猎物增长；捕食函数采用 Holling II；恐惧不直接杀死猎物，而降低有效出生率；`z(t)` 是历史捕食者密度的平滑风险记忆，不是第三个物种；所有主要参数非负，初始密度为正；数值模拟用于机制研究，不做真实预测。

        变量 `x(t)` 为猎物密度，`y(t)` 为捕食者密度，`z(t)` 为感知风险。参数 `r,d1,d2,p,h,eta,d3,k,alpha` 分别表示猎物最大出生率、自然死亡率、种内竞争、捕食强度、处理时间参数、转化效率、捕食者死亡率、恐惧强度和记忆更新速率。

        ## 4. 模型建立

        M0 无恐惧模型为

        ```text
        x' = r x - d1 x - d2 x^2 - p x y/(1+h x)
        y' = eta p x y/(1+h x) - d3 y
        ```

        M1 即时恐惧模型令 `z=y`：

        ```text
        x' = r x/(1+k y) - d1 x - d2 x^2 - p x y/(1+h x)
        y' = eta p x y/(1+h x) - d3 y
        ```

        M2 记忆恐惧模型为

        ```text
        x' = r x/(1+k z) - d1 x - d2 x^2 - p x y/(1+h x)
        y' = eta p x y/(1+h x) - d3 y
        z' = alpha (y-z)
        ```

        其中 alpha 越大，风险记忆越快跟随当前捕食者数量，记忆越短；alpha 越小，更新越慢，记忆越长。

        三级扩展 M3 使用底层猎物 `X`、中间捕食者 `Y`、顶级捕食者 `Z`，在 `X` 的出生项加入 `1/(1+k1 Y)`，在 `Y` 由捕食底层猎物获得的增长项加入 `1/(1+k2 Z)`。

        ## 5. 理论分析

        ### 5.1 正性

        在坐标平面上，若 `x=0` 则 `x'=0`，若 `y=0` 则 `y'=0`；对记忆变量，`z'=alpha(y-z)`，当 `z=0` 且 `y>0` 时有 `z'>0`。因此非负区域是不变的。也可写成指数形式：`y(t)=y(0)exp(∫(eta p x/(1+hx)-d3)dt)`，所以正初值保持正性；`x` 的方程也可写为 `x'=x Q(x,y,z)`，从而不会穿过 `x=0`。

        ### 5.2 有界性

        因为恐惧项不超过 1 且捕食项非负，

        ```text
        x' <= (r-d1)x - d2 x^2
        ```

        当 `r>d1` 时得到 `limsup x(t) <= (r-d1)/d2`。令 `W=eta x+y`，直接捕食项在组合中抵消，可得到 `W` 受一个线性耗散不等式控制，因此 `y(t)` 最终有界。又因为 `z'=alpha(y-z)` 是对 `y` 的指数加权平均，`y` 有界时 `z` 也有界。

        ### 5.3 平衡点

        灭绝平衡为 `E0=(0,0,0)`。若 `r>d1`，猎物单独存在平衡为 `E1=((r-d1)/d2,0,0)`。正平衡满足 `z*=y*`，且由捕食者方程得到

        ```text
        x* = d3/(eta p - d3 h),  eta p > d3 h.
        ```

        令 `B=p/(1+h x*)`，`H=d1+d2 x*`，猎物方程化为

        ```text
        B k (y*)^2 + (B+kH)y* + (H-r)=0.
        ```

        当 `r>H` 时正根存在；`k=0` 时 `y*=(r-H)/B`。

        ### 5.4 即时恐惧模型稳定性

        在 M1 正平衡处，

        ```text
        Fx = r/(1+k y*) - d1 - 2 d2 x* - p y*/(1+h x*)^2
        Fy = -r k x*/(1+k y*)^2 - p x*/(1+h x*) < 0
        Gx = eta p y*/(1+h x*)^2 > 0
        Gy = eta p x*/(1+h x*) - d3 = 0
        ```

        因此 `det J=-Fy Gx>0`，局部稳定主要由 `tr J=Fx` 决定；`Fx=0` 是可能的 Hopf 临界条件。

        ### 5.5 记忆模型 Routh-Hurwitz 条件

        M2 的 Jacobian 写成

        ```text
        J = [[A, B, C],
             [D, 0, 0],
             [0, alpha, -alpha]]
        ```

        其中

        ```text
        A = r/(1+kz*) - d1 - 2d2x* - p y*/(1+h x*)^2
        B = -p x*/(1+h x*)
        C = -r k x*/(1+kz*)^2
        D = eta p y*/(1+h x*)^2
        ```

        特征多项式 `lambda^3 + A1 lambda^2 + A2 lambda + A3=0`，其中

        ```text
        A1 = alpha - A
        A2 = -A alpha - B D
        A3 = -alpha D (B+C)
        ```

        稳定条件为 `A1>0, A2>0, A3>0, A1 A2>A3`，Hopf 临界边界可由 `A1 A2=A3` 给出。图 9 将该理论边界叠加到数值分类热力图上。

        ## 6. 数值模拟

        程序优先使用 `scipy.integrate.solve_ivp` 的 DOP853 方法；二维大网格扫描用向量化 RK4 提高复现速度。尾部区间计算均值、最大最小值、振幅和相对振幅，并按稳定共存、振荡共存、灭绝、低密度风险和无效分类。

        本次 `k` 扫描中，首端捕食者尾部均值约为 `{y0:.4g}`，末端约为 `{y_end:.4g}`；捕食者尾部振幅从 `{amp0:.4g}` 变化到 `{amp_end:.4g}`。这说明恐惧强度改变了捕食者平均密度和振荡强度，但具体方向依赖参数区域。

        k-alpha 二参数扫描分类计数为：{counts_text}。

        代表性参数为：

        {reps_text}

        图 7 显示了稳定、振荡和低密度风险区域的分布；图 8 用连续振幅展示分类图中不易看出的振荡强弱；图 9 表明 Routh-Hurwitz 边界与数值稳定区域大体对应，但在有限时间、长周期或低密度风险附近会出现差异。

        ## 7. 三级食物链扩展

        M3 表明，在多营养级食物链中，恐惧不只影响底层猎物，也可能通过中间捕食者对顶级捕食者的风险响应改变能量传递。本文只做时间序列和 `(k1,k2)` 扫描，不对三级模型做完整理论证明。

        ## 8. 讨论

        恐惧强度增加通常会降低捕食者可获得的猎物出生补给，因此常见结果是捕食者平均密度或峰值下降；在部分参数区间，高恐惧会使极限环收缩并趋于稳定平衡，这与 Wang 2016 和 Liu 2021 的经典叙事一致。但恐惧并不总是稳定系统：若参数落在强振荡区域，恐惧可能主要降低峰值而仍保留周期振荡。记忆变量不改变正平衡的位置，因为平衡时 `z*=y*`；但它改变 Jacobian 的第三个特征方向，长记忆可能产生反馈滞后，使振荡拉长、放大或带来低密度风险。将恐惧函数换成指数型或二次有理型后，主要定性结论仍保留，说明结果不是单一函数形式造成的。

        ## 9. 结论

        本文构建了无恐惧、即时恐惧和记忆恐惧三个层级模型，并实现了三级食物链扩展。理论分析表明，正共存平衡的存在依赖于 `eta p>d3 h` 和 `r>d1+d2x*`；记忆不改变平衡点位置，但会通过 Routh-Hurwitz 条件改变稳定性。数值模拟显示，恐惧强度和记忆速率共同决定系统处于稳定共存、振荡共存还是低密度风险区域。本文结论是机制模拟和定性分析，不代表对真实生态系统的精确预测。

        ## 参考文献

        见项目根目录 `references.bib` 和 `literature/literature_table.md`。
        """
    ).strip()
    md = "\n".join(line[8:] if line.startswith("        ") else line for line in md.splitlines())
    (report_dir / "report.md").write_text(md + "\n", encoding="utf-8")
    tex = (
        "\\documentclass[UTF8]{ctexart}\n"
        "\\usepackage{amsmath,amssymb,graphicx,geometry}\n"
        "\\geometry{margin=2.4cm}\n"
        "\\title{恐惧效应与记忆反馈下捕食者--猎物系统的动力学建模与稳定性分析}\n"
        "\\author{}\n\\date{}\n\\begin{document}\n\\maketitle\n"
        "\\section*{说明}\n完整报告正文见 report.md；本文件保留主要公式与图表插入入口，便于后续用 XeLaTeX 排版。\n"
        "\\section*{主模型}\n\\[\n\\begin{cases}\n"
        "x'=\\dfrac{rx}{1+kz}-d_1x-d_2x^2-\\dfrac{pxy}{1+hx},\\\\\n"
        "y'=\\eta\\dfrac{pxy}{1+hx}-d_3y,\\\\\n"
        "z'=\\alpha(y-z).\n\\end{cases}\n\\]\n"
        "\\section*{Routh--Hurwitz 条件}\n\\[\nA_1=\\alpha-A,\\quad A_2=-A\\alpha-BD,\\quad A_3=-\\alpha D(B+C),\n\\]\n"
        "\\[\nA_1>0,\\quad A_2>0,\\quad A_3>0,\\quad A_1A_2>A_3.\n\\]\n"
        "\\end{document}\n"
    )
    (report_dir / "report.tex").write_text(tex, encoding="utf-8")


def write_simple_report_pdf(root: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.font_manager import FontProperties

    report_md = (root / "report" / "report.md").read_text(encoding="utf-8")
    font_candidates = [
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
    ]
    font_path = next((path for path in font_candidates if path.exists()), None)
    font_prop = FontProperties(fname=str(font_path), size=8.5) if font_path else FontProperties(size=8.5)
    chunks = []
    current = []
    for line in report_md.splitlines():
        current.append(line)
        if len(current) >= 34:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    with PdfPages(root / "report" / "report.pdf") as pdf:
        for chunk in chunks:
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.95, chunk, va="top", ha="left", fontproperties=font_prop, wrap=True)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
