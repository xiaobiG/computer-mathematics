---
title: 行列式与可逆性：行变换如何测量体积缩放
description: 从排列的有向体积、行变换和消元推导行列式，连接可逆性、秩亏与特征值。
courseLevel: "1–2（线性变换与消元）"
prerequisites: "矩阵乘法、线性方程组与高斯消元"
estimatedMinutes: 60
experiment: "用精确有理数重放消元中的交换、主元与零行列式"
---

# 行列式与可逆性：行变换如何测量体积缩放

## 学习目标

- 将二维面积、三维体积缩放连接到方阵的行列式；
- 解释三种行变换对行列式的影响；
- 从消元推导三角矩阵行列式与可逆性判据；
- 区分“行列式为零”的代数结论与浮点数中的近奇异诊断。

## 从一个计算问题开始

线性变换把单位正方形映为平行四边形。若它把一个方向压到另一方向上，面积变成零；此时不同输入可得到同一输出，方程不可能对每个右端都有唯一解。行列式把这件几何事实压缩成一个带符号数。

## 定义：有向面积与体积缩放

对二维列向量组成的矩阵

$$A=\begin{bmatrix}a&b\\c&d\end{bmatrix},$$

定义

$$\det(A)=ad-bc.$$

其绝对值是单位正方形经 $A$ 变换后的面积；符号记录方向是否翻转。一般 $n\times n$ 方阵的行列式满足多线性、交换两行变号、相同行使其为零以及 $\det(I)=1$。这些性质唯一确定它，也比死记排列求和更适合解释算法。

## 推导：消元为何只需追踪交换和主元

三种初等行操作分别使行列式：交换两行乘 $-1$；一行乘常数乘同一常数；一行加另一行的倍数不变。高斯消元只使用交换和“加倍数”，因此将 $A$ 化到上三角 $U$ 后，若交换了 $s$ 次，

$$\det(A)=(-1)^s\prod_{i=1}^n U_{ii}.$$

三角矩阵的结论来自体积的逐轴缩放：第 $i$ 个对角元是尚未被前面轴消去的缩放量。若某列没有非零主元，消元得到零行，乘积为零；反过来所有主元非零就能回代。因此对方阵

$$\det(A)\ne0\Longleftrightarrow A\text{ 可逆}\Longleftrightarrow Ax=b\text{ 对每个 }b\text{ 有唯一解}.$$

这不是说“求逆是默认算法”：数值求解通常仍使用选主元的消元、QR 或 SVD。

## 可运行实验：精确轨迹而非浮点巧合

```python
from fractions import Fraction
from projects.linear_algebra_lab.determinant_trace import (
    classify_square_matrix,
    determinant_trace,
    determinant_trace_certificate,
    square_matrix_classification_certificate,
)

matrix = [[0, 2], [3, 4]]
determinant, events = determinant_trace(matrix)
assert determinant == Fraction(-6)
assert events[0].swapped
assert determinant_trace_certificate(matrix, determinant, events)

singular, singular_events = determinant_trace([[1, 2], [2, 4]])
assert singular == 0
assert singular_events[-1].pivot_row is None

report = classify_square_matrix([[1, 2], [2, 4]])
assert (report.rank, report.nullity, report.invertible) == (1, 1, False)
assert not report.unique_solution_for_every_rhs
assert square_matrix_classification_certificate([[1, 2], [2, 4]], report)
```

实验用 `Fraction` 保存消元，明确记录每列的主元行、是否交换和当前上三角形态。`classify_square_matrix` 不把 `determinant != 0` 当成孤立的布尔判断：它以同一份精确输入另行做“允许跳过零列”的秩消元，再给出秩、零空间维数、可逆性，以及“对每个 $b$ 都唯一可解”这个**全称**结论。这个区别很重要：$\begin{bmatrix}0&1\\0&0\end{bmatrix}$ 的第一列没有主元、行列式为零，但秩仍为 1；判定行列式为零可以停止，计算秩却不能把后列一并丢掉。对奇异矩阵，这不等于“每个 $b$ 都无解”：有些右端会有无穷多解，有些没有解；报告只拒绝“每个右端恰有一个解”的更强说法。两个证书都从原矩阵重放，篡改交换标志、主元轨迹或分类字段都会失败。它只接受最多 $6\times6$ 的整数教学矩阵，不是高性能行列式库；真实浮点问题应报告条件数和缩放，不能把一个接近零的浮点行列式当作精确的不可逆证明。

