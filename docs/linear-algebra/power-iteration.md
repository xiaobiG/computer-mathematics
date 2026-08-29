---
title: 幂迭代：为何反复乘矩阵会找到主特征方向
description: 从特征向量展开推导幂迭代的收敛比率，以 Rayleigh 商和残差验证结果，并解释重根、初值与非对称矩阵边界。
courseLevel: 2
prerequisites: 矩阵乘法、特征值与特征向量、向量范数
estimatedMinutes: 55
experiment: projects/linear_algebra_lab/power_iteration.py
---

# 幂迭代：为何反复乘矩阵会找到主特征方向

## 学习目标

读完后，你能从特征向量展开解释幂迭代为何偏向主特征方向；实现归一化、Rayleigh 商与残差检查；并判断何时谱隙、初值或矩阵性质会让它失效。

## 从一个计算问题开始

PCA、图排序和低秩压缩常不需要完整特征分解，只需要最显著方向。对大而稀疏的矩阵，直接求所有特征值很昂贵；如果只需主方向，反复计算矩阵—向量乘法通常更合适。关键问题是：反复乘 $A$ 为什么不会把方向搅乱，反而会聚焦？

## 定义与算法

对实对称矩阵 $A$，令单位特征向量为 $v_1,\ldots,v_n$，并按绝对特征值排序：

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

从含有主方向成分的初值 $x^{(0)}=\sum_i c_i v_i$（$c_1\ne0$）开始，幂迭代为

$$y^{(k+1)}=Ax^{(k)},\qquad x^{(k+1)}=\frac{y^{(k+1)}}{\lVert y^{(k+1)}\rVert_2}.$$

归一化不是装饰：它防止 $|\lambda_1|^k$ 让数值上溢或下溢，并只保留我们关心的方向。

## 从特征展开推导收敛

未归一化时，

$$A^kx^{(0)}=\sum_i c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i>1}c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

当 $|\lambda_i/\lambda_1|<1$ 时，括号中的非主方向按几何速度衰减。故方向误差的典型比率约为 $|\lambda_2/\lambda_1|$，它称为谱隙的实际含义：比率越小，收敛越快。若 $c_1=0$，初值恰好与主方向正交，算法永远看不见 $v_1$。

方向接近后，用 Rayleigh 商估计特征值：

$$\hat\lambda=\frac{x^\mathsf{T}Ax}{x^\mathsf{T}x}.$$

单位向量时分母为一。真正的可检验证据是残差 $r=Ax-\hat\lambda x$；$\lVert r\rVert_2$ 小表示“这个向量几乎满足特征方程”。

## 手算两轮

令 $A=\begin{bmatrix}5&0\\0&2\end{bmatrix}$，$x^{(0)}=(1,1)/\sqrt2$。一次乘法得到 $(5,2)/\sqrt2$，归一化后第一坐标占比上升；再乘一次会使坐标比例从 $5:2$ 变为 $25:4$。因为每轮相对比例额外乘 $5/2$，方向逐渐贴近 $(1,0)$，对应特征值 5。

## 可运行实验

```python
from projects.linear_algebra_lab.power_iteration import dominant_eigenpair

value, vector, trace = dominant_eigenpair([[2.0, 1.0], [1.0, 3.0]])
assert trace[-1]["residual_norm"] < 1e-10
print(value, vector)
```

运行 `python -m unittest projects.linear_algebra_lab.test_power_iteration`。实现要求实对称且有限的方阵，返回估计特征值、单位向量和每轮的 Rayleigh 商/残差。测试覆盖已知二维特征对角矩阵、残差收敛、非对称输入、零矩阵与迭代上限失败。

每轮稠密矩阵—向量乘法为 $O(n^2)$ 时间、$O(n)$ 额外空间；若 $A$ 稀疏则为 $O(\operatorname{nnz}(A))$。这正是它比完整稠密分解更适合“只求一个方向”的原因。

## 失败案例与工程边界

- **没有谱隙**：若 $|\lambda_1|=|\lambda_2|$，方向可能不唯一、缓慢震荡或依赖初值。
- **错误初值**：若 $c_1=0$，迭代会停在次主不变子空间；随机重启是实践中的常用补救。
- **负主特征值**：向量符号可以每轮翻转，方向仍收敛；不要把符号翻转误判为失败。
- **非对称矩阵**：可能有复特征值、非正交特征向量和暂态放大。本文实现故意拒绝它；应使用 Arnoldi 等适合的算法。
- **小残差不是绝对误差保证**：病态特征问题仍需结合谱隙与条件分析。

## 常见误区

- **“幂迭代得到最大数值特征值”**：它优先绝对值最大的特征值。
- **“归一化改变了目标”**：它只丢弃长度，不改变非零向量方向。
- **“向量变了很少就证明收敛”**：用残差验证更直接。
- **“PCA 总能直接在数据矩阵上幂迭代”**：要先中心化，并通常在协方差矩阵或等价的 $X^\mathsf{T}X$ 上工作。

## 练习

1. **基础**：对对角矩阵 $\operatorname{diag}(4,1)$ 从 $(1,1)$ 手算两轮并归一化。
2. **推导**：从特征展开推出误差项含 $(\lambda_2/\lambda_1)^k$。
3. **编码**：为轨迹增加相邻 Rayleigh 商之差，并构造一个无谱隙的矩阵观察行为。
4. **开放**：在中心化数据的协方差矩阵上运行幂迭代，与[PCA](/linear-algebra/eigenvalues-pca)的第一主成分比较；说明高维稀疏数据为何应避免显式形成协方差矩阵。

## 下一步

[特征值与 PCA](/linear-algebra/eigenvalues-pca)将主方向解释为最大方差方向；[SVD](/linear-algebra/svd)把它扩展到长方形矩阵；[低秩图像压缩](/linear-algebra/low-rank-image-compression)展示主方向如何变成压缩组件。
