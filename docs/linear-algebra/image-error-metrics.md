---
title: 图像误差指标：MSE、PSNR 与“压缩得好”的边界
description: 将低秩重构的逐像素差写成 MSE、RMSE、PSNR 和最大误差，并用可重放报告区分数值保真与感知质量。
courseLevel: "2–3（误差度量、实验审计与工程边界）"
prerequisites: "Frobenius 范数、低秩近似与平方根"
estimatedMinutes: 55
experiment: "为同一对灰度矩阵计算 MSE、RMSE、PSNR、最大误差并重放报告"
---

# 图像误差指标：MSE、PSNR 与“压缩得好”的边界

## 学习目标

读完后，你能把两张同形灰度图的差写成 MSE、RMSE、PSNR 与最大绝对误差；从 Frobenius 范数推导它们的关系；运行可重放的误差报告；并能说明为何高 PSNR 既不是视觉质量证明，也不是下游任务正确性的证明。

## 从一个计算问题开始

低秩压缩器重构出一张 $m\times n$ 图像 $\hat A$，并报告 $\|A-\hat A\|_F=20$。这个 `20` 到底大不大？它随像素数量增长，无法直接比较 $32\times32$ 缩略图和 $4K$ 图像；它也没有说明最坏的一个像素偏了多少。需要把同一份逐像素残差转换成按样本归一、且与像素峰值相关的指标。

## 定义：从残差到四种报告数

令 $e_{ij}=A_{ij}-\hat A_{ij}$，样本数 $N=mn$。定义

$$
\operatorname{MSE}=\frac1N\sum_{i,j}e_{ij}^2,
\qquad \operatorname{RMSE}=\sqrt{\operatorname{MSE}},
\qquad E_\infty=\max_{i,j}|e_{ij}|.
$$

对于峰值为 $P$ 的编码（8 位灰度通常取 $P=255$），当 MSE 非零时

$$
\operatorname{PSNR}=20\log_{10}\frac{P}{\operatorname{RMSE}}
=10\log_{10}\frac{P^2}{\operatorname{MSE}}.
$$

MSE 是平均平方误差，较重惩罚大偏差；RMSE 恢复原像素量纲；$E_\infty$ 暴露最坏点；PSNR 是 RMSE 相对于表示范围的对数刻度。完全相同的图像 MSE 为零，PSNR 写作 $+\infty$，而不是选一个任意大的有限数字。

## 分步推导：Frobenius 误差如何变成 MSE

Frobenius 范数定义为

$$
\|A-\hat A\|_F^2=\sum_{i,j}e_{ij}^2.
$$

两边除以 $N$，便得到

$$
\operatorname{MSE}=\frac{\|A-\hat A\|_F^2}{N},
\qquad
\operatorname{RMSE}=\frac{\|A-\hat A\|_F}{\sqrt N}.
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

## 正确性与复杂度

每个像素恰好贡献一次 $e_{ij}^2$ 与 $|e_{ij}|$，故累加器分别等于定义中的求和与最大值；除以样本数和开平方便给出 MSE、RMSE。只要 MSE 正，PSNR 的两种写法由 $\operatorname{RMSE}^2=\operatorname{MSE}$ 与对数规则严格等价。MSE 为零时不做除零，而是按定义报告无穷 PSNR。

这验证的是**度量实现**，不是低秩算法的最优性。只有精确截断 SVD 才有特定秩约束下 Frobenius 最优的定理；有限迭代的教学压缩器必须把实际误差另外测量。

## 失败案例与工程边界

- **相同 MSE、不同视觉效果**：一个孤立的 255 像素错误与分散的小噪声可以有相同 MSE，却可能有不同可见性。
- **峰值不明**：把 `[0,1]` 浮点图像错误地按 $P=255$ 报 PSNR，会得到没有意义的高数值；峰值必须随编码契约传入。
- **逐通道问题**：彩色图像究竟在 RGB、线性光还是亮度空间测误差，会改变结论；本实验只处理一个灰度矩阵。
- **裁剪和量化**：低秩重构可越出 `[0,255]`；输出前的裁剪、舍入和编码会形成另一份误差报告。
- **任务错位**：更高 PSNR 不保证人更易辨认物体，也不保证分类、检索、公平性或安全检查更好。

## 常见误区

1. “PSNR 是百分比。”错误：它是对数比值，不能按线性比例解释。
2. “同一个 Frobenius 误差可跨尺寸直接比较。”错误：必须至少报告样本数或换为 MSE/RMSE。
3. “PSNR 无穷说明编码器最强。”错误：只说明当前两份数值矩阵完全相等。
4. “MSE 小就等于视觉质量高。”错误：它只测逐像素平方差，不含人类感知或任务目标。

## 练习

1. **基础题**：若四个像素误差为 $1,-1,1,-1$，计算 MSE、RMSE 与最大绝对误差。
2. **推导题**：从 $\|A-\hat A\|_F$ 推导 RMSE 的归一化式，并说明为何面积变成四倍时不能只比较原始范数。
3. **编码题**：为 `image_quality_report` 增加逐行 MSE 报告，并为篡改的一行结果写一个拒绝测试。
4. **开放题**：设计一个压缩实验：同时报告 PSNR、最大误差、文件大小、主观评审与检索指标，并说明每一项回答的不同问题。

## 练习答案提示

1. 平方误差均为 1，故 MSE 为 1、RMSE 为 1、最大绝对误差也为 1；先确认像素数是 4。
2. Frobenius 范数平方是全部误差平方和，除以像素数后开平方即 RMSE；面积增为四倍时，同样的逐像素误差会让原始 Frobenius 范数变为两倍。
3. 每行报告应包含行像素数、平方误差和与该行 MSE；证书要重算聚合值，篡改任一行后应拒绝而非只比较最终均值。
4. PSNR 测逐像素对数误差，最大误差测最坏局部偏差，文件大小测存储，主观评审和检索指标分别测感知与任务质量，不能互相替代。

## 延伸

[低秩图像压缩](/linear-algebra/low-rank-image-compression)提供产生重构矩阵的低秩算法；[SVD](/linear-algebra/svd)说明何时 Frobenius 误差具有最优性；[浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)解释为何证书比较需要明确容差。下一步可研究 SSIM、感知指标、随机 SVD 与真实文件编码，但应单独说明它们的模型假设与失效模式。
