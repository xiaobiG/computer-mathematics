---
title: 项目：线性代数实验室
description: 用可测试的教学实现串起矩阵乘法、消元、投影和低秩图像压缩。
---

# 项目：线性代数实验室

## 目标

本项目把线性代数专题的关键操作做成小型、可测试的 Python 模块：矩阵乘法、带部分选主元的方程求解、正规方程与 QR 的最小二乘对照、二维 PCA、向量投影、幂迭代、低秩压缩，以及把灰度矩阵展平后的余弦相似度检索。`least_squares_comparison_report` 用同一份 $A^Tr$ 证书检查两条拟合路径；`pca_2d_report` 检查中心化、投影正交性和舍弃方差—重构误差恒等式；`compressed_image_search` 将压缩误差和压缩域排序放入同一报告，形成微型“压缩—检索”流程。它们用于核对数学定义，不取代 NumPy/SciPy 的生产实现。

## 数学连接

- [矩阵乘法](/linear-algebra/matrix-multiplication)：复合线性变换；
- [高斯消元](/linear-algebra/gaussian-elimination)：保持解集的行变换；
- [最小二乘](/linear-algebra/least-squares)：以正规方程和 QR 的同题比较验证投影残差。
- [幂迭代](/linear-algebra/power-iteration)：以 Rayleigh 商和残差审查主特征方向。
- [特征值与 PCA](/linear-algebra/eigenvalues-pca)：从中心化协方差到投影重构，并核对舍弃方差证书。
- [SVD](/linear-algebra/svd)：通过 $A^TA$ 的幂迭代获得主奇异方向；另以已验证的谱尾公式计算精确截断误差与参数量。
- [低秩图像压缩](/linear-algebra/low-rank-image-compression)：以逐次秩一近似比较保留秩与重构误差。
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

## 运行

```bash
python -m unittest projects.linear_algebra_lab.test_main
python -m unittest projects.linear_algebra_lab.test_power_iteration
python -m unittest projects.linear_algebra_lab.test_pca
```

测试覆盖矩阵形状错误、非交换变换、选主元、奇异系统、正规方程与 QR 的最小二乘一致性及 $A^Tr$ 证书、二维 PCA 的中心化/正交/舍弃方差证书、正交投影、幂迭代残差与失败边界、秩一矩阵重建、精确谱尾误差、低秩参数节省、更高保留秩不增加小例重构误差、压缩—检索联合报告，以及同形图像的余弦检索。完整项目测试仍可通过 `npm run projects:test` 运行。

## 挑战

1. 为 `solve` 增加多右侧向量的支持；
2. 为投影加入正交基上的逐步投影；
3. 使用 NumPy 比较教学实现与生产库在病态矩阵上的差异。
4. 对灰度小图逐次提取秩一分量，记录压缩率与 Frobenius 误差。

## 工程边界

模块仅使用密集 Python 列表和绝对容差，适合小矩阵教学。幂迭代只近似最大奇异方向，可能因谱间隙小而收敛缓慢，不能替代生产级 SVD。大型、稀疏或病态问题应采用成熟数值库及相对容差策略。
