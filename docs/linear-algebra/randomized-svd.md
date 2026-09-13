---
title: 随机 SVD：从随机子空间到低秩分解
description: 在随机范围发现后分解小矩阵 B=Q^TA，分解草图误差与子空间内截断误差，并用固定种子与误差证书审计结果。
courseLevel: "3（随机化线性代数与可复现实验）"
prerequisites: "SVD、QR、随机范围发现、Frobenius 范数"
estimatedMinutes: 70
experiment: "消费已验证的随机范围报告，分解同一小矩阵并重放两类截断重构误差"
---

# 随机 SVD：从随机子空间到低秩分解

## 学习目标

读完后，你能从随机范围发现的正交基 $Q$ 推导小矩阵 SVD；解释为何 $B=Q^TA$ 的分解可返回原空间；用 Frobenius 范数勾股分解区分草图误差与子空间内截断误差；并用固定种子重放报告。

## 从一个计算问题开始

完整 SVD 会直接处理整张大矩阵；随机范围发现已经把主要列空间压缩为少量正交方向。现在的问题是：**怎样把这个子空间转成可用于压缩的奇异值和左右方向，同时不把一次随机实验误写成最佳近似证明？**

## 直觉与定义：从投影到小矩阵分解

范围发现给出 $Q\in\mathbb R^{m\times\ell}$。令

$$B=Q^TA,$$

并分解 $B=\widetilde U\Sigma V^T$。由于 $Q^TQ=I$，令 $U=Q\widetilde U$，便有

$$A\approx QQ^TA=Q\widetilde U\Sigma V^T=U\Sigma V^T.$$

最终只保留前 $k$ 项。这里的误差包含“随机子空间未捕获的方向”与“在该子空间中截断”的共同影响，因此不能直接冒充精确 Eckart--Young 最优误差。

## 两种误差的正交分解

设 $P=QQ^T$，而 $B_k$ 是 $B$ 的秩 $k$ 截断，随机 SVD 的重构为 $\widehat A_k=QB_k$。把总残差拆开：

$$A-\widehat A_k=(I-P)A+Q(B-B_k).$$

第一项是范围发现遗漏的方向，第二项是在已经捕获的子空间内仍被秩 $k$ 截断丢掉的方向。它们在 Frobenius 内积下正交，因为

$$Q^T(I-P)=Q^T-Q^TQQ^T=0.$$

因此不是模糊地说“误差来自随机性”，而是有可审计恒等式：

$$\lVert A-\widehat A_k\rVert_F^2=\lVert(I-P)A\rVert_F^2+\lVert B-B_k\rVert_F^2.$$

这也解释了两个不同的改进手段：增加过采样或幂迭代主要试图降低第一项；提高保留秩 $k$ 主要降低第二项。两者都不自动保证相对精确 SVD 的最优误差更小，必须查看报告的实际数值。

## 算法与证据边界

1. 用固定种子生成随机草图并正交化为 $Q$；
2. 计算小矩阵 $B=Q^TA$；
3. 只对 $B$ 做 SVD，映射左奇异向量回 $U=Q\widetilde U$；
4. 截断到 $k$，报告 $\lVert A-U_k\Sigma_kV_k^T\rVert_F$；
5. 重放种子、过采样、幂迭代、截断参数和完整重构矩阵形状，拒绝被改写的误差或被截断的行列。

## 可运行实验

```python
from projects.linear_algebra_lab.randomized_range import randomized_range_report
from projects.linear_algebra_lab.randomized_svd import (
    randomized_svd_certificate,
    randomized_svd_from_range_report,
)

matrix = [[5.0, 0.0], [0.0, 1.0]]
range_report = randomized_range_report(matrix, rank=1, oversampling=1, seed=3)
report = randomized_svd_from_range_report(matrix, range_report, rank=1)
print(report.singular_values, report.frobenius_error)
assert report.source_range_report == range_report
assert report.range_projection_error >= 0
assert report.in_range_truncation_error >= 0
assert report.pythagorean_residual < 1e-10
assert randomized_svd_certificate(matrix, report)
```

