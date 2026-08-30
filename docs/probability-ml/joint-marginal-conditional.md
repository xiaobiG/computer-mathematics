---
title: 联合、边缘与条件分布：把相关变量拆开再连接
description: 从有限联合概率表推导边缘化、条件化与独立性，并用可测试代码审计概率质量。
courseLevel: "1–2（概率建模与推导）"
prerequisites: "集合、概率公理与条件概率"
estimatedMinutes: 55
experiment: "枚举有限联合表，验证边缘化、条件分布和独立性残差"
---

# 联合、边缘与条件分布：把相关变量拆开再连接

## 学习目标

读完后，你能用联合分布表示两个随机变量；由求和得到边缘分布；由归一化得到条件分布；以乘积关系判断独立性；并能识别零概率条件、遗漏状态和“相关不等于因果”的边界。

## 从一个建模问题开始

下雨和带伞显然有关。若程序只保存“下雨概率”和“带伞概率”，它无法回答“已经看到下雨时带伞的概率”，更无法检查两个事件是否独立。解决方法不是再加一条经验规则，而是先记录两个变量同时发生的概率。

令 $X\in\{\text{rain},\text{sun}\}$ 表示天气，$Y\in\{\text{umbrella},\text{none}\}$ 表示是否带伞。一个有限联合表为

| $P(X,Y)$ | umbrella | none |
| --- | ---: | ---: |
| rain | 0.18 | 0.02 |
| sun | 0.12 | 0.68 |

四格必须非负且总和为 $1$；这是后续所有推导的可验证前提。

## 定义与分步推导

**联合分布**给出 $P(X=x,Y=y)$。要忽略 $Y$ 的细节，就把所有兼容的 $y$ 加起来：

$$P(X=x)=\sum_yP(X=x,Y=y).$$

上表中 $P(X=\text{rain})=0.18+0.02=0.20$，称为 $X$ 的**边缘分布**；同理 $P(Y=\text{umbrella})=0.18+0.12=0.30$。

已知 $X=x$ 后，只在该行内重新归一化：

$$P(Y=y\mid X=x)=\frac{P(X=x,Y=y)}{P(X=x)},\qquad P(X=x)>0.$$

因此 $P(\text{umbrella}\mid\text{rain})=0.18/0.20=0.9$。分母是证据概率；若它为零，条件分布不由这个有限表定义，程序必须拒绝，而不能随意返回全零或均匀分布。

若每一格都满足

$$P(X=x,Y=y)=P(X=x)P(Y=y),$$

则 $X,Y$ 独立。这里 $0.18\ne0.20\times0.30$，所以天气与带伞不独立。独立是一个精确的概率乘积条件，不是“两个变量名称看上去无关”。

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

运行 `python -m unittest projects.naive_bayes_spam.test_joint_distribution`。实现先检查每格非负、有限且总和为一；再用一次扫描累计边缘概率。条件化只扫描给定行并除以证据概率。对有 $r$ 个非零联合状态的稀疏表，时间为 $O(r)$，额外空间为边缘状态数。

`independence_residual` 返回所有格中 $|P(x,y)-P(x)P(y)|$ 的最大值：它为零时是有限表独立性的证书；非零时给出偏离乘积模型的可量化证据，而不是只输出一个未经解释的布尔值。

## 正确性、边界与误区

边缘化不会丢失概率质量，因为对联合表的全部单元格恰好求和一次：$\sum_x\sum_yP(x,y)=1$。对正概率条件，条件表也归一：

$$\sum_yP(Y=y\mid X=x)=\frac{\sum_yP(X=x,Y=y)}{P(X=x)}=1.$$

- **零概率条件**：连续分布中还可借密度与极限定义条件分布；本节有限表不假装解决该更深问题。
- **遗漏状态**：观测表没有列出的组合到底是零概率还是未收集到，属于建模选择；必须在数据契约中写清。
- **样本频率不是已知真分布**：从计数估计联合表会有抽样误差，稀疏格还要考虑平滑与置信区间。
- **相关不是因果**：带伞与下雨相关，不证明伞导致雨或雨以外没有共同原因。

## 练习

1. **基础**：由表计算 $P(Y=\text{none})$ 与 $P(X=\text{sun}\mid Y=\text{umbrella})$。
2. **推导**：证明若联合表满足乘积关系，则对任意 $P(X=x)>0$ 有 $P(Y=y\mid X=x)=P(Y=y)$。
3. **编码**：为联合表加入从整数计数归一化的函数，并拒绝负计数和总数为零。
4. **开放**：设计一个垃圾邮件“含链接/含附件”联合表实验；说明如何区分数据相关、特征泄漏和可能的因果解释。

## 练习答案提示

1. 先按 $Y$ 的值跨行求和得到边缘概率；反向条件概率要用 $P(X=\text{sun},Y=\text{umbrella})/P(Y=\text{umbrella})$，不能沿用另一方向的分母。
2. 将 $P(x,y)=P(x)P(y)$ 代入条件概率定义并约去正的 $P(x)$；零概率行不在有限表的条件化定义域内。
3. 先验证所有计数是非负整数且总数正，再除以总数；归一化后还应测试概率和为一与边缘和的一致性。
4. 划分训练/测试时间段，检查特征是否在标签产生后才出现；联合相关只能提出假设，因果解释还需时间顺序、干预或混杂控制证据。

## 延伸

[条件概率与贝叶斯更新](/probability-ml/bayes)将联合—条件关系用于证据更新；[协方差与相关性](/probability-ml/covariance-correlation)把两个数值变量的共同变化进一步量化；[常见分布](/probability-ml/common-distributions)讨论如何在有限表之外选择生成模型。
