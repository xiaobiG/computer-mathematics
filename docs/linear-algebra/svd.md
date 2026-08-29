---
courseLevel: "2–3（推导与应用）"
prerequisites: "特征值、正交矩阵与范数"
estimatedMinutes: 65
experiment: "用截断 SVD 做低秩压缩"
title: SVD：矩阵的通用分解
description: 用奇异值分解理解坐标旋转、低秩近似、压缩与 PCA。
---

# SVD：矩阵的通用分解

## 学习目标

- 解释 $A=U\Sigma V^T$ 的三个几何步骤；
- 用截断奇异值构造低秩近似；
- 根据奇异值谱计算精确截断误差和参数量；
- 将 SVD 与 PCA、压缩和数值稳定性联系起来。

## 从一个计算问题开始

图像矩阵或用户—物品矩阵很大，却常可由少数模式近似。怎样有原则地丢弃信息，并知道丢弃了多少误差？

## 定义：三个彼此正交的步骤

任意 $A\in\mathbb R^{m\times n}$ 可写为

$$A=U\Sigma V^T,$$

其中 $U,V$ 的列正交，$\Sigma$ 的对角元 $\sigma_1\ge\sigma_2\ge\cdots\ge0$ 是奇异值。它表示：先用 $V^T$ 把输入改写到一组正交坐标；再沿每一坐标轴按 $\sigma_i$ 拉伸或压缩；最后用 $U$ 旋转到输出空间。因此 SVD 不要求 $A$ 为方阵，也不要求可逆。

将乘积按列展开，得到 $A=\sum_i\sigma_i u_i v_i^T$。每项都是秩一外积；保留前 $k$ 项得到 $A_k=U_k\Sigma_kV_k^T$。由于这些项在 Frobenius 内积下彼此正交，丢弃的项不会相互抵消。Eckart–Young–Mirsky 定理进一步说明：$A_k$ 在所有秩至多 $k$ 矩阵中最接近 $A$，且

$$\lVert A-A_k\rVert_F^2=\sum_{i>k}\sigma_i^2.$$

## 可验证的谱证书

对谱 $[5,2,1]$ 保留一个模式时，误差不是“看起来少了两个方向”，而是

$$\|A-A_1\|_F=\sqrt{2^2+1^2}=\sqrt5.$$

教学实验室把这个**精确截断 SVD 的理论量**写成独立函数：输入必须是降序、非负且有限的奇异值；这防止无序特征值、`NaN` 或越界的秩悄悄产生一个貌似合理的答案。

```python
from projects.linear_algebra_lab.main import (
    low_rank_parameter_report,
    truncated_svd_frobenius_error,
)

assert truncated_svd_frobenius_error([5.0, 2.0, 1.0], rank=1) == 5 ** 0.5
assert low_rank_parameter_report(8, 8, rank=2)["saved_parameters"] == 30
```

对 $m\times n$ 矩阵，原始密集表示要 $mn$ 个数；$k$ 个奇异三元组约要 $k(m+n+1)$ 个数。后者更少才表示参数层面有节省；它仍未包含量化、编码和元数据。

## 手算解释与实现边界

若只有一个非零奇异值，矩阵可写成 $\sigma uv^T$，所有行列都由一个模式决定，秩为一。对中心化数据 $X$ 做 SVD，$V$ 的列是 PCA 主方向，奇异值平方与解释方差成比例。

```python
from projects.linear_algebra_lab.main import compress_grayscale

pixels = [[8.0, 0.0], [0.0, 3.0]]
components, approximation, measured_error = compress_grayscale(pixels, rank=1, iterations=120)
print(len(components), measured_error)
```

这里的 `compress_grayscale` 用 $A^TA$ 幂迭代和残差消去提取分量；`measured_error` 是这次有限迭代的实际误差，而不是自动取得定理中的最优值。对精确 SVD，才可将误差与 `truncated_svd_frobenius_error` 的谱尾公式直接相等比较。完整密集 SVD 成本较高；实际压缩通常计算截断 SVD，并保存 $U_k,\Sigma_k,V_k$ 而非完整矩阵。可运行的压缩实验见[低秩图像压缩](/linear-algebra/low-rank-image-compression)。

## 失败案例与工程边界

低秩近似只保证平方误差最优，不保证语义、安全或公平性保持。奇异值很接近时，对应方向会对噪声敏感；零奇异值表示确切冗余。大规模稀疏矩阵应使用迭代或随机 SVD，不要先转为密集矩阵。

## 常见误区

- SVD 不要求方阵，也不要求可逆。
- 截断不是“随意删列”，而是保留最大奇异值对应模式。
- PCA 需要中心化；直接对原始矩阵做 SVD 不总是 PCA。
- 幂迭代的教学近似不是精确截断 SVD；不要把一次运行的误差当作 Eckart–Young 证书。

## 练习

1. 对奇异值 $5,2,1$ 计算保留一个模式的平方重构误差与 Frobenius 误差。
2. 解释秩一外积为何只有一个独立方向。
3. 用数值库对小灰度矩阵比较不同 $k$ 的重构误差，并与谱尾平方和核对。
4. **开放**：为一个 $1000\times800$ 矩阵选择参数量确有节省的 $k$，再说明为什么这仍不足以证明实际文件更小。

## 下一步

至此完成“向量—变换—求解—投影—降维”主线；用[线性代数实验室](/projects/linear-algebra-lab)复现关键计算，并继续阅读[低秩图像压缩](/linear-algebra/low-rank-image-compression)把谱证书与实际近似误差放在同一份实验报告中。
