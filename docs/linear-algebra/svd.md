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

## 定义与推导：三个彼此正交的步骤

任意 $A\in\mathbb R^{m\times n}$ 可写为

$$A=U\Sigma V^T,$$

其中 $U,V$ 的列正交，$\Sigma$ 的对角元 $\sigma_1\ge\sigma_2\ge\cdots\ge0$ 是奇异值。它表示：先用 $V^T$ 把输入改写到一组正交坐标；再沿每一坐标轴按 $\sigma_i$ 拉伸或压缩；最后用 $U$ 旋转到输出空间。因此 SVD 不要求 $A$ 为方阵，也不要求可逆。

将乘积按列展开，得到 $A=\sum_i\sigma_i u_i v_i^T$。每项都是秩一外积；保留前 $k$ 项得到 $A_k=U_k\Sigma_kV_k^T$。由于这些项在 Frobenius 内积下彼此正交，丢弃的项不会相互抵消。Eckart–Young–Mirsky 定理进一步说明：$A_k$ 在所有秩至多 $k$ 矩阵中最接近 $A$，且

$$\lVert A-A_k\rVert_F^2=\sum_{i>k}\sigma_i^2.$$

## 谱证书与数值秩：非零不等于应保留

对精确谱 $[5,2,1]$ 保留一个模式时，误差是

$$\|A-A_1\|_F=\sqrt{2^2+1^2}=\sqrt5.$$

精确截断报告会重放能量分解、平方误差和参数量，避免把“保留能量多”误写成“文件一定更小”。但**精确秩不自动给出数值有效秩**：谱 $[1,10^{-8},10^{-12}]$ 的精确秩为 3。绝对、相对阈值同为 $10^{-9}$ 时，两者都保留前两个值；把矩阵缩放为 $10^{-6}A$ 后，几何方向和相对谱间隙不变，绝对阈值却只保留一个值，相对阈值仍保留两个。单位、噪声和允许误差未声明时，“数值秩是多少”没有唯一答案。

```python
from projects.linear_algebra_lab.main import (
    numerical_rank_scale_comparison,
    numerical_rank_scale_comparison_certificate,
    truncated_svd_report,
    truncated_svd_report_certificate,
)

report = numerical_rank_scale_comparison([1.0, 1e-8, 1e-12], 1e-6, 1e-9, 1e-9)
assert report["original"]["exact_rank"] == 3
assert report["scaled"]["absolute_numerical_rank"] == 1
assert report["relative_rank_is_scale_invariant"]
assert numerical_rank_scale_comparison_certificate([1.0, 1e-8, 1e-12], 1e-6, 1e-9, 1e-9, report)

exact = truncated_svd_report([5.0, 2.0, 1.0], rank=1, rows=8, columns=8)
assert truncated_svd_report_certificate([5.0, 2.0, 1.0], 1, 8, 8, exact)["valid"]
```

秩 $k$ 因子约用 $k(m+n+1)$ 个数，少于 $mn$ 才有参数节省；量化、编码和元数据仍是另一问题。相对阈值的缩放不变性也不证明它正确：阈值应来自噪声、后向误差或下游允许损失，而不是从一次 SVD 输出反推。

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

低秩近似只保证平方误差最优，不保证语义、安全或公平性保持。奇异值很接近时，对应方向会对噪声敏感；零奇异值表示确切冗余。非零但很小的值是否计入数值秩，必须报告绝对/相对阈值及其噪声或误差模型。大规模稀疏矩阵应使用迭代或随机 SVD，不要先转为密集矩阵。

## 常见误区

- SVD 不要求方阵，也不要求可逆。
- 截断不是“随意删列”，而是保留最大奇异值对应模式。
- PCA 需要中心化；直接对原始矩阵做 SVD 不总是 PCA。
- 幂迭代的教学近似不是精确截断 SVD；不要把一次运行的误差当作 Eckart–Young 证书。
- “三个奇异值非零，所以有效秩必为三。”错误：数值秩需要声明阈值、单位和可接受误差。

## 练习

1. 对奇异值 $5,2,1$ 计算保留一个模式的平方重构误差与 Frobenius 误差。
2. 解释秩一外积为何只有一个独立方向。
3. 对谱 $[1,10^{-8},10^{-12}]$ 运行缩放对照；解释固定绝对阈值为何改变秩标签、相对阈值为何仍不能免除误差模型。
4. 用数值库对小灰度矩阵比较不同 $k$ 的重构误差与谱尾平方和；再说明参数节省为何不足以证明实际文件更小。

## 练习答案提示

1. 舍弃奇异值 $2,1$ 的平方和为 $5$，Frobenius 误差为 $\sqrt5$；区分“平方误差”和“误差范数”。
2. 外积 $uv^T$ 的任一列都是同一 $u$ 的标量倍，因此列空间至多一维；非零时秩恰为一。
3. 缩放不改变零/非零的精确秩，却改变绝对数值大小；相对阈值保留比例，仍需由噪声、后向误差或下游预算说明其合理性。
4. 对每个 $k$ 比较实际平方误差与 $\sum_{i>k}\sigma_i^2$，并检查能量分解；文件大小还取决于量化、编码、元数据和数据可压缩性。

## 下一步

至此完成“向量—变换—求解—投影—降维”主线；用[线性代数实验室](/projects/linear-algebra-lab)复现关键计算，并继续阅读[低秩图像压缩](/linear-algebra/low-rank-image-compression)把谱证书与实际近似误差放在同一份实验报告中。
