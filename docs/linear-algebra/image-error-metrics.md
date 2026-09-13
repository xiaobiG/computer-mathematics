---
title: 图像误差指标：MSE、PSNR 与“压缩得好”的边界
description: 将低秩重构的逐像素差写成 MSE、RMSE、PSNR 和最大误差，并用可重放报告区分数值保真与感知质量。
courseLevel: "2–3（误差度量、实验审计与工程边界）"
prerequisites: "Frobenius 范数、低秩近似与平方根"
estimatedMinutes: 70
experiment: "消费已验证的随机 SVD 重构，计算 MSE、RMSE、PSNR、最大误差并审计 MSE 预算"
---

# 图像误差指标：MSE、PSNR 与“压缩得好”的边界

## 学习目标

读完后，你能把两张同形灰度图的差写成 MSE、RMSE、PSNR 与最大绝对误差；并能解释全局 SSIM 与固定局部窗口为何回答不同问题。

## 从一个计算问题开始

低秩压缩器报告 $\|A-\hat A\|_F=20$。它随像素数增长，不能跨尺寸比较，也不暴露最坏像素；须转换为按样本归一的指标。

## 定义：从残差到四种报告数

令 $e_{ij}=A_{ij}-\hat A_{ij}$，样本数 $N=mn$。定义

$$
\mathrm{MSE}=\frac1N\sum_{i,j}e_{ij}^2,
\qquad \mathrm{RMSE}=\sqrt{\mathrm{MSE}},
\qquad E_\infty=\max_{i,j}|e_{ij}|.
$$

对于峰值为 $P$ 的编码（8 位灰度通常取 $P=255$），当 MSE 非零时

$$
\mathrm{PSNR}=20\log_{10}\frac{P}{\mathrm{RMSE}}
=10\log_{10}\frac{P^2}{\mathrm{MSE}}.
$$

MSE 重惩罚大偏差，RMSE 恢复量纲，$E_\infty$ 暴露最坏点；PSNR 是对数刻度。MSE 为零时 PSNR 为 $+\infty$。

## 分步推导：Frobenius 误差如何变成 MSE

Frobenius 范数定义为

$$
\|A-\hat A\|_F^2=\sum_{i,j}e_{ij}^2.
$$

两边除以 $N$，便得到

$$
\mathrm{MSE}=\frac{\|A-\hat A\|_F^2}{N},
\qquad
\mathrm{RMSE}=\frac{\|A-\hat A\|_F}{\sqrt N}.
$$

因此，同样的 Frobenius 误差在更大的图上对应更小的平均每像素误差。再代入 PSNR 定义得到第二个等式。若 RMSE 减半，PSNR 增加 $20\log_{10}2\approx6.02$ dB；PSNR 不是线性百分比分数。

## 算法实现：生成并核对报告

```python
from projects.linear_algebra_lab.image_metrics import image_quality_certificate, image_quality_report

reference = [[0.0, 255.0]]
approximation = [[0.0, 0.0]]
report = image_quality_report(reference, approximation, peak=255.0)

assert report.samples == 2
assert report.mse == 255.0 ** 2 / 2
assert report.max_absolute_error == 255.0
assert image_quality_certificate(reference, approximation, report)
```

运行 `python -m unittest projects.linear_algebra_lab.test_image_metrics`。报告先检查两幅图均为同形、非空、有限数值矩阵，再以一次扫描计算所有量。证书不信任存储的数字：它从输入重新计算 MSE、RMSE、PSNR 和最大误差，会拒绝被改过的字段。时间为 $O(N)$，除了常数个累加器外额外空间为 $O(1)$。

## 跨课实验：审计随机 SVD 的实际像素误差

`randomized_svd_image_quality_review` 先重放上游 SVD 产物，再把实际重构与声明的 MSE 预算比较：

```python
from projects.linear_algebra_lab.image_metrics import randomized_svd_image_quality_review
from projects.linear_algebra_lab.randomized_svd import randomized_svd_report

pixels = [[5.0, 0.0], [0.0, 1.0]]
svd_report = randomized_svd_report(pixels, rank=1, oversampling=1, seed=3)
review = randomized_svd_image_quality_review(pixels, svd_report, mse_budget=0.3, peak=5.0)

assert review.source_seed == 3
assert review.mse_budget_status == "within_mse_budget"
assert review.automatic_action == "none"
```

`mse_budget=0.2` 会拒绝同一重构；它不推出视觉或部署结论。

## 正确性与复杂度

逐像素累加 $e_{ij}^2,|e_{ij}|$ 得到 MSE 与最大误差；MSE 为零时 PSNR 为无穷。这验证度量，不证明低秩最优、感知或任务质量。

## 局部窗口：全局 SSIM 不能定位缺陷

全局 SSIM 不能指出坏区域。实验按完整、不重叠的固定窗口报告整图分数、各窗口分数与最差坐标：

