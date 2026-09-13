---
courseLevel: "2–3（推导与应用）"
prerequisites: "矩阵乘法、协方差与投影"
estimatedMinutes: 90
experiment: "推导 Rayleigh 商、协方差谱与 SVD 等价，并实现中心化、协方差与二维 PCA"
title: 特征值与 PCA：寻找数据变化最大的方向
description: 从特征方向、中心化和协方差推导主成分分析。
---

# 特征值与 PCA：寻找数据变化最大的方向

## 学习目标

- 解释 $Av=\lambda v$ 的几何含义；
- 从中心化、协方差、Rayleigh 商和拉格朗日条件推导 PCA；
- 将 PCA 与中心化 SVD 联系起来，并完成投影与重构；
- 区分方差最大与业务价值最大。

## 从一个计算问题开始

若二维传感器数据大多沿一条斜线变化，保留两个坐标是否浪费存储？PCA 要找一条方向，使投影后保留的数据变化尽可能大、正交重构误差尽可能小。

## 定义：先说明 PCA 优化的对象

非零向量满足 $Av=\lambda v$ 时，$v$ 是特征向量：线性变换只伸缩、不转向它。对中心化数据矩阵 $X$，协方差矩阵

$$C=\frac{1}{m-1}X^TX$$

沿单位方向 $w$ 的投影方差为 $w^TCw$。在 $\lVert w\rVert=1$ 下最大化它，得到最大特征值对应的特征向量；前 $k$ 个正交方向就是主成分。

协方差矩阵对称半正定：

$$
C^T=C,\qquad
w^TCw=\frac{1}{m-1}w^TX^TXw=\frac{\lVert Xw\rVert_2^2}{m-1}\ge0.
$$

故特征值非负且可取正交特征向量；对 $z=Xw$，$w^TCw$ 恰是投影样本方差：

$$
\frac{1}{m-1}\sum_{i=1}^m z_i^2
=\frac{\lVert Xw\rVert_2^2}{m-1}
=w^TCw.
$$

PCA 最大化样本方差，不是坐标数值的表面变化。

## 分步推导：Rayleigh 商为何选出主特征向量

单位长度约束不能省略；否则把 $w$ 放大十倍就会把 $w^TCw$ 放大一百倍。写拉格朗日函数

$$
\mathcal L(w,\lambda)=w^TCw-\lambda(w^Tw-1).
$$

因为 $C=C^T$，对 $w$ 求导得到

$$
\nabla_w\mathcal L=2Cw-2\lambda w=0
\quad\Longrightarrow\quad Cw=\lambda w.
$$

在这样的驻点，左乘 $w^T$ 且用 $w^Tw=1$，有 $w^TCw=\lambda$。再把任意单位向量在正交特征基中展开为 $w=\sum_i\alpha_i v_i$、$\sum_i\alpha_i^2=1$，便得到 Rayleigh 商

$$
w^TCw=\sum_i\alpha_i^2\lambda_i\le\lambda_1.
$$

等号只在 $w$ 落在最大特征值的特征子空间时成立。这不仅给出“一维方向为何是第一特征向量”，也解释了并列最大特征值时方向不唯一：任何该并列子空间中的单位组合都同样最优。

对 $k$ 个相互正交的方向组成 $W=[w_1,\ldots,w_k]$，约束为 $W^TW=I$。保留方差是

$$
\mathrm{tr}(W^TCW),
$$

其最大值为前 $k$ 个特征值之和；最优的不是“逐一贪心选几个看起来大的坐标”，而是整个由前 $k$ 个特征向量张成的子空间。

## 手算与算法步骤

对每列减均值，再算 $C$；二维 $C$ 的最大特征向量给出一维投影方向。将中心化点投影为 $z=Xw$，重构为 $zw^T$ 并加回均值。保留方差比例为 $\sum_{i\le k}\lambda_i/\sum_i\lambda_i$。

伪代码将这个过程拆成可以逐项审计的步骤：

```text
mu <- 每一列的均值
X <- rows - mu
C <- X^T X / (m - 1)
w, lambda <- C 的最大特征对
score_i <- X_i · w
reconstruction_i <- mu + score_i w
```

## 完整二维例子：方差、重构与舍弃量是同一笔账

设某个中心化二维数据集的样本协方差为

$$
C=\begin{bmatrix}2&1\\1&2\end{bmatrix}.
$$

直接代入可得两个正交单位特征向量与特征值：

$$
v_1=\frac1{\sqrt2}(1,1)^T,\ \lambda_1=3;
\qquad
v_2=\frac1{\sqrt2}(1,-1)^T,\ \lambda_2=1.
$$

选择 $v_1$ 时，解释方差比例为 $3/(3+1)=0.75$。对任意中心化行向量 $x$，一维重构为 $(xv_1)v_1^T$，残差为

$$
r=x-(xv_1)v_1^T.
$$

由于 $r^Tv_1=0$，投影和残差是直角分解。把所有样本相加，平方重构误差为

$$
\sum_i\lVert r_i\rVert_2^2=(m-1)(\mathrm{tr}(C)-\lambda_1)=(m-1)\cdot1.
$$

这里的“未解释 25% 方差”不是独立的可视化说法；它正是最优一维投影仍必须舍弃的残差能量。若选择 $v_2$，则只能保留 25% 方差，重构误差相应更大。

## 可运行实验：从协方差到重构证书

```python
from projects.linear_algebra_lab.pca import pca_2d_report, pca_2d_report_certificate

report = pca_2d_report([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
assert report.mean == (1.0, 1.0)
assert report.explained_variance_ratio == 1.0
assert report.reconstruction_error_squared < 1e-18
assert report.certificate["valid"]
assert pca_2d_report_certificate([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]], report)
```

