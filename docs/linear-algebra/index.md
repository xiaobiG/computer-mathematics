# 程序员的线性代数

**v0.2 已完成。** 本专题把线性代数讲成一条可执行的链：用向量表示对象，用矩阵表示变换，用消元或投影求解问题，最后以 PCA、SVD 压缩数据。

## 学习方式

每篇正文含有前置知识、推导、手算、代码、工程边界和三级练习。建议每周完成一篇，并在最后用[线性代数实验室](/projects/linear-algebra-lab)复现矩阵乘法、消元与投影。

## 课程地图

| 顺序 | 主题 | 你将解决的问题 | 状态 |
| --- | --- | --- | --- |
| 1 | [向量与点积](/linear-algebra/vectors-dot-product) | 两个对象的方向是否相近？ | 深度正文 · 45 分钟 |
| 2 | [线性组合、基与维度](/linear-algebra/linear-combinations-basis) | 哪些特征是冗余的？ | 深度正文 · 40 分钟 |
| 3 | [矩阵的四个基本子空间](/linear-algebra/four-fundamental-subspaces) | 哪些输出可达、哪些信息丢失？ | 深度正文 · 60 分钟 |
| 4 | [矩阵乘法与线性变换](/linear-algebra/matrix-multiplication) | 多个变换如何合成为一步？ | 深度正文 · 45 分钟 |
| 5 | [高斯消元](/linear-algebra/gaussian-elimination) | 方程组有哪一种解？ | 深度正文 · 50 分钟 |
| 6 | [正交投影、Gram–Schmidt 与 QR](/linear-algebra/orthogonal-projection-qr) | 如何稳定地求最近解？ | 深度正文 · 70 分钟 |
| 7 | [最小二乘](/linear-algebra/least-squares) | 没有精确解时如何拟合？ | 深度正文 · 50 分钟 |
| 8 | [特征值与 PCA](/linear-algebra/eigenvalues-pca) | 如何保留数据最重要方向？ | 深度正文 · 55 分钟 |
| 9 | [SVD](/linear-algebra/svd) | 如何用低秩近似压缩矩阵？ | 深度正文 · 55 分钟 |
| 10 | [低秩图像压缩](/linear-algebra/low-rank-image-compression) | 保留多少模式才能以可测误差压缩图像？ | 深度正文 · 70 分钟 |
| 11 | [Jacobian、Hessian 与自动微分](/linear-algebra/jacobian-hessian-autodiff) | 梯度如何成为可计算的线性代数？ | 深度正文 · 65 分钟 |

## 版本资源

- [v0.2 重写清单](/linear-algebra/rewrite-plan)：每篇的深化重点和发布节拍。
- [深度文章模板](/templates/deep-lesson)：后续专题写作的统一完成标准。
- [线性代数实验室](/projects/linear-algebra-lab)：可运行、可测试的教学实现。
