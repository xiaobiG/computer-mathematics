---
title: 迭代解线性方程组：Jacobi、Gauss–Seidel 与收敛证据
description: 从 Ax=b 的逐行重排推导两种驻定迭代，解释严格对角占优、残差、步长与发散系统，并实现可检查的迭代轨迹。
courseLevel: 2
prerequisites: 矩阵乘法、线性方程组、范数、浮点误差
estimatedMinutes: 60
experiment: projects/floating_point_museum/linear_iterations.py
---

# 迭代解线性方程组：Jacobi、Gauss–Seidel 与收敛证据

## 学习目标

读完后，你能从 $Ax=b$ 逐行推导 Jacobi 与 Gauss–Seidel 更新；用残差和更新量共同判断停止；知道严格对角占优是充分条件而非必要条件；并能识别一个会发散的迭代系统。

## 从“大矩阵不能直接求逆”开始

电路、网格模拟和推荐系统经常要求解 $Ax=b$。直接写 `inverse(A) @ b` 既浪费计算，也会把数值误差放大；大型稀疏系统通常只希望通过矩阵—向量运算逐步逼近解。迭代法的代价是：它不保证每个系统都会收敛，因此程序必须能给出收敛证据或明确失败。

## 定义与直觉

把 $A=D+L+U$ 分成对角、严格下三角和严格上三角部分。第 $i$ 行

$$a_{ii}x_i+\sum_{j\ne i}a_{ij}x_j=b_i$$

可重排为

$$x_i=\frac{b_i-\sum_{j\ne i}a_{ij}x_j}{a_{ii}}.$$

这要求 $a_{ii}\ne0$。Jacobi 在第 $k+1$ 轮的每一行都只用旧向量 $x^{(k)}$：

$$x^{(k+1)}=D^{-1}(b-(L+U)x^{(k)}).$$

Gauss–Seidel 计算到第 $i$ 行时立即使用本轮已更新的 $x_1^{(k+1)},\ldots,x_{i-1}^{(k+1)}$：

$$x^{(k+1)}=(D+L)^{-1}(b-Ux^{(k)}).$$

所以 Jacobi 的一轮天然可并行，Gauss–Seidel 的一轮有顺序依赖，却常在相同问题上更快。

## 手算一轮

考虑

$$\begin{bmatrix}4&-1\\-1&3\end{bmatrix}x=
\begin{bmatrix}15\\10\end{bmatrix},\qquad x^{(0)}=(0,0).$$

Jacobi 给出 $x^{(1)}=(15/4,10/3)$。第二轮第一分量仍使用旧的 $10/3$，所以为 $(15+10/3)/4$。Gauss–Seidel 的第二分量则立刻使用新的 $15/4$，变为 $(10+15/4)/3$。同一行方程、不同的信息更新时间，造成不同的收敛轨迹。

## 为什么有时会收敛

若每一行严格对角占优：

$$|a_{ii}|>\sum_{j\ne i}|a_{ij}|,$$

则 Jacobi 和 Gauss–Seidel 都收敛。这是很易检查的**充分**条件，不是必要条件；许多非对角占优矩阵也会收敛。更一般地，迭代矩阵的谱半径小于一才是收敛条件：Jacobi 为 $\rho(-D^{-1}(L+U))<1$。

反例 $A=\begin{bmatrix}1&2\\2&1\end{bmatrix}$、$b=(1,1)$ 没有对角占优。从零开始的 Jacobi 更新会反复放大旧误差；把 `max_steps` 用尽后仍无足够小残差，程序应报失败，而非返回最后一个数字。

## 可运行实现与验证

```python
from projects.floating_point_museum.linear_iterations import solve_iteratively

A = [[4.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 3.0]]
b = [15.0, 10.0, 10.0]
solution, trace = solve_iteratively(A, b, method="gauss-seidel")
assert max(abs(value - 5.0) for value in solution) < 1e-8
print(trace[-1])
```

运行 `python -m unittest projects.floating_point_museum.test_linear_iterations`。实现返回完整轨迹；每项包含迭代编号、$\lVert x^{(k+1)}-x^{(k)}\rVert_\infty$ 和 $\lVert b-Ax^{(k+1)}\rVert_\infty$。测试验证两种算法能解严格对角占优系统、Gauss–Seidel 在这个固定系统上不需更多轮、残差定义正确，以及发散/零对角/错误方法会显式失败。

每轮稠密实现为 $O(n^2)$ 时间、$O(n)$ 额外空间，$k$ 轮总计 $O(kn^2)$。对稀疏矩阵应只遍历非零元，使每轮成本接近 $O(\operatorname{nnz}(A))$。

## 停止准则、正确性与工程边界

残差 $r=b-Ax$ 测量“代回原方程是否一致”；更新量测量“迭代是否仍在移动”。只检查小步长会把停滞误判成收敛；只检查小残差也要考虑问题的条件数：

$$\frac{\lVert x-\hat{x}\rVert}{\lVert x\rVert}\lesssim\kappa(A)\frac{\lVert b-A\hat{x}\rVert}{\lVert b\rVert}.$$

病态矩阵可有很小残差却仍有较大前向误差。因此实现同时要求相对步长与残差低于容差，并保留最大轮数。返回的解是一个经过两类数值证据审查的近似值，不是符号意义的“已证明精确解”。

## 常见误区

- **“非对角占优必然发散”**：严格对角占优只是容易验证的充分条件。
- **“Gauss–Seidel 总更快”**：常见但不保证；它还降低了并行度。
- **“小残差等于小解误差”**：条件数大时不成立，需连接[条件数](/numerical-computing/condition-number)。
- **“求逆后相乘是通用解法”**：应使用分解或迭代求解，避免显式逆。

## 练习

1. **基础**：对手算系统完成 Jacobi 的第二轮，并与 Gauss–Seidel 的第二个分量比较。
2. **推导**：从逐行重排推导 $(D+L)x^{(k+1)}=b-Ux^{(k)}$。
3. **编码**：给轨迹加入相对残差，并为一个零对角输入写测试。
4. **开放**：将矩阵改成稀疏邻接结构，比较 Jacobi 的并行优势与 Gauss–Seidel 的数据依赖；说明何时应选择共轭梯度或预条件方法。

## 下一步

[条件数](/numerical-computing/condition-number)解释为什么残差不能独自保证答案质量；[浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)给出停止契约的工程写法。继续可学习主元消元、QR/SVD 与 Krylov 子空间方法。
