---
title: 结构相似度 SSIM：为何同样的 MSE 看起来不同
description: 从均值、方差与协方差构造全局 SSIM，并与 MSE/PSNR 对照其结构敏感性和感知边界。
courseLevel: "2–3（矩阵统计、误差度量与工程边界）"
prerequisites: "均值、方差、协方差、MSE 与 PSNR"
estimatedMinutes: 60
experiment: "为两幅小灰度矩阵重放全局 SSIM、统计量与证书"
---

# 结构相似度 SSIM：为何同样的 MSE 看起来不同

## 学习目标

你将能由均值、方差和协方差计算全局 SSIM，并区分它、窗口 SSIM 与真实感知质量。

## 从一个计算问题开始

MSE 独立比较每个坐标，不能说明亮暗变化是否共同出现。SSIM 用两组矩阵统计量比较亮度、对比度和结构。

## 定义与推导

把矩阵展平为 $x_1,\ldots,x_N$ 与 $y_1,\ldots,y_N$。样本均值、方差和协方差为 $\mu_x,\mu_y,\sigma_x^2,\sigma_y^2,\sigma_{xy}$；本课采用分母 $N-1$ 的样本统计量，故必须有 $N\ge2$。设 $C_1=(K_1P)^2,C_2=(K_2P)^2$，本课使用全局形式

$$\mathrm{SSIM}(x,y)=\frac{(2\mu_x\mu_y+C_1)(2\sigma_{xy}+C_2)}{(\mu_x^2+\mu_y^2+C_1)(\sigma_x^2+\sigma_y^2+C_2)}.$$

第一项比较亮度，第二项由协方差比较对比度/结构。$C_1,C_2$ 在低方差或低亮度时避免分母不稳定。完全相同的有限矩阵有相同均值、方差与协方差，因此 SSIM 为 1。

## 可运行实验

```python
from projects.linear_algebra_lab.image_metrics import (
    structural_similarity_certificate, structural_similarity_report,
)

reference = [[0.0, 255.0], [0.0, 255.0]]
reversed_columns = [[255.0, 0.0], [255.0, 0.0]]
report = structural_similarity_report(reference, reversed_columns)
assert report.ssim < 0.0
assert structural_similarity_certificate(reference, reversed_columns, report)
```

运行 `python -m unittest projects.linear_algebra_lab.test_image_metrics`。实现用分母 $N-1$ 的样本方差；证书从矩阵与 $P,K_1,K_2$ 重建报告，篡改协方差或 SSIM 会失败。时间为 $O(N)$，教学实现为便于审计显式展平，额外空间为 $O(N)$。

## 正确性与边界

相同矩阵的全局 SSIM 为 1；列反转的负协方差使它低于 0。结论依赖峰值、常量和全局聚合，不能把固定范围脱离输入契约解释。

生产评估还须声明窗口、色彩空间、动态范围和聚合。本课不加载图像文件、不模拟视觉或以单个分数替代任务测量。单像素图或 $1\times1$ 局部窗口没有样本方差/协方差；实现会拒绝它们，而不是把方差静默设为零并误称结构分数。

## 共享 MSE 后，结构项还留下什么

为避免把“SSIM 更高”误说成“只是 MSE 更小”，下面固定每个像素的误差平方平均值。常量亮度偏移与交错的正负噪声都使每个像素偏离 $10$，故 MSE 都是 $100$；但前者保留常量结构，后者引入交错方差，全局 SSIM 会不同：

```python
from projects.linear_algebra_lab.image_metrics import (
    same_mse_structural_comparison_certificate,
    same_mse_structural_comparison_report,
)

reference = [[128.0] * 4 for _ in range(4)]
brightness_shift = [[138.0] * 4 for _ in range(4)]
alternating_noise = [[118.0 if (r + c) % 2 == 0 else 138.0 for c in range(4)] for r in range(4)]
report = same_mse_structural_comparison_report(reference, brightness_shift, alternating_noise)
assert report.first_quality.mse == report.second_quality.mse == 100.0
assert report.higher_ssim == "first"
assert same_mse_structural_comparison_certificate(reference, brightness_shift, alternating_noise, report)
```

报告拒绝 MSE 不同的输入，并重放两份指标及排序。它只区分给定公式下的有限矩阵；不把常量偏移升级为人眼偏好，`automatic_action` 固定为 `none`。

## 失败案例与工程边界

- **局部损坏。** 全局平均可能稀释小块伪影。
- **颜色、窗口或参数不同。** 数字不能直接比较。
- **安全门槛。** 高 SSIM 不保证文字、医疗细节或分类正确。

## 常见误区

- **“SSIM 是百分比或取代 MSE。”** 错；两者依赖不同定义并回答不同问题。
- **“负值或相同均值是错误/同结构。”** 错；还要看协方差与方差。

## 练习

1. 为什么协方差需要保留正负号，而不能只取绝对值？
2. 证明完全相同矩阵的全局 SSIM 为 1。
3. 将 $K_1,K_2$ 改为更大值，观察低对比小矩阵的分数如何变化。
4. 设计一个同时报告 MSE、PSNR、全局/窗口 SSIM 和人工任务成功率的实验。

## 练习答案提示

1. 负号记录反向变化，不能取绝对值。
2. 代入相同均值、方差和协方差后分子分母相同。
3. 常量是模型选择，不是万能默认值。
4. 声明颜色、窗口、峰值、样本和任务，分开解释各指标。

## 延伸

[图像误差指标：MSE、PSNR](/linear-algebra/image-error-metrics)给出逐像素基线；[低秩图像压缩](/linear-algebra/low-rank-image-compression)产生重构；[协方差与相关性](/probability-ml/covariance-correlation)复习共同变化。
