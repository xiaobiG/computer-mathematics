---
title: 项目：线性代数实验室
description: 用可测试的教学实现串起矩阵计算、消元、投影、低秩压缩与推荐。
---

# 项目：线性代数实验室

## 目标

本项目把线性代数专题的关键操作做成小型、可测试的 Python 模块：矩阵乘法、列独立性和基坐标重构、带部分选主元且可重放的方程求解、正规方程与 QR 的最小二乘对照、双数前向自动微分、二维 PCA、向量投影、幂迭代、低秩压缩、把灰度矩阵展平后的余弦相似度检索、带种子重放的随机范围发现，以及只在观测评分上拟合的秩一 ALS。`pivot_trace_certificate` 从原始增广矩阵重放主元选择、行交换、消元和回代；`column_independence_report` 用逐列正交残差和秩检查冗余方向，`basis_coordinate_report` 用 $Ac-b$ 检查坐标重构；`demo_jvp_certificate` 将双数 JVP 与 $\nabla L^Tv$ 对照；`least_squares_comparison_report` 用同一份 $A^Tr$ 证书检查两条拟合路径；`pca_2d_report` 检查中心化、投影正交性和舍弃方差—重构误差恒等式；`compressed_image_search` 将压缩误差和压缩域排序放入同一报告，形成微型“压缩—检索”流程；`image_quality_certificate` 重算 MSE、RMSE、PSNR 与最大误差；`randomized_range_certificate` 重建固定种子的随机草图和 $QQ^TA$；`rank_one_als_trace_certificate` 重放每轮用户/物品的坐标最小化，核对观测集误差而不假装验证缺失评分。它们用于核对数学定义，不取代 NumPy/SciPy 的生产实现。

## 数学连接

- [矩阵乘法](/linear-algebra/matrix-multiplication)：复合线性变换；
- [线性组合、基与维度](/linear-algebra/linear-combinations-basis)：以逐列残差识别冗余方向，并验证非标准基坐标重构。
- [Jacobian、Hessian 与自动微分](/linear-algebra/jacobian-hessian-autodiff)：用双数前向模式核对 JVP 与梯度点积。
- [高斯消元](/linear-algebra/gaussian-elimination)：保持解集的行变换；
- [最小二乘](/linear-algebra/least-squares)：以正规方程和 QR 的同题比较验证投影残差。
- [幂迭代](/linear-algebra/power-iteration)：以 Rayleigh 商和残差审查主特征方向。
- [特征值与 PCA](/linear-algebra/eigenvalues-pca)：从中心化协方差到投影重构，并核对舍弃方差证书。
- [SVD](/linear-algebra/svd)：通过 $A^TA$ 的幂迭代获得主奇异方向；另以已验证的谱尾公式计算精确截断误差与参数量。
- [低秩图像压缩](/linear-algebra/low-rank-image-compression)：以逐次秩一近似比较保留秩与重构误差。
- [图像误差指标](/linear-algebra/image-error-metrics)：将同一重构残差转换为 MSE、RMSE、PSNR 与最大误差。
- [随机范围发现](/linear-algebra/randomized-range-finder)：用带种子的随机草图构造可重放的 $QQ^TA$ 投影。
- [低秩推荐](/linear-algebra/low-rank-recommendation)：只对观测评分做交替最小二乘，并分离训练误差与缺失预测。
- [向量与点积](/linear-algebra/vectors-dot-product)：以余弦相似度对同形图像向量排序。

## 压缩—检索实验

```python
from projects.linear_algebra_lab.main import compressed_image_search

query = [[8.0, 0.0], [0.0, 3.0]]
report = compressed_image_search(query, [query, [[0.0, 3.0], [8.0, 0.0]]], rank=2, iterations=120)
assert report["ranking"][0][0] == 0
assert report["query_error"] < 1e-9
```

报告同时给出查询/图库各自的分量数、Frobenius 压缩误差与余弦相似度排序。测试验证精确重构的小例中原图排第一；当使用较低秩或有限迭代时，必须另外观察误差和排序是否改变，不能从“压缩误差小”直接推断语义检索仍正确。

## 推荐实验

```python
from projects.linear_algebra_lab.recommendation import rank_one_als_report, rank_one_als_trace_certificate

ratings = [[5.0, None, 2.0], [4.0, 2.0, None], [None, 1.0, 1.0]]
report = rank_one_als_report(ratings, iterations=20, regularization=0.1)
assert report.observed_rmse < 0.7
assert rank_one_als_trace_certificate(ratings, report, iterations=20, regularization=0.1)
```

这个报告仅度量已观测评分上的拟合误差。没有评分的用户或物品会被显式拒绝为冷启动，而不是偷偷填零；未观测格的数值是模型假设产生的预测，仍需要留出集与在线指标验证。

## 图像误差实验

```python
from projects.linear_algebra_lab.image_metrics import image_quality_report

report = image_quality_report([[0.0, 255.0]], [[0.0, 0.0]])
assert report.mse == 255.0 ** 2 / 2
assert report.max_absolute_error == 255.0
```

PSNR 将像素 RMSE 与约定峰值联系起来；它仍只是逐像素数值度量，不能替代感知质量或检索质量的评估。

## 随机范围发现实验

```python
from projects.linear_algebra_lab.randomized_range import randomized_range_report

matrix = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]]
report = randomized_range_report(matrix, rank=1, oversampling=1, seed=17)
assert report.frobenius_error < 1e-10
```

报告记录 seed 与实际正交基的列数；在慢衰减谱上需比较多个 seed、过采样和幂迭代，而不是将一次运行当作通用误差界。

## 运行

```bash
python -m unittest projects.linear_algebra_lab.test_main
python -m unittest projects.linear_algebra_lab.test_power_iteration
python -m unittest projects.linear_algebra_lab.test_pca
python -m unittest projects.linear_algebra_lab.test_basis
python -m unittest projects.linear_algebra_lab.test_forward_autodiff
python -m unittest projects.linear_algebra_lab.test_image_metrics
python -m unittest projects.linear_algebra_lab.test_randomized_range
python -m unittest projects.linear_algebra_lab.test_recommendation
```

测试覆盖矩阵形状错误、非交换变换、列独立性与基坐标重构、选主元、奇异系统、正规方程与 QR 的最小二乘一致性及 $A^Tr$ 证书、双数 JVP 与梯度点积、二维 PCA 的中心化/正交/舍弃方差证书、正交投影、幂迭代残差与失败边界、秩一矩阵重建、精确谱尾误差、低秩参数节省、更高保留秩不增加小例重构误差、压缩—检索联合报告、同形图像的余弦检索、MSE/RMSE/PSNR 报告与篡改拒绝、固定种子的随机范围发现及其轨迹篡改拒绝，以及 ALS 观测误差与轨迹篡改/冷启动边界。完整项目测试仍可通过 `npm run projects:test` 运行。

## 挑战

1. 为 `solve` 增加多右侧向量的支持；
2. 为投影加入正交基上的逐步投影；
3. 使用 NumPy 比较教学实现与生产库在病态矩阵上的差异。
4. 对灰度小图逐次提取秩一分量，记录压缩率与 Frobenius 误差。
5. 为秩一 ALS 加入用户/物品偏置，并设计按时间切分的留出评估。

## 工程边界

模块仅使用密集 Python 列表和绝对容差，适合小矩阵教学。幂迭代只近似最大奇异方向，可能因谱间隙小而收敛缓慢，不能替代生产级 SVD。大型、稀疏或病态问题应采用成熟数值库及相对容差策略。
