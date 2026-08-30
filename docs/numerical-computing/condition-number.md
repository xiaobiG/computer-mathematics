---
courseLevel: "2–3（误差分析与工程）"
prerequisites: "相对误差、矩阵与范数"
estimatedMinutes: 60
experiment: "比较病态问题的前向与后向误差"
title: 条件数：问题对误差有多敏感
description: 用相对误差、矩阵条件数和前向/后向误差区分病态问题与不稳定算法。
---

# 条件数：问题对误差有多敏感

## 文章元信息

- **建议阅读层级**：2–3 · 误差推导、算法选择与数值线性代数
- **前置知识**：范数、线性方程组、[浮点数表示](/numerical-computing/floating-point)
- **预计学习时间**：60 分钟
- **配套实验**：[浮点数错误博物馆](/projects/floating-point-museum)

## 学习目标

读完后，你能用相对扰动解释条件数；推导可逆矩阵的范数条件数并区分前向、后向误差；运行病态线性系统的残差与放大报告；并能说明小残差、稳定算法和准确解之间并非同义。

## 从一个计算问题开始

两条几乎平行的直线交点很远。把其中一条常数项改动百万分之一，交点可能移动数千倍：这是代码写错，还是问题本身无法可靠回答？条件数将这两个问题分开。

## 定义与推导

对函数 $f$，局部相对条件数近似衡量输入相对扰动如何放大为输出相对扰动：

$$\frac{\lVert\delta f\rVert}{\lVert f\rVert}
\lesssim \kappa\frac{\lVert\delta x\rVert}{\lVert x\rVert}.$$

对于可逆矩阵线性系统 $Ax=b$，在相容范数下

$$\kappa(A)=\lVert A\rVert\lVert A^{-1}\rVert.$$

由 $(A+\delta A)(x+\delta x)=b$ 的一阶近似可得：当 $\lVert A^{-1}\delta A\rVert$ 很小时，解的相对变化受约为 $\kappa(A)$ 倍的相对矩阵扰动控制。接近奇异时 $A^{-1}$ 很大，条件数随之爆炸。

## 算法实验与复杂度

```python
from projects.floating_point_museum.conditioning import perturbation_report


epsilon = 1e-6
report = perturbation_report(
    [[1.0, 1.0], [1.0, 1.0 + epsilon]],
    [2.0, 2.0 + epsilon],       # 真解为 [1, 1]
    [2.0, 2.0 + 2.0 * epsilon], # 右端只多了 epsilon
)

assert report["relative_rhs_change"] < 1e-6
assert report["relative_solution_change"] > 0.9
assert report["certificate"]["observed_change_is_bounded_by_condition_number"]
assert report["certificate"]["perturbed_solution_has_small_scaled_residual"]
print(report["condition_number"])  # 约为 4_000_002
```

这份报告刻意同时给出两组解、相对扰动、观测放大倍数与条件数界。它核对

$$
\frac{\lVert\delta x\rVert_\infty}{\lVert x\rVert_\infty}
\leq
\kappa_\infty(A)
\frac{\lVert\delta b\rVert_\infty}{\lVert b\rVert_\infty},
$$

而不是只打印一个很大的条件数。输入的相对变化约为 $5\times10^{-7}$，解却从 $[1,1]$ 变到 $[0,2]$；但第二个解的残差仍接近零，因为它准确地解了**被轻微改动后的问题**。报告还给出尺度无关的残差比

$$
\eta(\hat x)=\frac{\lVert b-A\hat x\rVert_\infty}
{\lVert A\rVert_\infty\lVert\hat x\rVert_\infty+\lVert b\rVert_\infty}.
$$

小 $\eta$ 只说明方程的后向一致性；它不能反驳这个病态问题造成的大前向变化。这就是“后向看似很好、前向却不可靠”的可观察版本。

## 交互实验：拖动扰动尺度

<ConditioningExplorer />

面板固定矩阵、只改变右端第二项的扰动尺度。注意两条柱状条为了可读性采用不同的显示缩放；应比较右侧显示的科学计数法数值，而不是比较像素长度。这里的残差为零是因为展示的 $(0,2)$ 精确满足**扰动后的**方程，绝不是说明它仍接近原问题的解。

## 矩阵也会被扰动：为什么界里多出一个分母

