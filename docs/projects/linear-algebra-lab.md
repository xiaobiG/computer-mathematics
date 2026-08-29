---
title: 项目：线性代数实验室
description: 用可测试的教学实现串起矩阵乘法、消元、投影和低秩图像压缩。
---

# 项目：线性代数实验室

## 目标

本项目把线性代数专题的关键操作做成小型、可测试的 Python 模块：矩阵乘法、带部分选主元的方程求解、向量投影、低秩压缩，以及把灰度矩阵展平后的余弦相似度检索。它们用于核对数学定义，不取代 NumPy/SciPy 的生产实现。

## 数学连接

- [矩阵乘法](/linear-algebra/matrix-multiplication)：复合线性变换；
- [高斯消元](/linear-algebra/gaussian-elimination)：保持解集的行变换；
- [最小二乘](/linear-algebra/least-squares)：投影与残差的基本构件。
- [SVD](/linear-algebra/svd)：通过 $A^TA$ 的幂迭代获得主奇异方向，并重建秩一近似。
- [低秩图像压缩](/linear-algebra/low-rank-image-compression)：以逐次秩一近似比较保留秩与重构误差。
- [向量与点积](/linear-algebra/vectors-dot-product)：以余弦相似度对同形图像向量排序。

## 运行

```bash
python -m unittest projects.linear_algebra_lab.test_main
```

测试覆盖矩阵形状错误、非交换变换、选主元、奇异系统、正交投影、秩一矩阵重建、更高保留秩不增加小例重构误差，以及同形图像的余弦检索。完整项目测试仍可通过 `npm run projects:test` 运行。

## 挑战

1. 为 `solve` 增加多右侧向量的支持；
2. 为投影加入正交基上的逐步投影；
3. 使用 NumPy 比较教学实现与生产库在病态矩阵上的差异。
4. 对灰度小图逐次提取秩一分量，记录压缩率与 Frobenius 误差。

## 工程边界

模块仅使用密集 Python 列表和绝对容差，适合小矩阵教学。幂迭代只近似最大奇异方向，可能因谱间隙小而收敛缓慢，不能替代生产级 SVD。大型、稀疏或病态问题应采用成熟数值库及相对容差策略。
