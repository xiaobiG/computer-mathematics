---
courseLevel: "1–2（核心概念与推导）"
prerequisites: "随机变量、求和与基础代数"
estimatedMinutes: 55
experiment: "模拟样本均值与方差的收敛"
title: 期望、方差与不确定性：平均值遗漏了什么
description: 从随机变量的加权平均推导方差、全期望和全方差，并连接采样与模型风险。
---

# 期望、方差与不确定性：平均值遗漏了什么

## 文章元信息

- **建议阅读层级**：1–2 · 随机变量、推导与估计误差
- **前置知识**：概率质量函数、求和、[条件概率](/probability-ml/bayes)
- **预计学习时间**：60 分钟
- **配套实验**：[朴素贝叶斯垃圾邮件分类器](/projects/naive-bayes-spam)

## 学习目标

- 用期望与方差描述随机变量的中心和波动；
- 推导全期望、全方差并解释“组间/组内”不确定性；
- 区分总体方差、样本方差与模型输出的不确定性。

## 从一个计算问题开始

两个服务的平均响应时间都为 100 ms。服务 A 每次都在 100 ms 左右，服务 B 一半为 1 ms、一半为 199 ms。只看平均值会将它们误判为同样稳定；用户体验、容量规划和超时策略却完全不同。

## 定义与直觉

离散随机变量 $X$ 的期望是加权平均：

$$E[X]=\sum_x xP(X=x).$$

公平骰子的期望为 3.5，不是可能出现的结果，而是大量重复下的长期平均。方差衡量围绕均值的平方偏离：

$$\operatorname{Var}(X)=E[(X-\mu)^2]=E[X^2]-\mu^2,\qquad\mu=E[X].$$

平方避免正负偏离抵消，并使远离均值的风险贡献更大；标准差 $\sigma=\sqrt{\operatorname{Var}(X)}$ 保留原单位。

## 分步推导：从条件到总体

若类别 $Y$ 将样本分组，先对每组求均值再按组概率加权：

$$E[X]=E[E[X\mid Y]].$$

将 $X-E[X]$ 拆成 $(X-E[X\mid Y])+(E[X\mid Y]-E[X])$，交叉项条件期望为零，得到全方差公式：

$$\operatorname{Var}(X)=E[\operatorname{Var}(X\mid Y)]+\operatorname{Var}(E[X\mid Y]).$$

第一项是组内波动，第二项是组均值差异。它解释了为什么合并数据时，总方差不仅是各组方差的平均。

## 算法实现与复杂度

```python
from projects.naive_bayes_spam.moments import (
    finite_expectation,
    finite_variance,
    total_variance_report,
    welford_population,
)

distribution = {1.0: 1 / 3, 3.0: 1 / 3, 5.0: 1 / 3}
assert finite_expectation(distribution) == 3.0
assert finite_variance(distribution) == 8 / 3
assert welford_population([1.0, 3.0, 5.0])[1] == 8 / 3

report = total_variance_report(
    {"low": 0.25, "high": 0.75},
    {"low": {0.0: 0.5, 2.0: 0.5}, "high": {8.0: 0.5, 10.0: 0.5}},
)
assert report["total_variance"] == report["within_variance"] + report["between_variance"]
```

运行 `python -m unittest projects.naive_bayes_spam.test_moments`。有限分布模块检查概率质量后计算 $E[X]$ 与 $\operatorname{Var}(X)$；`welford_population` 逐项维护均值和平方偏差和；`total_variance_report` 分别给出组内项、组间项和总量，形成全方差公式的可运行证书。两遍实现与 Welford 均为 $O(n)$ 时间和 $O(1)$ 额外空间；对巨大或流式数据，后者避免累计平方与均值相减造成的消去误差。

## 正确性与工程边界

代码直接实现总体方差定义。若目标是从样本估计未知总体方差，常使用分母 $n-1$ 的无偏样本方差；不能将两者混用。重尾分布中均值/方差可能对少数极端值不稳，分位数、截尾均值或稳健损失更合适。方差描述分布宽度，不等于置信区间或预测校准。

## 常见误区

- 期望不是最可能值，也不是单次必然结果。
- 方差单位是原单位的平方；解释时常使用标准差。
- “模型方差高”与数据集的数值方差不是同一概念，需说明随机来源。

## 练习

1. **基础**：构造两组均值相同、方差不同的三元数据。
2. **推导**：从定义证明 $\operatorname{Var}(X)=E[X^2]-E[X]^2$。
3. **编码**：实现 Welford 在线方差，并与两遍算法比较。
4. **开放**：将垃圾邮件分类器按不同来源分组，设计检查组内/组间错误率差异的方案。

## 练习答案提示

1. 例如 $(1,3,5)$ 与 $(2,3,4)$ 的均值都为 3，但前者离均差平方更大；明确使用总体还是样本方差。
2. 展开 $(X-E[X])^2$，用线性性把 $E[X]$ 当常数；两项交叉项合并后剩下 $E[X^2]-E[X]^2$。
3. 逐项维护样本数、均值和 $M2$；用不同尺度、流式顺序和常量输入与两遍结果核对，避免只测普通小整数。
4. 先选定错误率/损失并按来源分层，同时报告每组样本量、组内波动和组间均值差；不要把观察差异直接解释为模型或用户的因果差异。

## 延伸与下一步

[协方差与相关性](/probability-ml/covariance-correlation)将把单变量波动扩展到特征共同变化；[最大似然](/probability-ml/maximum-likelihood)讨论如何从有限观测估计这些分布参数。