二维实验以幂迭代检查中心化、单位方向、残差正交及“重构误差 = 舍弃方差 $\times(m-1)$”，将最大方差与最小重构误差绑定。

报告字段本身不足为证。重放器从二维行重算均值、协方差、方向、投影与误差；篡改数值或标记会失败。它不验证高维统计代表性或业务价值。

这个教学接口明确只接收至少两行的 `list[list[有限实数]]`：行不是二维、传入一次性迭代器、布尔值、`NaN` 或无穷都会拒绝。这样“重放同一数据”的合同不依赖迭代器是否已被消费；在生产环境中若要支持数组、流式批次或缺失值，应另行定义数据所有权、缺失策略与数值缩放规则。

## 同一数据的反例：不中心化会追随偏移量

对 `[[100,-1],[100,0],[100,1]]`，中心化后的变化只沿 $y$ 轴；原始二阶矩却被 $x=100$ 的均值偏移主导：

```python
from projects.linear_algebra_lab.pca import (
    pca_2d_centering_comparison_certificate,
    pca_2d_centering_comparison_report,
)

rows = [[100.0, -1.0], [100.0, 0.0], [100.0, 1.0]]
report = pca_2d_centering_comparison_report(rows)
assert abs(report["centered_component"][1]) > .999
assert abs(report["uncentered_component"][0]) > .999
assert report["uncentered_is_more_aligned_to_mean"]
assert pca_2d_centering_comparison_certificate(rows, report)
```

证书重放两条路径；它说明原始 $X^TX/m$ 的方向可追均值，而非“未中心化算法错误”。

中心化为 $O(md)$，形成密集协方差为 $O(md^2)$；二维幂迭代每轮为常数成本。高维数据常直接使用截断 SVD，避免显式形成 $d\times d$ 协方差矩阵。

## 正确性与复杂度

对单位向量 $w$，中心化数据投影后的样本方差为 $w^TCw$。拉格朗日乘子条件 $Cw=\lambda w$ 说明极值只能出现在特征方向；最大特征值对应最大方差。对每个中心化行 $x_i$，重构残差为 $x_i-(x_i^Tw)w$，它与 $w$ 的点积为零。把所有残差平方和相加，可得

$$\sum_i\lVert x_i-(x_i^Tw)w\rVert^2=(m-1)(\mathrm{tr}(C)-\lambda_1).$$

这正是实验检查的“舍弃方差”恒等式。若协方差没有唯一的最大特征值，主方向不唯一，任何落在主子空间的单位方向都可能合理；不要把符号或并列方向差异误判为程序错误。

## PCA 与 SVD：不要把两个算法记成两套无关公式

对中心化矩阵作薄 SVD：

$$
X=U\Sigma V^T.
$$

代回协方差定义：

$$
C=\frac1{m-1}X^TX
=V\frac{\Sigma^2}{m-1}V^T.
$$

因此 PCA 的主方向是 $V$ 的列，解释方差是 $\sigma_i^2/(m-1)$，投影分数为

$$
XV=U\Sigma,
$$

而保留前 $k$ 个分量的中心化重构为 $X_k=U_k\Sigma_kV_k^T=XV_kV_k^T$。这给出两个工程结论：当样本数或特征数很大时，通常不必先显式构造协方差；而“PCA 截断误差”与[SVD](/linear-algebra/svd)中的谱尾平方和是同一个 Frobenius 几何事实。前提仍是先中心化；对原始矩阵做 SVD 可是有效分解，却不必然对应 PCA。

## 失败案例与工程边界

PCA 对尺度敏感：以“元”和“毫秒”一起输入会让量纲较大的变量主导，常需标准化。标准化也不是无害按钮：它等于改用相关矩阵，隐含“每个特征的一单位标准差同等重要”的建模选择。最大方差也可能是噪声或敏感属性，不能自动等同于“最有用”。PCA 只描述线性结构，弯月形等非线性数据会失败；有异常值时，均值和协方差本身也可能被少量极端样本拉偏。

## 常见误区

- 未中心化就做 PCA，第一方向可能只是在追均值。
- 主成分符号可翻转，$w$ 与 $-w$ 表示同一方向。
- PCA 是无监督压缩，不保证对预测任务最佳。
- “解释 95% 方差”不是保留 95% 业务信息；它只是在当前特征、尺度与样本上的二次能量比例。

## 练习

1. **基础**：对三组二维点中心化并写出协方差矩阵。
2. **推导**：展开 $\lVert x-(x^Tw)w\rVert^2$，证明单位 $w$ 时最小重构误差等价于最大化 $w^TCw$。
3. **编码**：为 `pca_2d_report` 加一组非共线点，检查残差正交与舍弃方差证书。
4. **开放**：比较标准化前后的第一主成分；说明何时“方差最大”可能主要是在保留噪声或敏感属性。

## 练习答案提示

1. 先求每个坐标的均值并逐点相减；协方差的对角线是各坐标方差，非对角线是共同变化，注意分母采用的样本约定。
2. 展开平方后用 $w^Tw=1$ 合并二次项，得到 $\lVert x\rVert^2-(x^Tw)^2$；第一项与方向无关，所以最小误差等价于最大投影能量。
3. 除了比较主方向，还应断言每个残差与方向点积接近零、残差平方和与舍弃方差一致；符号翻转的方向应视为等价。
4. 标准化前后分别报告单位与解释方差；大尺度特征、测量噪声和敏感代理变量都可能主导最大方差方向，而不等于任务信息。

## 下一步

[SVD](/linear-algebra/svd)会将 PCA 扩展到任意形状的数据矩阵，并给出最佳低秩近似。
