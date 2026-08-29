---
title: 随机范围发现：大矩阵如何近似低秩结构
description: 从随机测试矩阵推导 QQ^T A 近似，记录种子与正交基，并用可重放实验观察谱间隙、幂迭代和误差边界。
courseLevel: "3（随机化线性代数、性能权衡与可复现实验）"
prerequisites: "矩阵乘法、正交投影、QR、SVD 与随机数种子"
estimatedMinutes: 70
experiment: "固定随机种子运行范围发现，重放 QQ^T A 报告并比较幂迭代前后的实际残差"
---

# 随机范围发现：大矩阵如何近似低秩结构

## 学习目标

读完后，你能解释随机范围发现为何只需访问矩阵少数次；从随机草图推导 $QQ^TA$；实现并重放带种子的随机实验；理解过采样和幂迭代的作用；并区分范围发现的实际残差、精确截断 SVD 的最优误差和生产级随机 SVD。

## 从一个计算问题开始

若图像或特征矩阵 $A\in\mathbb R^{m\times n}$ 很大，先求完整 SVD 往往不划算：完整分解会处理所有方向，即使应用只需要前几十个。但直接随机抽几列也可能错过重要模式。问题变成：怎样以少量随机探测，尽量找到 $A$ 的主列空间，再把原矩阵投影到这个小空间？

## 直觉与严格定义

取目标秩 $k$、过采样 $p$，令 $ell=k+p$。生成固定种子下的随机测试矩阵

$$\Omega\in\mathbb R^{n\times\ell},\qquad Y=A\Omega.$$

每列 $A\omega_j$ 是 $A$ 的列空间中的随机混合。对 $Y$ 做 QR（本课用改进 Gram–Schmidt 的教学版本），得到列正交矩阵 $Q$，再以

$$\hat A=QQ^TA$$

近似原矩阵。这里 $Q$ 的列数至多 $ell$，故 $\hat A$ 的秩至多 $ell$。范围发现本身并不产出奇异向量；后续若要随机 SVD，应再对小矩阵 $B=Q^TA$ 做分解。

## 分步推导：为何 $QQ^TA$ 是正确的投影形式

若 $Q^TQ=I$，则 $P=QQ^T$ 满足

$$P^T=P,\qquad P^2=QQ^TQQ^T=QQ^T=P.$$

因此 $P$ 是到 $\operatorname{col}(Q)$ 的正交投影。对每一列 $a_j$，$QQ^Ta_j$ 都是该子空间中距 $a_j$ 最近的向量；把所有列拼起来就是 $QQ^TA$。随机性的职责不是改变投影定理，而是希望草图 $Y=A\Omega$ 的列空间足够接近 $A$ 的主方向。

当奇异值衰减慢时，标准草图可能混入较弱方向。可做 $q$ 次幂迭代：

$$Y=(AA^T)^qA\Omega.$$

在奇异向量基中，第 $i$ 个方向被放大为 $sigma_i^{2q+1}$，主方向相对更显著；代价是每次多读矩阵两遍，也可能放大浮点尺度差异。

## 算法实现：固定种子，重放同一份草图

```python
from projects.linear_algebra_lab.randomized_range import (
    randomized_range_certificate,
    randomized_range_report,
)

matrix = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]]
report = randomized_range_report(matrix, rank=1, oversampling=1, seed=17)

assert report.basis_columns == 1
assert report.frobenius_error < 1e-10
assert randomized_range_certificate(matrix, report, oversampling=1)
```

运行 `python -m unittest projects.linear_algebra_lab.test_randomized_range`。实现用局部 `Random(seed)` 产生测试矩阵，保存种子、请求秩、实际正交基列数、幂迭代次数、基、近似与 Frobenius 残差。证书从同一输入和种子重建草图，拒绝任何被改过的基、近似或误差字段；它验证可复现的实现轨迹，不会把一次随机样本当作普适的质量证明。

若 $\ell=k+p$，每次矩阵乘法约为 $O(mn\ell)$；做 $q$ 次幂迭代后约为 $O((2q+1)mn\ell)$，正交化约为 $O(m\ell^2)$。真正适合大规模和稀疏矩阵的实现应使用块乘法、稳定 QR、流式输入和成熟库，而不是本课的密集 Python 列表。

## 正确性与复杂度

上述投影恒等式证明输出位于 $\operatorname{col}(Q)$，并且对**这个已采样的子空间**是最小二乘最优。秩上界来自 $QQ^TA$ 经过至多 $ell$ 个正交方向。测试用秩一矩阵验证其随机草图仍落在同一列空间，重构误差接近零；同时用固定种子比较幂迭代前后实测残差，检查并非只宣称“随机通常有效”。

它不证明在任意矩阵、任意种子下误差接近最佳秩 $k$ 误差。高概率理论还依赖随机分布、过采样、谱性质和精确/稳定正交化等前提；完整结论应带概率界，而不是省略成确定性保证。

## 失败案例与工程边界

- **零矩阵与退化草图**：没有非零采样范围时，教学实现显式拒绝；生产代码要有零秩分支和容差策略。
- **随机种子不是质量证书**：固定种子让失败复现，不会让该种子天然代表所有数据或随机草图。
- **慢衰减谱**：奇异值接近时，小 $\ell$ 容易漏掉方向；可增大过采样、使用幂迭代并报告实际残差。
- **数值正交性**：改进 Gram–Schmidt 在高度近相关列上仍会损失正交性；生产实现应使用 Householder QR 或 TSQR。
- **不是完整随机 SVD**：$QQ^TA$ 是投影近似，尚未对 $B=Q^TA$ 求小型 SVD；也不自动提供严格的前 $k$ 奇异值。

## 常见误区

1. “随机算法不需要验证。”错误：至少要固定种子、记录参数并测量实际残差。
2. “$QQ^TA$ 必然是最佳秩 $k$ 近似。”错误：它只对采样得到的子空间最优，且秩上界是 $k+p$。
3. “幂迭代越多越好。”错误：矩阵遍历、运行时间与舍入敏感性都增加。
4. “随机范围发现就是完整 SVD。”错误：它通常只是构建一个小的近似子空间，SVD 是后续可选步骤。

## 练习

1. **基础题**：验证 $P=QQ^T$ 的对称性和幂等性，并说明其像空间是什么。
2. **推导题**：在 $A=U\Sigma V^T$ 中展开 $(AA^T)^qA\Omega$，推导 $sigma_i^{2q+1}$ 的来源。
3. **编码题**：比较同一矩阵在多个 seed、不同 oversampling 下的实际残差；保存最差种子为回归测试。
4. **开放题**：为稀疏推荐矩阵设计一份随机 SVD 实验报告，包含数据切分、随机分布、种子、矩阵遍历数、误差、内存和与精确/迭代基线的比较。

## 延伸

[SVD](/linear-algebra/svd)给出精确低秩最优性的参照；[低秩图像压缩](/linear-algebra/low-rank-image-compression)把投影连接到重构；[随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)解释为何种子和重复报告不可省略。继续学习可检索 randomized SVD、Halko–Martinsson–Tropp、subspace iteration、TSQR 与 streaming PCA。
