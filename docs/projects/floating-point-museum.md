---
title: 项目：浮点数错误博物馆
description: 用可复现实验观察舍入、累计误差、消去误差与蒙特卡洛抽样波动，并验证稳定改写。
---

# 项目：浮点数错误博物馆

## 目标

这个项目收录数值程序中常见的陷阱：直接相等比较、长序列求和、相近数相减，以及把一次随机模拟当成结论。每个案例都同时提供“容易出错的写法”和更稳定的处理方式。

## 数学连接

- [浮点数](/numerical-computing/floating-point)：为何十进制小数常被近似存储；
- [Kahan 求和](/numerical-computing/kahan-summation)：如何补偿累计时丢失的低位；
- [条件数](/numerical-computing/condition-number)：为何有些表达式对误差天生敏感。
- [迭代解线性方程组](/numerical-computing/iterative-linear-systems)：用残差和步长一起审查 Jacobi/Gauss–Seidel 的收敛。
- [数值插值](/numerical-computing/interpolation)：用差商构造多项式，并观察外推与高阶节点的误差边界。
- [随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)：抽样误差、固定种子与重复报告。
- [牛顿法](/numerical-computing/newton-method)：重放每步 Newton/二分决策与符号变化区间，审查混合求根的收敛证据。
- [割线法](/numerical-computing/secant-method)：以两点插值公式、事件连接和残差审计无导数迭代。
- [数值微分](/numerical-computing/numerical-differentiation)：扫描中心差分步长，审查二阶截断趋势与极小步长的误差反弹。

## 运行

```bash
python projects/floating_point_museum/examples.py
python projects/floating_point_museum/simulation.py
python -m unittest projects.floating_point_museum.test_examples
python -m unittest projects.floating_point_museum.test_representation
python -m unittest projects.floating_point_museum.test_integration
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
8. 数值积分：以 $\sin x$ 的精确积分为预言，比较梯形法和 Simpson 法网格加密时约为 4 与 16 的误差比，并拒绝奇数 Simpson 网格和非有限函数值。
9. 受保护牛顿法：对每一步保留的符号变化区间做审计；当牛顿建议跳出区间时回退到二分，而不是把循环或越界伪装成收敛。
10. 数值微分：扫描中心差分的十进制步长，核对粗步长区的二阶误差趋势与极小步长的舍入误差反弹；域边界使双侧差分不可用时，确认接口拒绝函数值非有限的样本。
11. 算法稳定性：对二次方程的小根比较直接公式与 Vieta 改写，使用高精度参考值检查消去如何放大前向误差。
12. 驻定迭代：重放 Jacobi/Gauss–Seidel 的每一步向量、更新量与残差，确认停止不是由被篡改的轨迹标签触发。

## 工程边界

没有“万能 epsilon”。容差必须随业务尺度、允许误差和量纲决定；随机实验还必须区分抽样波动与浮点误差。金额通常应使用最小货币单位整数或十进制定点类型。
