---
courseLevel: "2–3（推导与工程）"
prerequisites: "投影、转置与线性方程组"
estimatedMinutes: 60
experiment: "比较正规方程、QR 与 SVD 拟合"
title: 最小二乘：没有精确解怎么办
description: 从正交投影推导正规方程，并理解 QR 与 SVD 的数值边界。
---

# 最小二乘：没有精确解怎么办

## 学习目标

- 将拟合问题写为最小化残差 $\lVert Ax-b\rVert^2$；
- 从正交投影推导正规方程；
- 知道何时不应直接求解 $A^TAx=A^Tb$。

## 从一个计算问题开始

测得点 $(0,1),(1,2),(2,2)$ 不在同一直线上。程序不该要求一条恰好经过所有点的直线，而应寻找总体误差最小的直线。

## 定义与推导

令 $A$ 的列为可用特征方向，$A\hat x$ 是对 $b$ 的近似。最优残差 $r=b-A\hat x$ 必与每个列方向正交：

$$A^T(b-A\hat x)=0\quad\Longrightarrow\quad A^TA\hat x=A^Tb.$$

这不是“先求逆”的许可，而是投影的代数描述。若 $A$ 列满秩，理论解为 $(A^TA)^{-1}A^Tb$；实现中通常解方程，而不显式求逆。

## 手算一个完整例子

拟合 $y=ax+c$ 时，令 $A=\begin{bmatrix}0&1\\1&1\\2&1\end{bmatrix}$、$b=(1,2,2)^T$。先计算 $A^TA=\begin{bmatrix}5&3\\3&3\end{bmatrix}$ 与 $A^Tb=(6,5)^T$，再解二元系统即可得到最小二乘直线。残差不必为零，但它与 $A$ 的两列都正交。

## 把公式实现为代码

```python
def residual_sum_squares(a, b, x):
    residual = [sum(row[j] * x[j] for j in range(len(x))) - target
                for row, target in zip(a, b)]
    return sum(value * value for value in residual)

assert residual_sum_squares([[1]], [3], [3]) == 0
```

构造正规方程的密集成本约为 $O(mn^2)$；随后求解 $n\times n$ 系统为 $O(n^3)$。

## 失败案例与工程边界

正规方程会近似平方条件数，近似共线的特征可能使小误差被放大。生产数值代码优先用 QR 或 SVD；特征尺度相差很大时先标准化。最小二乘最小化平方误差，对离群点敏感，鲁棒回归是另一种目标。

## 常见误区

- “最小二乘”不保证每个点误差最小，只保证平方和最小。
- 不要显式计算矩阵逆。
- 残差与 $b$ 不必正交，而是与列空间正交。

## 练习

1. 完成例子中的二元系统并验证两个正交条件。
2. 给一个重复特征列，解释为什么正规方程奇异。
3. 用 QR/SVD 库函数与正规方程比较病态输入。

## 下一步

投影选择的是一个子空间；[特征值与 PCA](/linear-algebra/eigenvalues-pca)将寻找最值得保留的子空间方向。