## 同一个零主元，四种等价语言

对 $n\times n$ 方阵，消元中每一列都有主元，等价于秩为 $n$；此时零空间只有零向量、行列式不为零，并且 $Ax=b$ 对每个 $b$ 都唯一可解。若行列式消元在对角位置缺主元，行列式立即为零；秩消元仍会检查后续列。它最终给出

$$\operatorname{rank}(A)<n,\qquad \operatorname{nullity}(A)=n-\operatorname{rank}(A)>0,\qquad \det(A)=0.$$

非零的零空间向量 $z$ 满足 $Az=0$。因此只要某个右端有解 $Ax=b$，那么 $x+tz$（任意实数 $t$）也是解；这正是唯一性失败的原因。另一方面，右端不在列空间时根本无解。行列式、秩、零空间和方程解的说法不是四条松散口诀，而是同一条消元证据在几何、线性空间和方程三个视角下的读法。

## 与特征值、秩和复杂度的连接

若 $Av=\lambda v$，则 $\det(A-\lambda I)=0$ 是特征值出现非零方向的条件。行列式为零等价于列向量线性相关，也等价于秩小于 $n$。密集消元求行列式约为 $O(n^3)$；展开余子式的 $O(n!)$ 公式适合小推导，不适合程序实现。

## 失败案例与工程边界

- **把行加倍数也当作变号。** 只有交换改变符号；行替换不改变行列式。
- **把小行列式当作唯一稳定性指标。** 单位缩放会改变其数值大小；条件数更适合衡量相对敏感性。
- **用余子式展开写生产代码。** 公式正确却指数爆炸；应使用分解。
- **把非方阵硬塞进行列式。** 标准行列式只定义于方阵；最小二乘和 SVD 回答的是不同问题。

## 常见误区

1. “行列式是矩阵所有元素的乘积。”错误：只有三角矩阵才是对角线乘积。
2. “行列式为零说明输入数据错误。”错误：它只说明线性变换压低维度，冗余特征常会造成这一情形。
3. “可逆就应显式求逆。”错误：解方程通常应直接分解并回代。
4. “负行列式代表负面积。”错误：面积取绝对值；负号表示定向翻转。

## 练习

1. **基础**：计算 $\det\begin{bmatrix}2&1\\3&4\end{bmatrix}$，解释符号。
2. **推导**：证明一行加另一行倍数不改变二维公式 $ad-bc$。
3. **编码**：篡改一次 `determinant_trace` 的交换字段，确认重放拒绝；再构造一个秩亏矩阵。
4. **推导**：若 $Az=0$ 且 $z\ne0$，证明任何一个已知解 $x$ 都不能是唯一解；说明这并不保证每个 $b$ 都有解。
5. **建模**：说明为何把长度从米换成厘米会改变行列式大小却不改变可逆性。

## 练习答案提示

1. 得到 $8-3=5$；正号表示未翻转定向。
2. 将一行替换后的两项展开，新增交叉项相消。
3. 使用成比例的两行，并检查证书不信任展示字段。
4. 比较 $A(x+tz)$ 与 $Ax$；只有先知道某个解存在，才能构造整条解直线。
5. 每个坐标轴缩放都会乘入行列式，零/非零状态不变。

## 下一步

[高斯消元](/linear-algebra/gaussian-elimination)给出稳定求解轨迹；[LU 分解与主元选择](/linear-algebra/lu-factorization-pivoting)将同一消元过程复用于多个右端；[特征值与 PCA](/linear-algebra/eigenvalues-pca)将 $\det(A-\lambda I)$ 连接到方向与谱。
