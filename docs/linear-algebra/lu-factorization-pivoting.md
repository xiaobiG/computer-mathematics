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

同一个系数矩阵 $A$ 可能需要解很多次：物理仿真每帧只改变外力 $b$，回归要比较多个目标列。每次都重新消元浪费了什么？LU 分解将一次昂贵的消元结果保存下来。

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
def forward_substitute(lower, right_side):
    result = []
    for row, target in enumerate(right_side):
        known = sum(lower[row][col] * result[col] for col in range(row))
        result.append((target - known) / lower[row][row])
    return result


assert forward_substitute([[1, 0], [2, 1]], [5, 11]) == [5.0, 1.0]
```

对 $n\times n$ 密集矩阵，分解耗时 $O(n^3)$、存储 $O(n^2)$；每个新右侧向量的前代和回代合计 $O(n^2)$。实际实现通常将 $L,U$ 覆盖存于同一数组并记录置换向量。

## 正确性与工程边界

每一步消元左乘一个初等下三角矩阵，其逆的乘积形成 $L$；因此重排后必有 $PA=LU$。前代、回代分别满足两个等价三角系统，合并即解原系统。部分选主元选择当前列绝对值最大的行，通常抑制除以小数的误差放大；但条件数极大时，任何直接法的解都可能对输入敏感。稀疏矩阵还需控制填充（fill-in），不能直接套密集 LU。

## 常见误区

- $PA=LU$ 中的 $P$ 不能省略：有主元交换时 $A\ne LU$。
- LU 不比消元“更准确”，它是将同一过程保存并复用。
- 多个右侧向量才显著体现分解复用的收益。

## 练习

1. **基础**：验证上例 $LU=A$，再对另一组 $b$ 做前代与回代。
2. **推导**：说明第 $k$ 次消元的乘子为何进入 $L$ 的第 $k$ 列。
3. **编码**：实现带部分选主元的 LU，并测试必须首行交换的矩阵。
4. **开放**：比较 LU、QR、SVD 在方阵、最小二乘、秩亏和病态问题上的取舍。

## 延伸与下一步

LU 擅长反复求解方阵系统；[正交投影与 QR](/linear-algebra/orthogonal-projection-qr)更适合稳定最小二乘，SVD 则处理秩亏和低秩近似。
