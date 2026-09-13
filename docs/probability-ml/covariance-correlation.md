---
courseLevel: "1–2（核心概念与推导）"
prerequisites: "期望、方差与散点图"
estimatedMinutes: 55
experiment: "计算协方差矩阵、主方向，并构造零协方差但强相关的反例"
title: 协方差、相关性与特征
description: 从共同变化到协方差矩阵，理解线性相关、PCA 与因果推断之间的边界。
---

# 协方差、相关性与特征

> 这一课回答三个常被混为一谈的问题：两个量会不会一起变化？它们的线性关系有多强？能否据此断言一个造成了另一个？答案分别由协方差、相关系数和因果推断给出。

## 学习目标

完成本课后，你应该能够：

- 从定义推导 $\mathrm{Cov}(X,Y)=\mathbb E[XY]-\mathbb E[X]\mathbb E[Y]$；
- 正确解释样本协方差、相关系数与协方差矩阵；
- 用“零协方差但不独立”的反例划清线性关系与一般依赖；
- 说明 PCA 为什么从中心化数据的协方差矩阵出发；
- 在数据分析中明确“相关不等于因果”究竟缺少了什么证据。

## 从一个数据分析误判开始

某团队收集到用户每天使用学习 App 的时长 $X$ 与测验得分 $Y$。散点图呈上升趋势，于是报告写道：“使用 App 会提高分数。”

这里至少跳过了两层推理：

1. 上升趋势是否稳定、是否近似线性？这由协方差和相关系数描述。
2. 即使趋势稳定，是否是 App 导致了分数？也许自律程度 $Z$ 同时让学生更愿意学习、也更愿意打开 App。$Z$ 是混杂变量。

因此，协方差不是“因果强度”。它首先是一个描述**共同线性变化方向**的量。

## 协方差：把偏离均值的方向相乘

对随机变量 $X,Y$，定义

$$
\mathrm{Cov}(X,Y)=\mathbb E[(X-\mu_X)(Y-\mu_Y)],
\qquad \mu_X=\mathbb E[X],\;\mu_Y=\mathbb E[Y].
$$

每次观测都先减去自己的平均值：

- 两者常常同在平均值上方或同在下方，乘积多为正，协方差为正；
- 一个偏高时另一个常偏低，乘积多为负，协方差为负；
- 正负抵消时，协方差接近零。

展开括号即可得到最常用的计算式：

$$
\begin{aligned}
\mathbb E[(X-\mu_X)(Y-\mu_Y)]
&=\mathbb E[XY]-\mu_X\mathbb E[Y]-\mu_Y\mathbb E[X]+\mu_X\mu_Y\\
&=\mathbb E[XY]-\mathbb E[X]\mathbb E[Y].
\end{aligned}
$$

当 $X=Y$ 时协方差就是方差。协方差带两个变量量纲，不能跨“小时×分数”与“厘米×千克”直接比较。

### 样本版本与 $n-1$

有 $n$ 个样本 $(x_i,y_i)$ 时，常见的样本协方差是

$$
s_{xy}=\frac1{n-1}\sum_{i=1}^n(x_i-\bar x)(y_i-\bar y).
$$

描述此样本可用 $n$；在独立同分布假设下估计总体常用 $n-1$。关键是声明并保持分母约定。

## 相关系数：消除单位后的线性刻度

皮尔逊相关系数定义为

$$
\rho_{XY}=\frac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y},
\qquad
r=\frac{s_{xy}}{s_xs_y}.
$$

它把协方差除以两个标准差，因而没有单位，且由柯西—施瓦茨不等式保证 $-1\le r\le1$。

- $r=1$：样本点严格落在一条正斜率直线上；
- $r=-1$：严格落在一条负斜率直线上；
- $r\approx0$：没有明显的**线性**关系，不能推出“没有关系”。

相关系数对平移和正缩放不变，负缩放翻转符号；强弯曲关系仍可能零相关。

## 一个必须会用的反例：零协方差不等于独立

令 $X$ 在 $[-1,1]$ 上均匀分布，$Y=X^2$。显然 $Y$ 完全由 $X$ 决定，二者绝不独立。但对称性给出 $\mathbb E[X]=0$、$\mathbb E[X^3]=0$，所以

