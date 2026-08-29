---
title: 正交投影、Gram–Schmidt 与 QR 分解：稳定地求最近解
description: 从投影推导 Gram–Schmidt 正交化和 QR 分解，理解它为何优于正规方程。
---

# 正交投影、Gram–Schmidt 与 QR 分解：稳定地求最近解

## 文章元信息

- **建议阅读层级**：2–3 · 推导、算法与数值稳定性
- **前置知识**：[向量与点积](/linear-algebra/vectors-dot-product)、[四个基本子空间](/linear-algebra/four-fundamental-subspaces)、[最小二乘](/linear-algebra/least-squares)
- **预计学习时间**：70 分钟
- **配套实验**：[线性代数实验室](/projects/linear-algebra-lab)

## 学习目标

- 从正交条件推导向量投影与最小二乘解；
- 用 Gram–Schmidt 构造正交基并写出 $A=QR$；
- 解释 QR 为什么通常比正规方程更稳定。

## 从一个计算问题开始

当 $b$ 不在矩阵 $A$ 的列空间中，最小二乘需要找到最近的 $A\hat x$。直接解 $A^TA\hat x=A^Tb$ 看似方便，但接近相关的列会使条件数近似平方。怎样既保留列空间，又避免这一放大？

## 直觉与定义

若 $q$ 是单位向量，$v$ 在 $q$ 方向的投影是

$$\operatorname{proj}_q(v)=(q^Tv)q.$$

投影后残差 $v-\operatorname{proj}_q(v)$ 与 $q$ 正交。对一组正交单位列组成的 $Q$，投影到其列空间可写成 $QQ^Tb$；因为 $Q^TQ=I$，坐标就是 $Q^Tb$。

## 分步推导：Gram–Schmidt 与 QR

对线性无关列 $a_1,\ldots,a_n$，依次去除前面方向：

$$u_j=a_j-\sum_{i<j}(q_i^Ta_j)q_i,\qquad q_j=\frac{u_j}{\lVert u_j\rVert}.$$

令 $r_{ij}=q_i^Ta_j$（$i\le j$），可将每列重写为 $a_j=\sum_{i\le j}q_ir_{ij}$，合并得到

$$A=QR,$$

其中 $Q$ 的列正交、$R$ 为上三角。最小二乘 $\min_x\lVert Ax-b\rVert$ 变为 $\min_x\lVert Rx-Q^Tb\rVert$；对满列秩 $A$，只需回代 $R\hat x=Q^Tb$。

## 算法实现与复杂度

```python
from math import sqrt


def modified_gram_schmidt(columns):
    orthonormal, upper = [], [[0.0] * len(columns) for _ in columns]
    for j, column in enumerate(columns):
        work = list(map(float, column))
        for i, basis in enumerate(orthonormal):
            upper[i][j] = sum(a * b for a, b in zip(basis, work))
            work = [value - upper[i][j] * basis[k] for k, value in enumerate(work)]
        upper[j][j] = sqrt(sum(value * value for value in work))
        if upper[j][j] <= 1e-12:
            raise ValueError("columns are linearly dependent at this tolerance")
        orthonormal.append([value / upper[j][j] for value in work])
    return orthonormal, upper


q, r = modified_gram_schmidt([[1, 0], [1, 1]])
assert abs(sum(a * b for a, b in zip(q[0], q[1]))) < 1e-12
```

对 $m\times n$ 密集矩阵，改进 Gram–Schmidt 为 $O(mn^2)$，存储 $O(mn+n^2)$。工业库多使用 Householder QR，稳定性和缓存行为通常更好。

## 正确性与工程边界

每次减去所有已有基上的投影，因此新残差与所有旧 $q_i$ 正交；归一化后得到正交单位列。展开投影系数即得到 $A=QR$。经典 Gram–Schmidt 在近线性相关列上会丢失正交性，改进版本较好但仍不如 Householder 反射；秩亏问题应使用列主元 QR 或 SVD，而不是将极小范数任意除掉。

## 常见误区

- 正交不必单位长；正交归一才使 $Q^TQ=I$。
- $QQ^T$ 是投影矩阵，$Q^TQ$ 在列正交时是单位矩阵，二者维度与意义不同。
- QR 不“消除”病态性，它避免正规方程额外平方条件数。

## 练习

1. **基础**：计算 $(3,4)$ 在单位方向 $(1,0)$ 上的投影与残差。
2. **推导**：证明投影残差与每个 $q_i$ 正交。
3. **编码**：为 `modified_gram_schmidt` 添加重复列、近相关列和三列输入测试。
4. **开放**：比较正规方程、改进 Gram–Schmidt、Householder QR 在病态数据上的残差与前向误差。

## 延伸与下一步

QR 为最小二乘提供稳定路径；[SVD](/linear-algebra/svd)进一步处理秩亏与最佳低秩近似，并连接 PCA 与压缩。
