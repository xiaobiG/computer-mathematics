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
from projects.linear_algebra_lab.main import solve


def intersection(epsilon, right_side):
    # x + y = 2; x + (1 + epsilon)y = right_side
    return solve([[1, 1], [1, 1 + epsilon]], [2, right_side])


first = intersection(1e-8, 2 + 1e-8)
second = intersection(1e-8, 2 + 2e-8)
assert abs(first[1] - second[1]) > 0.1
```

这里的消元为 $O(n^3)$；条件数的精确计算通常也需要分解或迭代估计，生产程序往往只估计它，而非显式求逆矩阵。

## 前向误差、后向误差与工程边界

**前向误差**比较计算结果与真解；**后向误差**问“计算结果是否恰好解了一个很接近的输入问题”。后向稳定算法在良态问题上通常给出小前向误差，但再稳定的算法也无法挽救巨大条件数。正规方程会近似平方条件数，因此[最小二乘](/linear-algebra/least-squares)中常优先 QR/SVD；消元中选主元也是降低算法额外误差，而不是改变问题条件数。

## 常见误区

- 条件数大不代表程序必然错误，而是输出需要报告不确定性。
- 残差小不一定表示解准确，病态系统可有小残差和大前向误差。
- 将“稳定算法”误解为“任何输入都稳定”。

## 练习

1. **基础**：改变例子中的 `right_side`，观察解随 $\epsilon$ 变小时如何放大。
2. **推导**：证明若 $A$ 是正交矩阵，在 2-范数下 $\kappa(A)=1$。
3. **编码**：用实验室的 `solve` 对两个接近奇异的系统比较残差和解的变化。
4. **开放**：解释为何特征标准化可改善某些建模问题，却不必然消除所有病态性。

## 延伸与下一步

条件数描述问题，算法稳定性描述计算过程。[Kahan 求和](/numerical-computing/kahan-summation)展示如何通过改写算法降低不必要的舍入误差。
