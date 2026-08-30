---
title: 随机 SVD：从随机子空间到低秩分解
description: 在随机范围发现后分解小矩阵 B=Q^TA，重构截断近似并用固定种子与误差证书审计结果。
courseLevel: "3（随机化线性代数与可复现实验）"
prerequisites: "SVD、QR、随机范围发现、Frobenius 范数"
estimatedMinutes: 60
experiment: "固定种子构造随机范围、分解小矩阵并重放截断重构误差"
---

# 随机 SVD：从随机子空间到低秩分解

## 学习目标

读完后，你能从随机范围发现的正交基 $Q$ 推导小矩阵 SVD；解释为何 $B=Q^TA$ 的分解可返回原空间；区分截断误差、一次草图误差与精确 SVD 最优误差；并用固定种子重放报告。

## 从一个计算问题开始

完整 SVD 会直接处理整张大矩阵；随机范围发现已经把主要列空间压缩为少量正交方向。现在的问题是：**怎样把这个子空间转成可用于压缩的奇异值和左右方向，同时不把一次随机实验误写成最佳近似证明？**

## 直觉与定义：从投影到小矩阵分解

范围发现给出 $Q\in\mathbb R^{m\times\ell}$。令

$$B=Q^TA,$$

并分解 $B=\widetilde U\Sigma V^T$。由于 $Q^TQ=I$，令 $U=Q\widetilde U$，便有

$$A\approx QQ^TA=Q\widetilde U\Sigma V^T=U\Sigma V^T.$$

最终只保留前 $k$ 项。这里的误差包含“随机子空间未捕获的方向”与“在该子空间中截断”的共同影响，因此不能直接冒充精确 Eckart--Young 最优误差。

## 算法与证据边界

1. 用固定种子生成随机草图并正交化为 $Q$；
2. 计算小矩阵 $B=Q^TA$；
3. 只对 $B$ 做 SVD，映射左奇异向量回 $U=Q\widetilde U$；
4. 截断到 $k$，报告 $\lVert A-U_k\Sigma_kV_k^T\rVert_F$；
5. 重放种子、过采样、幂迭代和截断参数，拒绝被改写的误差。

## 可运行实验

```python
from projects.linear_algebra_lab.randomized_svd import (
    randomized_svd_certificate,
    randomized_svd_report,
)

matrix = [[5.0, 0.0], [0.0, 1.0]]
report = randomized_svd_report(matrix, rank=1, oversampling=1, seed=3)
print(report.singular_values, report.frobenius_error)
assert randomized_svd_certificate(matrix, report)
```

运行：

```bash
python -m unittest \
  projects.linear_algebra_lab.test_randomized_svd
```

## 正确性与反例

秩一矩阵在草图捕获其列空间时可近似精确重构；测试验证这一点。对对角矩阵 $\operatorname{diag}(5,1)$ 只保留一项时，误差应为正：低秩截断不会凭随机性消灭被舍弃方向。

固定种子只能让同一草图可重放。不同种子、谱间隙、过采样和浮点正交化都会影响实际误差；高概率界需要额外分布与谱假设，本课不把它写成确定性承诺。

## 失败案例与工程边界

若谱没有明显间隙、过采样不足或随机草图恰好弱覆盖主方向，随机近似可能远差于精确截断 SVD；此时应报告种子、实际误差与资源预算，而不是只保留一个好看的运行。该实现还只对小型 $B$ 使用密集 SVD，不能替代稀疏、分布式或流式系统中的成熟数值库。

## 常见误区

- **“随机 SVD 就是不做 SVD。”** 错；它把大矩阵的分解缩到小矩阵 $B$。
- **“种子固定就说明质量可靠。”** 错；种子只使失败也能复现。
- **“报告误差等于最佳秩 $k$ 误差。”** 不一定；随机子空间可能遗漏方向。
- **“该实现可替代大规模生产库。”** 不可以；它仅用于小型、可检查教学实验。

## 练习

1. 推导 $U=Q\widetilde U$ 的列正交性。
2. 比较不同种子下同一矩阵的报告误差。
3. 解释过采样为何可能改善子空间而不保证每次改善。
4. 写出报告必须保存的四个随机化参数。

## 练习答案提示

1. 用 $Q^TQ=I$ 与 $\widetilde U^T\widetilde U=I$ 相乘。
2. 固定其余参数，多次运行并同时报告种子和误差。
3. 更多随机方向可能覆盖主子空间，但仍受抽样和数值条件影响。
4. 至少包括种子、目标秩、过采样量和幂迭代次数。

## 延伸

[随机范围发现](/linear-algebra/randomized-range-finder)解释 $Q$ 的来源；[SVD](/linear-algebra/svd)给出精确低秩最优性的参照；[低秩图像压缩](/linear-algebra/low-rank-image-compression)展示重构误差的应用。
