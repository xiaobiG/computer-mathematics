---
courseLevel: "2–3（推导与工程）"
prerequisites: "内积、投影与最小二乘"
estimatedMinutes: 60
experiment: "比较 Gram–Schmidt 与正规方程"
title: 正交投影、Gram–Schmidt 与 QR 分解：稳定地求最近解
description: 从投影推导 Gram–Schmidt 正交化和 QR 分解，理解它为何优于正规方程。
---

# 正交投影、Gram–Schmidt 与 QR 分解：稳定地求最近解

## 文章元信息

- **建议阅读层级**：2–3 · 推导、算法与数值稳定性
- **前置知识**：[向量与点积](/linear-algebra/vectors-dot-product)、[四个基本子空间](/linear-algebra/four-fundamental-subspaces)、[最小二乘](/linear-algebra/least-squares)
- **预计学习时间**：60 分钟
- **配套实验**：[线性代数实验室](/projects/linear-algebra-lab)

## 学习目标

- 从正交条件推导向量投影与最小二乘解；
- 用 Gram–Schmidt 构造正交基并写出 $A=QR$；
- 解释 QR 为什么通常比正规方程更稳定。

## 从一个计算问题开始

当 $b$ 不在矩阵 $A$ 的列空间中，最小二乘需要找到最近的 $A\hat x$。直接解 $A^TA\hat x=A^Tb$ 看似方便，但接近相关的列会使条件数近似平方。怎样既保留列空间，又避免这一放大？

## 直觉与定义

若 $q$ 是单位向量，$v$ 在 $q$ 方向的投影是

$$\mathrm{proj}_q(v)=(q^Tv)q.$$

投影后残差 $v-\mathrm{proj}_q(v)$ 与 $q$ 正交。对一组正交单位列组成的 $Q$，投影到其列空间可写成 $QQ^Tb$；因为 $Q^TQ=I$，坐标就是 $Q^Tb$。

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

## 同一 QR 重构，为什么正交性仍会失效

经典 Gram–Schmidt（CGS）与改进 Gram–Schmidt（MGS）的代数公式等价，但浮点计算的投影顺序不同。CGS 用原列 $a_j$ 一次算出所有 $q_i^Ta_j$，再一起相减；MGS 每减去一个投影，就用更新后的残差计算下一个系数。当列几乎共线时，这个顺序决定被消去的低位是否还能参与下一次投影。

取三列

$$
a_1=(1,1,1)^T,\quad a_2=(1,1+10^{-8},1)^T,\quad a_3=(1,1,1+10^{-8})^T.
$$

它们仍线性无关，却会放大舍入影响。以下报告用同一输入分别运行两种算法，独立记录 QR 重构误差与最大非对角内积

$$
\max_{i<j}|q_i^Tq_j|.
$$

```python
from projects.linear_algebra_lab.main import (
    gram_schmidt_stability_certificate,
    gram_schmidt_stability_report,
)

delta = 1e-8
columns = [[1.0, 1.0, 1.0], [1.0, 1.0 + delta, 1.0], [1.0, 1.0, 1.0 + delta]]
report = gram_schmidt_stability_report(columns)

assert report["classical"]["qr_reconstruction_error"] < 1e-12
assert report["modified"]["qr_reconstruction_error"] < 1e-12
assert report["classical"]["orthogonality_defect"] > 0.9
assert report["modified"]["orthogonality_defect"] < 1e-5
assert gram_schmidt_stability_certificate(columns, report)
```

这个输入上 CGS 的正交缺陷约为 $0.998$，MGS 约为 $1.1\times10^{-7}$；两种 `QR` 重构误差却都接近零。故“$A\approx QR$”不足以证实 $Q^TQ\approx I$，而后者正是用 $Q^Tb$ 当投影坐标的前提。该对照不宣称 MGS 对任意病态矩阵足够稳定，也不替代 Householder QR、列主元或 SVD；它只提供一个可复现的理由，说明相同的代数恒等式在不同浮点路径上可有不同质量。

## 常见误区

- 正交不必单位长；正交归一才使 $Q^TQ=I$。
- $QQ^T$ 是投影矩阵，$Q^TQ$ 在列正交时是单位矩阵，二者维度与意义不同。
- QR 不“消除”病态性，它避免正规方程额外平方条件数。

## 练习

1. **基础**：计算 $(3,4)$ 在单位方向 $(1,0)$ 上的投影与残差。
2. **推导**：证明投影残差与每个 $q_i$ 正交。
3. **编码**：运行 `gram_schmidt_stability_report`，分别检查 CGS/MGS 的重构误差和正交缺陷；再改变扰动大小，观察何时两者都开始失效。
4. **开放**：比较正规方程、改进 Gram–Schmidt、Householder QR 在病态数据上的残差、前向误差和 $Q^TQ-I$ 缺陷。

## 练习答案提示

1. 投影为 $((3,4)\cdot(1,0))(1,0)=(3,0)$，残差是 $(0,4)$；先确认方向已单位化。
2. 写 $r=v-\sum_i(q_i^Tv)q_i$，分别与任意 $q_j$ 点积；正交归一使除交叉项外只留下 $q_j^Tv-q_j^Tv$。
3. 重构小不等于基仍正交：报告需同时看 $QR-A$ 与最大 $|q_i^Tq_j|$。改变扰动时还要记录何时算法按容差拒绝，而不是把数值噪声叫作新方向。
4. 固定同一病态矩阵，分开测后向残差、相对解误差和 $Q^TQ-I$；正规方程会放大条件数，Householder 通常是更稳的数值基线。

## 延伸与下一步

QR 为最小二乘提供稳定路径；[SVD](/linear-algebra/svd)进一步处理秩亏与最佳低秩近似，并连接 PCA 与压缩。