```python
from projects.linear_algebra_lab.image_metrics import local_structural_similarity_report

reference = [[128.0] * 4 for _ in range(4)]
approximation = [[128.0] * 4 for _ in range(4)]
for row in range(2):
    for column in range(2):
        approximation[row][column] = 0.0

report = local_structural_similarity_report(reference, approximation, 2, 2)
assert (report.worst_window_row, report.worst_window_column) == (0, 0)
assert report.worst_window_ssim < report.global_ssim
```

窗口尺寸必须整除图像；固定灰度平铺只定位数值弱点，不代表感知或任务质量。

## 线性 RGB：相同通道 MSE 不等于相同亮度误差

在线性 RGB 中，$Y=0.2126R+0.7152G+0.0722B$。红色与绿色通道各偏 10 时，逐通道平均 MSE 相同，亮度误差却不同：

```python
from projects.linear_algebra_lab.image_metrics import linear_rgb_error_report

reference = [[[0.0, 0.0, 0.0]]]
red = linear_rgb_error_report(reference, [[[10.0, 0.0, 0.0]]])
green = linear_rgb_error_report(reference, [[[0.0, 10.0, 0.0]]])
assert red.rgb_mse == green.rgb_mse
assert red.linear_luminance_mse < green.linear_luminance_mse
```

该报告只接受线性 RGB；编码 sRGB 必须先线性化，且不代表外观或感知。

## 编码 sRGB：错误空间会改变预算

“先线性化”不是格式洁癖。归一化的 sRGB 代码值 $c\in[0,1]$ 通过分段传递函数变成线性分量 $L$：

$$
L(c)=
\begin{cases}
c/12.92,&c\le0.04045,\\
\left((c+0.055)/1.055\right)^{2.4},&c>0.04045.
\end{cases}
$$

同一对编码像素走两条路径：直接做线性算术，或先解码再用 Rec.709 系数。声明预算 $0.005$ 令状态相反：

```python
from projects.linear_algebra_lab.image_metrics import (
    srgb_linear_luminance_comparison,
    srgb_linear_luminance_comparison_certificate,
)

reference = [[[0.0, 0.0, 0.0]]]
encoded_red = [[[0.5, 0.0, 0.0]]]
report = srgb_linear_luminance_comparison(reference, encoded_red, luminance_mse_budget=0.005)

assert report.encoded_budget_status == "exceeds_luminance_mse_budget"
assert report.decoded_budget_status == "within_luminance_mse_budget"
assert srgb_linear_luminance_comparison_certificate(reference, encoded_red, report)
```

编码 $0.5$ 不等于线性光强 $0.5$，故两条路径回答不同数值问题。报告重放传递函数、系数、预算与状态，且固定 `automatic_action="none"`。它不读文件或 ICC，不处理色域、显示条件、感知、色彩 SSIM 或任务质量。

## 失败案例与工程边界

- **相同 MSE、不同可见性**：孤立的大错误和分散噪声可有相同 MSE；固定窗口只能定位，不能判定感知。
- **编码与量化**：峰值、裁剪和量化都会改变结论；线性 RGB 的亮度加权也不等于色彩感知。
- **任务错位**：PSNR 或 SSIM 更高不保证识别、检索、公平性或安全性更好。

## 常见误区

1. “PSNR 是百分比。”错误：它是对数比值，不能按线性比例解释。
2. “同一个 Frobenius 误差可跨尺寸直接比较。”错误：必须至少报告样本数或换为 MSE/RMSE。
3. “PSNR 无穷说明编码器最强。”错误：只说明当前两份数值矩阵完全相等。
4. “MSE 小就等于视觉质量高。”错误：它只测逐像素平方差，不含人类感知或任务目标。

## 练习

1. **基础题**：若四个像素误差为 $1,-1,1,-1$，计算 MSE、RMSE 与最大绝对误差。
2. **推导题**：从 $\|A-\hat A\|_F$ 推导 RMSE 的归一化式，并说明为何面积变成四倍时不能只比较原始范数。
3. **编码题**：为 `image_quality_report` 增加逐行 MSE 报告，并为篡改的一行结果写一个拒绝测试。
4. **开放题**：设计同时报告 PSNR、最大误差、文件大小、主观评审与检索指标的压缩实验。

## 练习答案提示

1. 平方误差均为 1，故 MSE 为 1、RMSE 为 1、最大绝对误差也为 1；先确认像素数是 4。
2. Frobenius 平方是误差平方和；面积四倍时，相同像素误差的范数变两倍。
3. 行报告须重算每行与聚合值，不能只信最终均值。
4. 它们分别回答数值、局部、存储、感知与任务问题。

## 延伸

[低秩图像压缩](/linear-algebra/low-rank-image-compression)产生重构；[SVD](/linear-algebra/svd)讨论 Frobenius 最优性；[浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)解释证书容差。感知指标与真实文件编码需另行声明模型。