数值误差并不只来自右端 $b$；测量系数、离散化和浮点消元都会把 $A$ 改成 $A+\Delta A$。令原解为 $x$、扰动后解为 $x+\Delta x$，并保持右端不变：

$$
(A+\Delta A)(x+\Delta x)=b=Ax.
$$

移项后不是简单的 $A\Delta x=-\Delta A x$，而是

$$
A\Delta x=-\Delta A(x+\Delta x).
$$

设 $\delta=\lVert\Delta A\rVert/\lVert A\rVert$，取范数并把含 $\lVert\Delta x\rVert$ 的项移到左侧；当 $\kappa(A)\delta<1$ 时，得到

$$
\frac{\lVert\Delta x\rVert}{\lVert x\rVert}
\le
\frac{\kappa(A)\delta}{1-\kappa(A)\delta}.
$$

分母不是装饰：若 $\kappa(A)\delta$ 接近 1，原矩阵的逆附近可能已经不再稳定，右侧界会爆炸，不能把一阶近似当成保证。教学实验将这一条件写成可检查证书：

```python
from projects.floating_point_museum.conditioning import matrix_perturbation_report

report = matrix_perturbation_report(
    [[1.0, 0.0], [0.0, 1.0]],
    [[1.001, 0.0], [0.0, 1.0]],
    [1.0, 2.0],
)

assert report["certificate"]["bound_has_positive_margin"]
assert report["certificate"]["observed_change_is_bounded_by_matrix_perturbation"]
```

这和前一节的右端扰动报告是两种不同契约：前者固定 $A$ 并给出 $\kappa(A)\lVert\Delta b\rVert/\lVert b\rVert$，这里固定 $b$ 并必须额外检查分母的正裕量。

实验的求解和求逆都是固定 $2\times2$ 的教学公式，因而为 $O(1)$；一般 $n\times n$ 情况中，消元为 $O(n^3)$，条件数的精确计算通常也需要分解或迭代估计。生产程序往往只估计它，而非显式求逆矩阵。

## 前向误差、后向误差与工程边界

**前向误差**比较计算结果与真解；**后向误差**问“计算结果是否恰好解了一个很接近的输入问题”。上面的 `perturbed_residual_norm` 是后向诊断的一个起点，而 `relative_solution_change` 直接暴露前向敏感性。后向稳定算法在良态问题上通常给出小前向误差，但再稳定的算法也无法挽救巨大条件数。正规方程会近似平方条件数，因此[最小二乘](/linear-algebra/least-squares)中常优先 QR/SVD；消元中选主元也是降低算法额外误差，而不是改变问题条件数。

## 常见误区

- 条件数大不代表程序必然错误，而是输出需要报告不确定性。
- 残差小不一定表示解准确，病态系统可有小残差和大前向误差。
- 将“稳定算法”误解为“任何输入都稳定”。

## 练习

1. **基础**：改变例子中的 `right_side`，观察解随 $\epsilon$ 变小时如何放大。
2. **推导**：证明若 $A$ 是正交矩阵，在 2-范数下 $\kappa(A)=1$。
3. **编码**：运行 `matrix_perturbation_report`，分别报告矩阵扰动与右端扰动，并比较残差和解的变化；构造一个使 $\kappa\delta\ge1$ 的例子，确认该界被标为不可用。
4. **开放**：解释为何特征标准化可改善某些建模问题，却不必然消除所有病态性。

## 练习答案提示

1. 每次只改变一个量，并同时记录 $\lVert\delta b\rVert/\lVert b\rVert$ 与 $\lVert\delta x\rVert/\lVert x\rVert$；不要只比较解的绝对差。
2. 由 $Q^TQ=I$ 得 $Q^{-1}=Q^T$；再利用 2-范数在正交变换下不变，得到 $\lVert Q\rVert_2=\lVert Q^{-1}\rVert_2=1$。
3. 为两类扰动保留各自的相对量、解变化和尺度化残差；矩阵扰动还要检查 $1-\kappa\delta>0$，否则不能声称界成立；小残差和大解变化可以同时出现，测试应刻意覆盖这种情况。
4. 标准化可改善列尺度差异并常使优化更顺畅，但共线性、近重复样本和模型本身的不可辨识性仍会造成病态。

## 延伸与下一步

条件数描述问题，算法稳定性描述计算过程。[Kahan 求和](/numerical-computing/kahan-summation)展示如何通过改写算法降低不必要的舍入误差。
