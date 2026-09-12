---
courseLevel: "2–3（算法与工程）"
prerequisites: "高斯消元与矩阵乘法"
estimatedMinutes: 55
experiment: "实现 PA=LU 并比较重复求解成本"
title: LU 分解与主元选择：把消元变成可复用的求解器
description: 从高斯消元推导 PA=LU，理解重复求解、部分选主元和数值边界。
---

# LU 分解与主元选择：把消元变成可复用的求解器

## 文章元信息

- **建议阅读层级**：2–3 · 算法分解、复杂度与数值稳定性
- **前置知识**：[高斯消元](/linear-algebra/gaussian-elimination)、[条件数](/numerical-computing/condition-number)
- **预计学习时间**：65 分钟
- **配套实验**：[线性代数实验室](/projects/linear-algebra-lab)

## 学习目标

- 将消元的乘子组织为 $L$，得到上三角 $U$；
- 用前代和回代高效解决多个右侧向量；
- 解释部分选主元为何形成 $PA=LU$，以及它不能解决什么问题。

## 从一个计算问题开始

物理仿真或多目标回归会反复使用同一个 $A$、只改变 $b$。LU 保存一次消元结果，避免重复分解。

## 定义与推导

消元中用第 $k$ 行消去第 $i$ 行的系数 $l_{ik}=a_{ik}/a_{kk}$。把对角线置为 1、下三角填入所有乘子得到下三角矩阵 $L$；消元后的上三角矩阵为 $U$。无须换行时有

$$A=LU.$$

若存在零或很小的主元，则交换行。将这些行交换组成置换矩阵 $P$，稳定的形式是

$$PA=LU.$$

解 $Ax=b$ 等价于先解 $Ly=Pb$（前代），再解 $Ux=y$（回代）。三角系统每个未知量只依赖已知量。

## 手算一个完整例子

对 $A=\begin{bmatrix}2&1\\4&3\end{bmatrix}$，消去乘子为 $l_{21}=2$：

$$L=\begin{bmatrix}1&0\\2&1\end{bmatrix},\quad U=\begin{bmatrix}2&1\\0&1\end{bmatrix},\quad LU=A.$$

若 $b=(5,11)^T$，前代给 $y_1=5,y_2=1$；回代给 $x_2=1,x_1=2$。换一个 $b$ 时 $L,U$ 保持不变，只需两次 $O(n^2)$ 的三角求解。

## 算法实现与复杂度

```python
from projects.linear_algebra_lab.lu_factorization import (
    lu_factorize,
    permuted_rows,
    solve_many_lu,
)
from projects.linear_algebra_lab.main import matmul

matrix = [[0.0, 2.0], [1.0, 3.0]]
factorization = lu_factorize(matrix)

assert factorization.permutation == [1, 0]  # 第一列必须换行
assert matmul(factorization.lower, factorization.upper) == permuted_rows(matrix, factorization.permutation)
assert solve_many_lu(factorization, [[2.0, 4.0], [4.0, 8.0]]) == [[1.0, 1.0], [2.0, 2.0]]
```

`permuted_rows` 给出 $PA$，`matmul(L,U)` 重构它。密集 $n\times n$ 分解为 $O(n^3)$、存储 $O(n^2)$；每个新右端的三角求解为 $O(n^2)$。实际实现常覆盖存储 $L,U$。

## 同一矩阵、两条工作路径

报告在同一矩阵/右端上重放“一次分解”与“每次重分解”，只计消元乘减更新和三角点积项：

```python
from projects.linear_algebra_lab.lu_factorization import lu_reuse_work_certificate, lu_reuse_work_report

matrix = [[0.0, 2.0], [1.0, 3.0]]
right_sides = [[2.0, 4.0], [4.0, 8.0]]
report = lu_reuse_work_report(matrix, right_sides)
assert report.reuse_work_units == 6
assert report.refactor_every_time_work_units == 8
assert report.solutions_match and report.pa_equals_lu
assert lu_reuse_work_certificate(matrix, right_sides, report)
```

单次分解计数为 $F=\sum_{k=0}^{n-1}(n-k-1)(n-k)$，每个右端的两次三角点积为 $T=n(n-1)$。$r$ 个右端的两条路径为 $F+rT$、$r(F+T)$，差为 $(r-1)F$。计数不含主元搜索、除法、内存、稀疏填充或设备效应，不能替代基准；`automatic_action` 为 `none`。

## 正确性与工程边界

初等消元矩阵的逆相乘形成 $L$，故重排后有 $PA=LU$；前代、回代合并即解原系统。部分选主元通常抑制小主元误差，但不修复病态；稀疏矩阵还须控制填充。

## 常见误区

- 有换行时必须验证 $PA=LU$，不是 $A=LU$。
- LU 保存消元，不自动改善病态或只解一次右端。

## 练习

1. **基础**：验证上例 $LU=A$，再对另一组 $b$ 做前代与回代。
2. **推导**：说明第 $k$ 次消元的乘子为何进入 $L$ 的第 $k$ 列。
3. **编码**：实现带部分选主元的 LU，并测试必须首行交换的矩阵。
4. **开放**：比较 LU、QR、SVD 在方阵、最小二乘、秩亏和病态问题上的取舍。

## 练习答案提示

1. 有换行时验证 $PA=LU$，再复用同一分解。
2. 第 $k$ 列下方存放该列消元乘子。
3. 换主元时同步交换已填的 $L$；奇异矩阵必须拒绝。
4. 多右端方阵用 LU，最小二乘用 QR，秩亏用 SVD；病态另行诊断。

## 延伸与下一步

LU 用于多右端方阵；[QR](/linear-algebra/orthogonal-projection-qr)处理稳定最小二乘，SVD 处理秩亏。
