# Final Report Blueprint

## Title direction

Use a title that makes the core contribution explicit. A strong default is:

`恐惧效应与记忆反馈下捕食者-猎物系统的动力学建模与稳定性分析`

This is better than a broad title because it says exactly what the main model adds.

## Recommended chapter structure

### 1. 问题背景与课程要求理解

Write this section around the assignment, not only around the literature.

State clearly:

- the course asks for mechanism-based modeling
- real-data fitting is optional, not mandatory
- the main task is to analyze how fear and memory alter long-term dynamics

### 2. 文献综述与建模切入点

Recommended structure:

- behavioral ecology basis: fear is a real ecological mechanism
- mathematical fear models: Wang 2016 as the main starting point
- delay and memory motivation: Liu 2021, Yang and Jin 2022
- broader extensions: Panday 2018, Zhao 2025

End the section with:

- what is already known
- what your course project will do in a simpler but rigorous way

### 3. 模型假设与符号说明

This section should be explicit and compact.

Must include:

- system is closed
- environment is spatially homogeneous in the main model
- fear affects prey effective reproduction rather than direct mortality
- `z(t)` is perceived risk memory, not a species
- main analysis is mechanism-oriented rather than predictive

### 4. 模型建立

Best presentation order:

1. `M0` no-fear baseline
2. `M1` instant fear
3. `M2` memory fear
4. `M3` tritrophic extension

This progression makes the project easy to read.

### 5. 理论分析

This is where the paper gains rigor.

Recommended subsections:

- positivity
- boundedness
- existence of equilibria
- Jacobian matrix
- local stability
- Routh-Hurwitz conditions for `M2`

Important:

- do not overclaim global theory if it is not fully derived
- say clearly when an extension model is only explored numerically

### 6. 数值方法与判别标准

Explain:

- ODE solver strategy
- vectorized scan approximation
- tail-window metrics
- classification logic

This section matters because it makes the numerical results look designed rather than improvised.

### 7. 主要结果

Recommended order:

1. baseline time-series comparison
2. `k` scan
3. `k-alpha` scan
4. theory overlay
5. robustness across fear functions
6. representative cases

For each figure, answer one question only.

### 8. 扩展结果

Keep extensions in one chapter, not scattered.

Suggested order:

- tritrophic extension
- delay extension
- Leslie-Gower comparison
- discrete-time comparison

Frame them as:

- evidence of breadth
- structural robustness checks
- future work directions

not as separate core theses

### 9. 讨论

This is where a high-quality course paper separates itself from a script dump.

Discuss:

- why fear can stabilize in some regions but not all
- why memory changes stability without moving the equilibrium
- why numerical and theoretical boundaries are close but not identical
- why the main phase map uses `alpha in [10^-2, 5]` rather than an arbitrarily larger stiff region
- what the simplified memory variable means biologically

### 10. 结论

The conclusion should center on one sentence:

Fear and memory jointly reshape predator-prey dynamics, and memory-mediated fear can stabilize, preserve, or destabilize coexistence depending on the parameter regime.

## Writing rules for a strong final draft

- every major claim should point to a formula, figure, or table
- every extension should justify why it exists
- every limitation should be stated calmly and explicitly
- do not let the report read like four separate mini-projects

## Suggested figure order

1. mechanism diagram
2. model-layer diagram
3. baseline and representative time series
4. phase portraits
5. `k` bifurcation-style extrema
6. mean density and amplitude vs `k`
7. `k-alpha` classification heatmap
8. amplitude heatmap
9. theory boundary overlay
10. robustness comparison
11. empirical scale calibration
12. tritrophic extension
13. delay extension
14. Leslie-Gower extension
15. discrete extension

## Suggested table order

1. symbol table
2. main parameter set
3. classification rule summary
4. representative cases
5. extension-model parameter summary
