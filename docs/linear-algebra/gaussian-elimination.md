---
courseLevel: "2–3（算法与工程）"
prerequisites: "矩阵、线性方程组与浮点数基础"
estimatedMinutes: 60
experiment: "实现带选主元的消元与回代"
title: 高斯消元：解线性方程组
description: 用保持解集不变的行变换、选主元和回代求解线性系统。
---

# 高斯消元：解线性方程组

## 学习目标

- 将 $Ax=b$ 化为增广矩阵并消元；
- 解释部分选主元为何改善浮点计算；
- 区分唯一解、无解与无穷多解。

## 从一个计算问题开始

电路、约束布局和回归都会生成方程组。对 $2x+y=5,\ x-y=1$，消元将“同时满足”变成可逐行回代的三角结构。

## 直觉模型与严格定义

增广矩阵 $[A\mid b]$ 把每条方程的系数与右端常数放在同一行。交换两行、以非零数倍乘一行，或以一行加上另一行的倍数，都不改变解集：它们分别只是重排方程、等价缩放方程和把已知等式加到另一等式。

对例子按 $R_1\leftarrow R_1-2R_2$：

$$
\left[\begin{array}{cc|c}2&1&5\\1&-1&1\end{array}\right]
\longrightarrow
\left[\begin{array}{cc|c}0&3&3\\1&-1&1\end{array}\right].
$$

因此 $3y=3$，回代得到 $y=1,x=2$。若出现 $[0\ 0\mid c]$ 且 $c\ne0$，系统无解；若无矛盾但主元数少于变量数，则存在自由变量和无穷多解。

## 算法、正确性与复杂度

第 $k$ 列选择尚未使用行中绝对值最大的元素为主元，交换到第 $k$ 行，再对所有下方行做 $R_i\leftarrow R_i-(a_{ik}/a_{kk})R_k$。循环不变量是：已经处理的列在主元下方为零，且当前增广矩阵与原系统解集相同。循环结束后得到上三角系统；从最后一行向上回代，每一步都唯一确定一个变量，因此返回值满足原系统。

密集 $n\times n$ 系统的消元是 $O(n^3)$，回代是 $O(n^2)$，增广矩阵额外占用 $O(n^2)$ 空间。

## 把算法实现为代码

```python
from projects.linear_algebra_lab.main import (
    classify_linear_system,
    pivot_trace_certificate,
    solve_with_pivot_trace,
)

matrix = [[1e-16, 1.0], [1.0, 1.0]]
solution, trace = solve_with_pivot_trace(matrix, [1.0, 2.0])

assert trace[0]["swapped"]             # 选中第二行的 1.0，而不是 1e-16
assert abs(trace[-1]["upper"][1][0]) < 1e-12
assert solution == [1.0, 1.0]
assert pivot_trace_certificate(matrix, [1.0, 2.0], solution, trace)
assert classify_linear_system([[1, 1], [2, 2]], [2, 5]) == "none"
```

`trace` 保存每列的主元行、是否交换、消元倍数和当时的上三角增广矩阵。`pivot_trace_certificate` 从原始 $[A\mid b]$ 独立重选主元、重放行交换与消元，再回代比较解；篡改任一倍数或上三角项都会被拒绝。它让读者检查不变量，而非只相信最终答案，但并不能以小残差掩盖病态系统。[线性代数实验室](/projects/linear-algebra-lab)提供完整教学实现与自动测试。

## 失败案例与工程边界

不选主元时，上例第一步要把 $1$ 除以 $10^{-16}$，会制造约 $10^{16}$ 的倍数并放大舍入误差；部分选主元选择当前列绝对值最大的候选行，避免这个不必要的放大。它不能改变问题的[条件数](/numerical-computing/condition-number)：病态问题仍可能需要 QR、SVD 或正则化。

## 常见误区

- 把接近零的浮点数当作严格零。
- 只在失败时换行，而非每列选主元。
- 将奇异矩阵误认为数据必然错误。

## 练习

1. 对 $x+y=2,\ 2x+2y=4$ 消元并识别自由变量。
2. 构造出现 $[0\ 0\mid c]$ 的矛盾系统。
3. 修改 `solve_with_pivot_trace`，对每一步验证已处理列在主元下方都为零。
4. 在同一个病态系统上比较残差与相对前向误差，解释为什么选主元并不能让高条件数问题变良态。

## 练习答案提示

1. 第二行减去第一行的两倍；零行表示一个自由变量，而不是矛盾。
2. 让左侧两行成比例，再把右侧常数设成不同比例；检查增广列。
3. 每轮重放后只检查当前主元列的行索引大于主元行的位置，零判断必须使用既定容差。
4. 以同一精确解构造 $b$，分别报告 $\lVert b-A\hat x\rVert$ 与 $\lVert x-\hat x\rVert/\lVert x\rVert$；两者不能互相替代。

## 下一步

当 $Ax=b$ 无精确解时，转向[最小二乘](/linear-algebra/least-squares)最小化残差。
