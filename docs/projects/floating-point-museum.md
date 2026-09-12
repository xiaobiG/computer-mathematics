---
title: 项目：浮点数错误博物馆
description: 用可复现实验观察舍入、累计误差、消去误差与蒙特卡洛抽样波动，并验证稳定改写。
---

# 项目：浮点数错误博物馆

## 目标

这个项目收录数值程序中常见的陷阱：直接相等比较、长序列求和、相近数相减，以及把一次随机模拟当成结论。每个案例都同时提供“容易出错的写法”和更稳定的处理方式。

## 浏览器内浮点舍入实验

下面的面板把两个经典反例放在 binary64 的局部间距中观察。切换案例后，先比较结果与参考值，再看 ULP：`1e16 + 1` 不是“算错了 1”，而是 1 小于该尺度下可表达数之间的间距；`0.1 + 0.2` 的偏差则来自三个十进制常量各自的二进制近似。

<FloatingPointExplorer />

该面板直接使用浏览器的 JavaScript `Number`（IEEE 754 binary64）并实时计算相邻数间距。它用于建立直觉；精确十进制财务运算仍应使用整数最小单位或十进制定点类型，完整的可复核报告与边界测试见下方 Python 实验。

## 浏览器内病态系统实验

<ConditioningExplorer />

这个面板展示的是问题敏感性：保持近奇异矩阵不变，右端只作极小变化，精确解也可能发生数量级更大的移动。它与“无选主元消元”的算法不稳定是不同现象，详细推导见[条件数](/numerical-computing/condition-number)。

## 数学连接

- [浮点数](/numerical-computing/floating-point)：为何十进制小数常被近似存储；
- [Kahan 求和](/numerical-computing/kahan-summation)：如何补偿累计时丢失的低位；
- [直接法与选主元](/numerical-computing/direct-methods-pivoting)：为何微小主元会破坏消元轨迹；
- [条件数](/numerical-computing/condition-number)：为何有些表达式对误差天生敏感。
- [迭代解线性方程组](/numerical-computing/iterative-linear-systems)：用残差和步长一起审查 Jacobi/Gauss–Seidel 的收敛。
- [数值插值](/numerical-computing/interpolation)：用差商构造多项式，并观察外推与高阶节点的误差边界。
- [随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)：抽样误差、固定种子与重复报告。
- [牛顿法](/numerical-computing/newton-method) 与 [割线法](/numerical-computing/secant-method)：从读者声明的根任务合同选择“残差加保留区间”的受保护牛顿，或“不声称全局保证”的无导数割线。
- [数值微分](/numerical-computing/numerical-differentiation)：扫描中心差分步长，并以同一步长比较中心/前向模板在平滑内部与定义域边界的可用性。
- [数值积分](/numerical-computing/numerical-integration)：用自适应 Simpson 的叶区间、误差预算与函数调用上限审查何时真正停止。
- [多维积分的结构化采样](/numerical-computing/multidimensional-integration)：在同一二维积分基准中比较规则网格、固定种子蒙特卡洛与样本预算。
- [重要性采样诊断](/numerical-computing/importance-sampling-diagnostics)：以有真值基准审计权重退化与有效样本量。

## 运行

```bash
python projects/floating_point_museum/examples.py
python projects/floating_point_museum/simulation.py
python -m unittest projects.floating_point_museum.test_examples
python -m unittest projects.floating_point_museum.test_representation
python -m unittest projects.floating_point_museum.test_integration
python -m unittest projects.floating_point_museum.test_multidimensional_integration
python -m unittest projects.floating_point_museum.test_simulation
python -m unittest projects.floating_point_museum.test_root_finding
python -m unittest projects.floating_point_museum.test_differentiation
python -m unittest projects.floating_point_museum.test_linear_iterations
python -m unittest projects.floating_point_museum.test_stability
python -m unittest projects.floating_point_museum.test_conditioning
```

## 三个案例

1. binary64 字段、十进制转换、相邻值与 ULP：将源文本 `"0.1"` 作为精确分数与实际存储值相减，核对误差方向和半 ULP 上界；再验证 `1e16` 附近间距为 2，因此加 1 会丢失；
2. `0.1 + 0.2`：说明二进制近似与容差比较；
3. `1e16 + 1 + 1 - 1e16`：比较普通累加、Kahan 与固定归约树的 pairwise 求和；观察 pairwise 改善误差层数，却不保证修复每个抵消顺序。
4. $\sqrt{x+1}-\sqrt{x}$：通过有理化避免消去误差。
5. 单位圆蒙特卡洛：用多个固定 seed 估计 $\pi$，报告均值、样本标准差和标准误，而不是挑选一次结果。
6. 割线法：不提供导数求解 $x^2-2=0$，逐轮检查两点插值公式、事件连接和残差，并观察零割线斜率如何被拒绝。
7. 病态 $2\\times2$ 线性系统：验证右端扰动到解扰动的放大不超过条件数界，同时保持尺度无关后向残差接近零；这是条件数与后向误差不能混为一谈的反例。
8. 数值积分：以 $\sin x$ 的精确积分为预言，比较梯形法和 Simpson 法网格加密时约为 4 与 16 的误差比；自适应 Simpson 报告叶区间、最大深度、函数调用预算和独立重放证书，并拒绝奇数 Simpson 网格、非有限函数值或将预算耗尽伪装为成功。
9. 受保护牛顿法：对每一步保留的符号变化区间做审计；当牛顿建议跳出区间时回退到二分，而不是把循环或越界伪装成收敛。
10. 数值微分：扫描中心差分的十进制步长，核对粗步长区的二阶误差趋势与极小步长的舍入误差反弹；再以同一步长比较中心/前向模板，确认 $\log x$ 的左侧越界时中心模板不可用，而可计算的前向值仍须审查误差。
11. 算法稳定性：对二次方程的小根比较直接公式与 Vieta 改写，使用高精度参考值检查消去如何放大前向误差。
12. 驻定迭代：重放 Jacobi/Gauss–Seidel 的每一步向量、更新量与残差，确认停止不是由被篡改的轨迹标签触发。
13. 直接法：比较不选主元和部分选主元的增广矩阵轨迹，分别报告前向和后向误差，确认行交换不是条件数的修复。
14. 为同一个方程写两份 `diagnose_root_task` 合同：一份要求保留符号变号区间且提供导数，另一份声明无导数、只验收局部残差；解释为何后者不能继承前者的全局保证。

## 工程边界

没有“万能 epsilon”。容差必须随业务尺度、允许误差和量纲决定；随机实验还必须区分抽样波动与浮点误差。金额通常应使用最小货币单位整数或十进制定点类型。