$$
\mathrm{Cov}(X,Y)=\mathbb E[X^3]-\mathbb E[X]\mathbb E[X^2]=0.
$$

散点图是一条抛物线：左半边下降、右半边上升，线性趋势正好相互抵消。结论是：

$$
X\perp Y \Longrightarrow \mathrm{Cov}(X,Y)=0,
\quad\text{但反向一般不成立。}
$$

只有在一些特殊分布族（例如联合高斯）中，零协方差才足以推出独立。不要把这个额外条件悄悄省掉。

## 协方差矩阵：多个特征的一张结构图

将 $d$ 维特征写为随机向量 $\mathbf X$，其协方差矩阵是

$$
\Sigma=\mathbb E[(\mathbf X-\boldsymbol\mu)(\mathbf X-\boldsymbol\mu)^\mathsf T].
$$

第 $i,j$ 个元素是第 $i$ 与第 $j$ 个特征的协方差；对角线是各特征的方差。它有两个极重要的性质：

1. **对称**：$\Sigma=\Sigma^\mathsf T$。
2. **半正定**：对任意向量 $\mathbf v$，

$$
\mathbf v^\mathsf T\Sigma\mathbf v
=\mathrm{Var}(\mathbf v^\mathsf T\mathbf X)\ge0.
$$

第二式表示：沿任意方向投影后，方差绝不会是负数。它保证了协方差矩阵的特征值非负，也为 PCA 选择主方向提供了数学基础。

## 为什么 PCA 要看协方差矩阵

将每行是一个样本的中心化数据矩阵记为 $Z\in\mathbb R^{n\times d}$。其样本协方差矩阵为

$$
S=\frac1{n-1}Z^\mathsf T Z.
$$

把样本投影到单位向量 $\mathbf v$ 上，投影后的样本方差正是

$$
\mathrm{Var}(Z\mathbf v)=\mathbf v^\mathsf T S\mathbf v.
$$

所以 PCA 的第一主成分是在 $\|\mathbf v\|=1$ 约束下最大化这个二次型。拉格朗日乘子条件给出 $S\mathbf v=\lambda\mathbf v$：最大特征值对应的特征向量，就是方差最大的方向。

这也带来实践上的警告：若“收入”以元计、“年龄”以年计，方差大的量会支配 PCA。此时通常先标准化为零均值、单位方差，再对相关矩阵做 PCA；是否标准化应由业务量纲决定，不能机械套用。

## 用代码把定义变成可检查的计算

实验显式检查中心化、分母和零方差：

```python
from projects.naive_bayes_spam.covariance import (
    covariance_report, covariance_report_certificate,
    sample_correlation, sample_covariance,
)

report = covariance_report([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]])
assert report["covariance"] == [[1.0, 2.0], [2.0, 4.0]]
assert report["certificate"]["valid"]
assert covariance_report_certificate([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]], report)["valid"]

xs = [-2.0, -1.0, 0.0, 1.0, 2.0]
ys = [value * value for value in xs]
assert sample_covariance(xs, ys) == 0.0
assert sample_correlation(xs, ys) == 0.0
```

`covariance_report` 检查中心化列和、对称性与对角方差；证书从原样本重算。二次样本的零协方差/相关仍不等于独立。

## 相关不是因果：随机分配改变了什么

观察相关还兼容反向关系、共同原因 $Z\to X,Z\to Y$ 与筛选偏差。若单位 $i$ 的控制/处理潜在结果是 $Y_i(0),Y_i(1)$，目标有限总体效应为

$$\tau=\frac1N\sum_i\bigl(Y_i(1)-Y_i(0)\bigr).$$

完全随机地从固定人数的全部处理集合中等概率抽取时，处理减对照均值的**分配期望**等于 $\tau$；一次抽签的均值差不必等于它。实验精确枚举小表，而不是以一次模拟代替该恒等式：

```python
from projects.naive_bayes_spam.randomized_experiment import complete_randomization_report

outcomes = [(0.0, 1.0), (0.0, 2.0), (1.0, 1.0), (1.0, 3.0)]
report = complete_randomization_report(outcomes, treated_count=2)
assert report["expected_difference_in_means"] == 1.25
assert report["finite_population_average_treatment_effect"] == 1.25
```