运行：

```bash
python -m unittest \
  projects.linear_algebra_lab.test_randomized_svd
```

## 跨课使用：把实际重构交给图像误差评审

随机 SVD 的 `approximation` 不应脱离来源后作为一张匿名矩阵传递。把完整 `report` 交给[图像误差指标](/linear-algebra/image-error-metrics)的评审函数时，下游会先重放随机范围与小矩阵分解，再计算 MSE、RMSE、PSNR 和最大误差：

```python
from projects.linear_algebra_lab.image_metrics import randomized_svd_image_quality_review

quality_review = randomized_svd_image_quality_review(matrix, report, mse_budget=0.3, peak=5.0)
assert quality_review.source_rank == 1
assert quality_review.mse_budget_status == "within_mse_budget"
```

改变上游矩阵、seed、过采样、幂迭代、来源范围或截断重构会使评审拒绝；改变下游的 MSE 预算会改变“预算内/超出”的数值结论。两种结果都固定 `automatic_action="none"`：像素误差预算不能替代感知实验、文件编码评估或业务风险判断。

## 正确性与反例

秩一矩阵在草图捕获其列空间时可近似精确重构；测试验证这一点。对对角矩阵 $\mathrm{diag}(5,1)$ 使用两个草图方向而只保留一项时，范围误差约为零、子空间内截断误差为 1、总误差也为 1。这把“误差为正”进一步定位为截断而非草图失败。

固定种子只能让同一草图可重放。报告证书不仅重算总误差、两项分量和勾股残差，也验证 `source_range_report` 的矩阵、seed、过采样、幂迭代和正交基，再检查完整近似矩阵的行列数；否则只用 `zip` 逐行比较会让少一行或少一列的前缀静默通过。不同种子、谱间隙、过采样和浮点正交化都会影响第一项；高概率界需要额外分布与谱假设，本课不把它写成确定性承诺。

## 失败案例与工程边界

若谱没有明显间隙、过采样不足或随机草图恰好弱覆盖主方向，随机近似可能远差于精确截断 SVD；此时应报告种子、实际误差与资源预算，而不是只保留一个好看的运行。该实现还只对小型 $B$ 使用密集 SVD，不能替代稀疏、分布式或流式系统中的成熟数值库。

## 常见误区

- **“随机 SVD 就是不做 SVD。”** 错；它把大矩阵的分解缩到小矩阵 $B$。
- **“种子固定就说明质量可靠。”** 错；种子只使失败也能复现。
- **“报告误差等于最佳秩 $k$ 误差。”** 不一定；随机子空间可能遗漏方向。
- **“该实现可替代大规模生产库。”** 不可以；它仅用于小型、可检查教学实验。

## 练习

1. 推导 $U=Q\widetilde U$ 的列正交性。
2. 比较不同种子下同一矩阵的两项误差，并判断变化发生在草图还是截断。
3. 解释过采样与提高保留秩分别主要影响勾股分解中的哪一项。
4. 写出报告必须保存的四个随机化参数。

## 练习答案提示

1. 用 $Q^TQ=I$ 与 $\widetilde U^T\widetilde U=I$ 相乘。
2. 固定其余参数，多次运行并同时报告种子、范围误差、子空间内截断误差和总误差；不要只比较一个总数。
3. 更多随机方向可能覆盖主子空间，主要改变第一项；提高 $k$ 改变第二项。两者仍受抽样和数值条件影响。
4. 至少包括种子、目标秩、过采样量和幂迭代次数。

## 延伸

[随机范围发现](/linear-algebra/randomized-range-finder)解释 $Q$ 的来源；[SVD](/linear-algebra/svd)给出精确低秩最优性的参照；[低秩图像压缩](/linear-algebra/low-rank-image-compression)展示重构误差的应用。
