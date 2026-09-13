---
title: 联合、边缘与条件分布：把相关变量拆开再连接
description: 从有限联合概率表推导边缘化、条件化与独立性，并用可测试代码审计概率质量。
courseLevel: "1–2（概率建模与推导）"
prerequisites: "集合、概率公理与条件概率"
estimatedMinutes: 55
experiment: "枚举有限联合表，并在同一分层计数表上对照边缘化与条件化结论"
---

# 联合、边缘与条件分布：把相关变量拆开再连接

## 学习目标

读完后，你能用联合分布表示两个随机变量；由求和得到边缘分布；由归一化得到条件分布；以乘积关系判断独立性；并能识别零概率条件、遗漏状态、总体与分层结论反转，以及“相关不等于因果”的边界。

## 从一个建模问题开始

只保存“下雨概率”和“带伞概率”，无法回答已知下雨时带伞的概率，也无法检查独立性；必须记录同时发生的概率。

令 $X\in\{\text{rain},\text{sun}\}$ 表示天气，$Y\in\{\text{umbrella},\text{none}\}$ 表示是否带伞。一个有限联合表为

| $P(X,Y)$ | umbrella | none |
| --- | ---: | ---: |
| rain | 0.18 | 0.02 |
| sun | 0.12 | 0.68 |

四格非负且和为 $1$，才是有效联合表。

## 定义与分步推导

**联合分布**给出 $P(X=x,Y=y)$。要忽略 $Y$ 的细节，就把所有兼容的 $y$ 加起来：

$$P(X=x)=\sum_yP(X=x,Y=y).$$

例如 $P(X=\text{rain})=0.20$；同理 $P(Y=\text{umbrella})=0.30$。

已知 $X=x$ 后，只在该行内重新归一化：

$$P(Y=y\mid X=x)=\frac{P(X=x,Y=y)}{P(X=x)},\qquad P(X=x)>0.$$

因此 $P(\text{umbrella}\mid\text{rain})=0.9$。分母为零时，本节的有限表不定义条件分布，程序必须拒绝。

若每一格都满足

$$P(X=x,Y=y)=P(X=x)P(Y=y),$$

则 $X,Y$ 独立。这里 $0.18\ne0.20\times0.30$，故不独立；变量名称“看上去无关”不是判据。

## 算法实现：让概率质量可审计

```python
from projects.naive_bayes_spam.joint_distribution import (
    conditional_second_given_first,
    independence_residual,
    marginal_first,
)

table = {
    ("rain", "umbrella"): 0.18, ("rain", "none"): 0.02,
    ("sun", "umbrella"): 0.12, ("sun", "none"): 0.68,
}

assert marginal_first(table) == {"rain": 0.2, "sun": 0.8}
assert conditional_second_given_first(table, "rain") == {"umbrella": 0.9, "none": 0.1}
assert independence_residual(table) > 0.0
```

运行 `python -m unittest projects.naive_bayes_spam.test_joint_distribution`。实现检查概率质量，再单次扫描累计边缘量；对 $r$ 个非零状态，时间为 $O(r)$。

`independence_residual` 是最大 $|P(x,y)-P(x)P(y)|$：零证明此有限表独立，非零量化偏离。

## 同一份计数：边缘化可能和条件化说相反的话

边缘化会把第三个变量 $Z$ 求和掉：

$$P(Y\mid X)=\sum_z P(Y\mid X,Z=z)P(Z=z\mid X).$$

权重 $P(Z=z\mid X)$ 可随 $X$ 改变；故每层较高的成功率可汇总成总体较低。以下是同一份轻症/重症计数表。

```python
from projects.naive_bayes_spam.stratified_association import (
    stratified_association_certificate,
    stratified_association_report,
)

counts = {
    "mild": {"exposed_success": 81, "exposed_failure": 6,
             "unexposed_success": 234, "unexposed_failure": 36},
    "severe": {"exposed_success": 192, "exposed_failure": 71,
               "unexposed_success": 55, "unexposed_failure": 25},
}
report = stratified_association_report(counts)
assert report["strata"]["mild"]["direction"] == "exposed_higher"
assert report["strata"]["severe"]["direction"] == "exposed_higher"
assert report["pooled"]["direction"] == "exposed_lower"
assert report["reversal"]["detected"]
assert stratified_association_certificate(counts, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_stratified_association`。报告重算每层与总体成功率；证书拒绝改动方向或反转结论。$s$ 个分层的时间、空间均为 $O(s)$。

这只是描述性关联：分层是否充分、抽样机制与可比性均需独立证据，不能自动行动或推出因果。

## 正确性、边界与误区

边缘化不会丢失概率质量，因为对联合表的全部单元格恰好求和一次：$\sum_x\sum_yP(x,y)=1$。对正概率条件，条件表也归一：

$$\sum_yP(Y=y\mid X=x)=\frac{\sum_yP(X=x,Y=y)}{P(X=x)}=1.$$

- **零概率与遗漏状态**：本节不定义零概率条件；未列组合是零还是缺失，须写入数据契约。
- **样本与总体**：计数有抽样误差；总体和每层冲突时不能删去分层变量。
- **相关不是因果**：相关不排除共同原因或反向关系。

## 练习

1. **基础**：由表计算 $P(Y=\text{none})$ 与 $P(X=\text{sun}\mid Y=\text{umbrella})$。
2. **推导**：证明若联合表满足乘积关系，则对任意 $P(X=x)>0$ 有 $P(Y=y\mid X=x)=P(Y=y)$。
3. **编码**：从整数计数归一化联合表，并拒绝负计数、零总数与分层的零分母。
4. **开放**：设计垃圾邮件分层表；说明特征泄漏、数据相关和因果解释的区别。

## 练习答案提示

1. 跨行求和；反向条件化改用 $P(Y=\text{umbrella})$ 作分母。
2. 代入乘积关系并约去正的 $P(x)$；零概率行不在本节定义域。
3. 验证非负整数、正总数与每层正分母，再检查归一化。
4. 需要时间顺序、干预或混杂控制证据；条件比例本身不提供因果解释。

## 延伸

[条件概率与贝叶斯更新](/probability-ml/bayes)将联合—条件关系用于证据更新；[协方差与相关性](/probability-ml/covariance-correlation)把两个数值变量的共同变化进一步量化；[常见分布](/probability-ml/common-distributions)讨论如何在有限表之外选择生成模型。