## 无干扰为何也是随机化恒等式的前提

若结果为 $Y_i(z_i,z_j)=2z_i+3z_j$，直接效应为 2；固定一人处理时均值差却为 $-1$：

```python
from projects.naive_bayes_spam.randomized_experiment import (
    two_unit_interference_certificate,
    two_unit_interference_report,
)

outcomes = [(0.0, 3.0, 2.0, 5.0), (0.0, 3.0, 2.0, 5.0)]  # 00, 01, 10, 11
report = two_unit_interference_report(outcomes)
assert report["average_direct_effect_when_peer_control"] == 2.0
assert report["expected_treated_minus_control"] == -1.0
assert not report["no_interference_condition_holds"]
assert two_unit_interference_certificate(outcomes, report)
```

这不是干扰估计器；随机化不能单独保证均值差是直接效应。

## 不依从：随机化的 ITT 不是“人人实际接受”的效应

令 $Z$ 为分配、$D(z)$ 为实际接受、$Y(d)$ 为结果。每行是 $(D(0),D(1),Y(0),Y(1))$，并声明无干扰、排除性和单调性 $D(1)\ge D(0)$；随机化均值差的期望是 ITT：

$$
\operatorname{ITT}=\frac1n\sum_i\left[Y_i(D_i(1))-Y_i(D_i(0))\right].
$$

```python
from projects.naive_bayes_spam.randomized_experiment import monotone_noncompliance_randomization_report

table = [(0, 0, 0, 4), (0, 1, 0, 2), (0, 1, 1, 4), (1, 1, 0, 10)]
report = monotone_noncompliance_randomization_report(table, treated_count=2)
assert report["all_units_received_treatment_effect"] == 4.75
assert report["intention_to_treat_effect"] == 1.25
assert report["complier_average_received_treatment_effect"] == report["wald_ratio"] == 2.5
```

4.75 是全体接受效应，1.25 是 ITT，2.5 是依从者效应。仅在已声明的排除性、单调性与非零接受差下，$\operatorname{ITT}/E[D(1)-D(0)]$ 等于后者；报告不验证这些假设，也不处理失访、时间/层级或自动决策。

## 常见误区

- **把大协方差当成强关系。** 协方差受单位影响；跨变量比较应先考虑相关系数或标准化。
- **把相关系数当作万能依赖检测器。** 它只能测量线性趋势；画散点图、检查分组与非线性。
- **先算相关再解释因果。** 相关的方向、混杂与选择偏差都未被解决。
- **未中心化就解释 $X^\mathsf TY$。** 原始内积混入了均值；协方差/PCA 的核心步骤是中心化。
- **忽略离群点。** 少数极端点可显著扭转皮尔逊相关；要同时报告图形、稳健统计或敏感性分析。

## 练习

1. **基础**：展开 $\mathbb E[(X-\mu_X)(Y-\mu_Y)]$，推出协方差计算式。
2. **推导**：证明协方差矩阵对称，并推导 $\mathbf v^\mathsf T\Sigma\mathbf v=\mathrm{Var}(\mathbf v^\mathsf T\mathbf X)$。
3. **编码**：为 `covariance_report` 加三维样本、篡改协方差，并测试常量列的相关拒绝。
4. **开放**：比较原始尺度与标准化后的 PCA 主方向，并写出量纲理由。
5. **开放**：新闻中出现“冰淇淋销量与溺水人数正相关”。画出一个含季节变量的因果图，说明为何该相关不能支持因果结论。

## 练习答案提示

1. 展开后用 $E[X]=\mu_X,E[Y]=\mu_Y$ 合并各项。
2. 交换 $i,j$；再展开线性组合方差。
3. 检查对称、非负对角和重放；常量列使相关分母无定义。
4. 先说明单位与标准化为何改变方向。
5. 画季节到两变量的共同原因箭头。

## 下一步

协方差矩阵将在线性代数专题的 [特征值、特征向量与 PCA](/linear-algebra/eigenvalues-pca) 中继续变成可计算的降维工具；若你希望把相关分析用于模型评估，下一步应学习置信区间、假设检验与校准，而不是急着作因果断言。
