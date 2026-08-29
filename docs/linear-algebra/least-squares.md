---
courseLevel: "2–3（推导与工程）"
prerequisites: "投影、转置与线性方程组"
estimatedMinutes: 60
experiment: "以同一拟合题比较正规方程与 QR，并验证 A^Tr=0"
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

实验室提供一条用于对照推导的正规方程路径，以及不显式形成 $A^TA$ 的 QR 路径：

```python
from projects.linear_algebra_lab.main import least_squares_comparison_report

A = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
report = least_squares_comparison_report(A, [1.0, 2.0, 2.0])

assert report["solution_distance"] < 1e-12
assert max(abs(value) for value in report["normal_normal_equation_residual"]) < 1e-12
assert max(abs(value) for value in report["qr_normal_equation_residual"]) < 1e-12
```

报告的两组 `*_normal_equation_residual` 都是 $A^Tr$：它们接近零，才说明相应路径确实达到最小二乘的一阶最优性条件。`least_squares_normal_equations` 有意调用带选主元的方程求解器，便于核对推导；`least_squares_qr` 以改进 Gram–Schmidt 得到 $A=QR$，计算 $Q^Tb$ 后对上三角 $R$ 回代，才是默认应选的数值路径。运行 `python -m unittest projects.linear_algebra_lab.test_main` 可验证小例解、两条路径的一致性、正交残差、秩亏列和宽矩阵边界。

构造正规方程或 QR 的密集成本都约为 $O(mn^2)$；随后求解 $n\times n$ 系统为 $O(n^3)$。QR 避免了正规方程将条件数近似平方的额外放大。

## 正确性证据与数值选择

对列满秩的 $A$，凸二次目标只有一个驻点；$A^Tr=0$ 因而既是正规方程的残差，也是最小解的证书。示例报告同时检查正规方程与 QR 的该证书，并报告两组系数的距离。这个小而良态的例子中两条路径应相同；若特征近似共线，二者的数值结果可能开始分离，这正是应该选择 QR 或 SVD 的信号，而不是把差异平均掉。

## 失败案例与工程边界

正规方程会近似平方条件数，近似共线的特征可能使小误差被放大。生产数值代码优先用 QR 或 SVD；特征尺度相差很大时先标准化。最小二乘最小化平方误差，对离群点敏感，鲁棒回归是另一种目标。

## 常见误区

- “最小二乘”不保证每个点误差最小，只保证平方和最小。
- 不要显式计算矩阵逆。
- 残差与 $b$ 不必正交，而是与列空间正交。

## 练习

1. **基础**：完成例子中的二元系统并验证两个正交条件。
2. **推导**：由 $A=QR$ 和 $Q^TQ=I$ 推导 $R\hat x=Q^Tb$。
3. **编码**：给 `least_squares_qr` 增加一组带截距的线性拟合测试，并检查 $A^Tr$。
4. **开放**：用 QR/SVD 库函数与正规方程比较病态输入的残差与前向误差。

## 下一步

投影选择的是一个子空间；[特征值与 PCA](/linear-algebra/eigenvalues-pca)将寻找最值得保留的子空间方向。
