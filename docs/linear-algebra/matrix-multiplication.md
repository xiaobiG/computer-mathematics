---
courseLevel: "1–2（核心概念与推导）"
prerequisites: "向量与函数复合"
estimatedMinutes: 40
experiment: "实现矩阵乘法并验证维度与结合律"
title: 矩阵乘法：连续变换如何合成为一步
description: 从线性变换推导行乘列规则、维度约束与组合顺序。
---

# 矩阵乘法：连续变换如何合成为一步

## 学习目标

- 从复合变换而非死记规则理解矩阵乘法；
- 检查维度并解释输出形状；
- 验证变换顺序通常不可交换。

## 从一个计算问题开始

图形程序要先横向拉伸点，再旋转九十度。能否预先合成为一个矩阵，使 $Cx=R(Sx)$？这就是矩阵乘法的定义动机。

## 定义与推导

若 $A\in\mathbb R^{m\times n}$、$B\in\mathbb R^{n\times p}$，$AB$ 将 $p$ 维输入变为 $m$ 维输出：

$$ (AB)_{ij}=\sum_{k=1}^{n}A_{ik}B_{kj}. $$

内侧 $n$ 同时是 $B$ 的输出维度和 $A$ 的输入维度；不一致则复合无定义。结合律来自函数复合，交换律一般不成立。

## 手算一个完整例子

$$S=\begin{bmatrix}2&0\\0&1\end{bmatrix},\quad R=\begin{bmatrix}0&-1\\1&0\end{bmatrix}.$$

$$RS=\begin{bmatrix}0&-1\\2&0\end{bmatrix},\qquad SR=\begin{bmatrix}0&-2\\1&0\end{bmatrix}.$$

对 $x=(1,1)$，$RSx=(-1,2)$ 而 $SRx=(-2,1)$。矩阵从右向左作用于向量。

## 把公式实现为代码

```python
def matmul(a, b):
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("incompatible matrix shapes")
    if any(len(row) != len(a[0]) for row in a + b):
        raise ValueError("matrices must be rectangular")
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]

assert matmul([[1, 2]], [[3], [4]]) == [[11]]
```

朴素算法耗时 $O(mnp)$、输出占 $O(mp)$ 空间。大规模计算应交给 BLAS/NumPy；这里的实现用于核对公式与维度。

## 失败案例与工程边界

内层 `sum` 恰是定义中的 $\sum_k A_{ik}B_{kj}$，所以每个输出位置正确。批量数据放行还是列必须项目内统一；稀疏矩阵不应以密集列表存储大量零。

## 常见误区

- $AB$ 表示先执行 $B$，后执行 $A$。
- 逐元素乘法不是变换复合。
- 形状匹配不保证特征语义匹配。

## 练习

1. 验证 $RS$、$SR$ 对点 $(1,1)$ 的结果。
2. 为不规则行和维度不符增加测试。
3. 解释神经网络的行批量约定为何常需转置。
4. 为一个“特征变换后接分类头”的两层线性模型写出矩阵形状，比较合成矩阵与逐层计算；再说明何时不应预先合成（例如中间层需要非线性、监控或稀疏优化）。

## 下一步

[高斯消元](/linear-algebra/gaussian-elimination)将反过来求解 $Ax=b$。
