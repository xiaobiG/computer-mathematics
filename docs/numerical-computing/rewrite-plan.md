---
title: 数值计算深度版路线
description: 从有限精度表示到稳定算法、误差分析和工程容差设计的学习路径。
---

# 数值计算深度版路线

## 主线

数值程序并非在实数上运行，而是在有限精度、有限范围和有限时间内近似计算。本专题依次区分表示误差、问题条件、算法稳定性和工程容差。

## 分层与顺序

| 层级 | 内容 | 状态 |
| --- | --- | --- |
| 0 | 二进制、范数、绝对/相对误差 | 由浮点文章补齐 |
| 1 | IEEE 754、NaN、无穷、溢出与下溢 | [浮点数表示](/numerical-computing/floating-point) 已深化 |
| 2 | 条件数、前向/后向误差、稳定性、Kahan、插值 | [条件数](/numerical-computing/condition-number)、[割线法](/numerical-computing/secant-method)与[数值插值](/numerical-computing/interpolation)已深化 |
| 3 | 主元、QR/SVD、迭代线性系统、属性测试、可复现模拟 | [迭代解线性方程组](/numerical-computing/iterative-linear-systems)、[浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)、[随机模拟与可复现性](/numerical-computing/stochastic-simulation-reproducibility)、牛顿法、数值微分与数值积分已深化；主元与 QR/SVD 由线性代数专题连接 |

## 项目连接

[浮点数错误博物馆](/projects/floating-point-museum)展示相等比较、普通/Kahan/pairwise 累计误差、消去误差、Jacobi/Gauss–Seidel 迭代轨迹、固定种子下的重复随机模拟，以及病态 $2\\times2$ 线性系统中“残差很小但解很敏感”的可复核报告。下一阶段可在此基础上补充病态线性系统的可视化对比。

## 练习

1. 为一个物理量选择绝对和相对容差，并写出量纲依据。
2. 对同一求和序列比较普通、Kahan 和 pairwise 算法。
3. 构造一个小残差但大前向误差的近奇异系统。
4. 说明如何让随机数值实验可复现并仍能探索误差分布。
