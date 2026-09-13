---
courseLevel: "2（推导与算法）"
prerequisites: "矩阵、消元、线性组合"
estimatedMinutes: 70
experiment: "重放四个基本子空间的基、维数恒等式与正交补关系"
title: 矩阵的四个基本子空间：秩、约束与可表示性
description: 用列空间、零空间、行空间和左零空间统一解释方程可解性、最小二乘与数据冗余。
---

# 矩阵的四个基本子空间：秩、约束与可表示性

## 文章元信息

- **建议阅读层级**：1–2 · 结构模型、消元与可解性
- **前置知识**：[线性组合、基与维度](/linear-algebra/linear-combinations-basis)、[高斯消元](/linear-algebra/gaussian-elimination)
- **预计学习时间**：70 分钟
- **配套实验**：[线性代数实验室](/projects/linear-algebra-lab)

## 学习目标

- 识别矩阵的列空间、零空间、行空间和左零空间；
- 用秩—零度定理判断可解性与信息丢失；
- 将子空间正交关系连接到消元、最小二乘与 SVD；
- 用 RREF 产出并审计四个子空间的基、维数与正交补关系。

## 从一个计算问题开始

同一个矩阵 $A$ 同时出现在三个问题里：哪些输出 $b$ 能写成 $Ax$？不同输入何时得到相同输出？为什么最小二乘的残差必须与某些方向正交？四个基本子空间给出一张统一地图。

## 直觉与严格定义

令 $A\in\mathbb R^{m\times n}$。它把输入空间 $\mathbb R^n$ 映到输出空间 $\mathbb R^m$：

| 子空间 | 所在空间 | 定义 | 程序问题 |
| --- | --- | --- | --- |
| 列空间 $C(A)$ | $\mathbb R^m$ | 所有 $Ax$ | 哪些 $b$ 可精确到达？ |
| 零空间 $N(A)$ | $\mathbb R^n$ | 所有 $Ax=0$ | 哪些输入信息被丢失？ |
| 行空间 $C(A^T)$ | $\mathbb R^n$ | $A$ 的行张成空间 | 哪些输入方向被测量？ |
| 左零空间 $N(A^T)$ | $\mathbb R^m$ | 所有 $A^Ty=0$ | 哪些输出约束必须成立？ |

若 $r=\mathrm{rank}(A)$，秩—零度定理给出

$$\dim N(A)=n-r,\qquad \dim N(A^T)=m-r.$$

并且 $C(A)$ 与 $N(A^T)$ 正交互补，$C(A^T)$ 与 $N(A)$ 正交互补。

## 手算一个完整例子

令 $A=\begin{bmatrix}1&1\\2&2\end{bmatrix}$。两列相同方向，因此 $r=1$。列空间是 $\mathrm{span}((1,2)^T)$：只有满足 $b_2=2b_1$ 的输出可精确解出。零空间由 $(1,-1)^T$ 张成，因为两种输入变化会相互抵消。左零空间由 $(2,-1)^T$ 张成，它正好表达输出约束 $2b_1-b_2=0$。

这也解释了为何 $Ax=b$ 对某些 $b$ 无解、对另一些 $b$ 有无穷多解：前者不在列空间，后者来自非零零空间。

## 算法实现：从同一 RREF 读出四个空间

消元将 $A$ 化为简化行阶梯形（RREF），主元数就是秩；**原矩阵**的主元列形成列空间的一组基，RREF 的非零行形成行空间的一组基。对每个自由变量设为 1、其余自由变量设为 0，可从 RREF 构造零空间基；同样对 $A^T$ 做一次 RREF，便得到左零空间基。

```python
from projects.linear_algebra_lab.basis import (
    fundamental_subspaces_certificate,
    fundamental_subspaces_report,
)

A = [[1.0, 1.0], [2.0, 2.0]]
report = fundamental_subspaces_report(A)

assert report["pivot_columns"] == [0]
assert report["column_space_basis"] == [[1.0, 2.0]]
assert report["null_space_basis"] == [[-1.0, 1.0]]
assert report["left_null_space_basis"] == [[-2.0, 1.0]]
assert report["dimensions"]["rank"] == 1
assert all(report["certificate"].values())
assert fundamental_subspaces_certificate(A, report)
```

对这个例子，零空间向量 $(-1,1)^T$ 与行空间基 $(1,1)$ 点积为零；左零空间向量 $(-2,1)^T$ 与列空间基 $(1,2)^T$ 点积也为零。报告还会显示

$$\mathrm{rank}(A)+\dim N(A)=n,\qquad
\mathrm{rank}(A)+\dim N(A^T)=m.$$

这让“两个秩—零度式”和“两个正交补”不再是四条孤立记忆。`fundamental_subspaces_certificate` 会独立重做 $A$ 与 $A^T$ 的 RREF、自由变量基和所有检查；篡改某个维数、主元列或任一基向量都会失败。对 $m\times n$ 密集矩阵，两次消元的时间为 $O(\min(m,n)^2\max(m,n))$，RREF、基与报告使用 $O(mn)$ 级存储。

## 正确性与工程边界

行变换不改变行空间维度和线性方程的可解性，阶梯形的非零行数因此等于秩。$A^Ty=0$ 等价于 $y$ 与每一列正交，故左零空间确为列空间的正交补；同理 $Ax=0$ 等价于 $x$ 与每一行正交，故零空间是行空间的正交补。报告逐对点积检查这些有限基向量，再由它们的维数和秩—零度式核对“补空间没有遗漏维度”。

这份有限 RREF 实验只证明其声明的容差下的计算结果。测量噪声使“零”变为“小奇异值”，严格秩可能不再反映可用信息量；应报告容差、尺度和有效秩，并在生产数值代码中采用带主元 QR 或 SVD。

## 常见误区

- 列空间属于输出空间，零空间属于输入空间；二者维度通常不同。
- 行变换可用于找秩，但列空间的基应从原矩阵的主元列选取。
- $Ax=b$ 无解不表示算法失败，而是 $b$ 不在列空间；[最小二乘](/linear-algebra/least-squares)会投影到最近可达输出。

## 练习

1. **基础**：求 $\begin{bmatrix}1&2\\3&6\end{bmatrix}$ 的秩与一个零空间基。
2. **推导**：证明 $y\in N(A^T)$ 当且仅当 $y$ 与 $C(A)$ 中每个向量正交。
3. **编码**：运行 `fundamental_subspaces_report`，篡改维数或左零空间基，确认证书拒绝；再对一个 $3\times2$ 满列秩矩阵解释为什么零空间为空而左零空间仍非空。
4. **开放**：解释 SVD 中接近零的奇异值如何对应近似零空间和特征冗余。

## 练习答案提示

1. 第二行是第一行的三倍，故秩为 1；解齐次方程 $x_1+2x_2=0$，令一个自由变量参数化即可。
2. $A^Ty=0$ 意味着每个分量都是 $y$ 与一列 $A$ 的点积，故 $y$ 与列空间每个线性组合都正交；反向逐列代入。
3. 满列秩 $3\times2$ 矩阵有 $n-r=0$ 个输入零空间维度，但有 $m-r=1$ 个左零约束；篡改后应让证书从原矩阵重新构造 RREF 与基，而不是只检查标签。
4. 小奇异值对应几乎不改变输出的输入方向；截断它们会丢失噪声敏感方向，但阈值需要与数据尺度、噪声和任务误差一起报告。

## 延伸与下一步

列空间上的投影就是[最小二乘](/linear-algebra/least-squares)的几何核心；下一阶段的 QR 分解会提供比正规方程更稳定的投影计算方式。
