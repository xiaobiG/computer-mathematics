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

`randomized_svd_image_quality_review` 重放上游 SVD 后才比较重构与 MSE 预算；同一 `pixels=[[5,0],[0,1]]`、`rank=1, seed=3, mse_budget=.3` 通过，预算 `.2` 不通过。它不推出视觉或部署结论。

## 局部窗口：全局 SSIM 不能定位缺陷

`local_structural_similarity_report` 以完整、不重叠且整除图像的窗口报告整图、各窗和最差坐标。对 $4\times4$ 的常数 128 图，将左上 $2\times2$ 改为 0，会得到最差坐标 $(0,0)$ 且其分数低于整图。它只定位数值弱点。

## 线性 RGB：相同通道 MSE 不等于相同亮度误差

在线性 RGB 中，$Y=.2126R+.7152G+.0722B$。黑色参考下红或绿通道各偏 10 的通道 MSE 相同，但前者亮度 MSE 更小；`linear_rgb_error_report` 可重算。它只接受线性 RGB，不代表外观。

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

编码 $0.5$ 不等于线性光强 $0.5$，故两条路径回答不同数值问题。报告重放传递函数、系数、预算与状态，且固定 `automatic_action="none"`。

## 从 RGB 距离到 CIE 色差：必须声明白点

`srgb_cielab_delta_e76_comparison` 固定 sRGB/D65：解码后以 sRGB$\to XYZ_{D65}$ 矩阵变换，再按 CIE Lab 的分段 $f(t)$ 映射；$W=(0.95047,1,1.08883)$，并报告

$$
\Delta E_{76}=\sqrt{(\Delta L^*)^2+(\Delta a^*)^2+(\Delta b^*)^2}
$$

的均值、最大值与预算。读者可用 `srgb_to_cielab_d65((1,1,1))` 核对约为 $(100,0,0)$，再用 `cielab_delta_e76` 手算距离；证书绑定编码、白点与结论。模型来源为 [CIE 15:2018](https://cie.co.at/publications/colorimetry-4th-edition) 与 [ICC sRGB 登记](https://registry.color.org/rgb-registry/srgb)。它不是 ICC profile、色域映射、色适应、显示条件、CIEDE2000、视觉偏好或自动验收。

## 失败案例与工程边界

- 相同 MSE 的孤立错误与噪声仍可能不同；窗口只定位。
- 峰值、量化、D65 与任务目标都会改变解释；PSNR、SSIM、$\Delta E_{76}$ 均不保证识别或视觉偏好。

## 常见误区

1. PSNR 是对数比值，不是百分比。
2. Frobenius 误差跨尺寸应先归一化为 MSE/RMSE。
3. PSNR 无穷只说明当前两矩阵相等。
4. MSE 小不推出视觉或任务质量高。

## 练习

1. **基础题**：若四个像素误差为 $1,-1,1,-1$，计算 MSE、RMSE 与最大绝对误差。
2. **推导题**：从 $\|A-\hat A\|_F$ 推导 RMSE 的归一化式，并说明为何面积变成四倍时不能只比较原始范数。
3. **编码题**：为 `image_quality_report` 增加逐行 MSE 报告，并为篡改的一行结果写一个拒绝测试。
4. **开放题**：设计同时报告 PSNR、$\Delta E$、文件大小、主观评审与检索指标的压缩实验。

## 练习答案提示

1. 平方误差均为 1，故 MSE 为 1、RMSE 为 1、最大绝对误差也为 1；先确认像素数是 4。
2. Frobenius 平方是误差平方和；面积四倍时，相同像素误差的范数变两倍。
3. 行报告须重算每行与聚合值，不能只信最终均值。
4. 它们分别回答数值、色差、存储、感知与任务问题。

## 延伸

[低秩图像压缩](/linear-algebra/low-rank-image-compression)产生重构；[SVD](/linear-algebra/svd)讨论 Frobenius 最优性；[浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)解释证书容差。真实 profile、显示与感知模型仍须另行声明。
