---
title: 多组概率的部分汇聚：Beta–Binomial 层级模型为何让小组向整体收缩
description: 用共享 Beta 先验推导多组伯努利率的后验、收缩权重与不确定性，并审计“组可交换”假设的边界。
courseLevel: "3（层级模型与小样本决策）"
prerequisites: "共轭先验与后验预测、条件概率、期望与方差"
estimatedMinutes: 75
experiment: "hierarchical-beta-binomial-partial-pooling/v1：冻结组计数与共享先验下的部分汇聚"
---

# 多组概率的部分汇聚：Beta–Binomial 层级模型为何让小组向整体收缩

## 学习目标

- 区分每组独立 MLE、完全合并与部分汇聚三个估计策略；
- 从共享 Beta 先验推导组后验均值等于数据均值与先验均值的加权组合；
- 解释小样本组为何收缩得更多，并检查该结论依赖的可交换性；
- 运行可重放报告，避免把先验共享、超参数拟合和因果比较混为一谈。

## 同为“100%”，证据却不一样

一个新地区观察到 1 次成功、0 次失败，另一个地区观察到 80 次成功、20 次失败。两者的 MLE 分别是 1 和 0.8；若直接按组排序，新地区似乎最好。但前者只有一次试验，不能和 100 次观测拥有同等稳定性。

完全合并会把所有地区塞进一个概率，丢掉真正的组差异。完全分离会让每个小组孤立，放大抽样噪声。**部分汇聚**介于两者之间：允许每组有自己的概率，但让这些概率来自一个公开的共享分布。

## 两层模型与后验更新

对预先定义的组 $g=1,\ldots,G$，令其成功率为 $p_g$。本课固定超参数并设

$$
p_g\mid\alpha,\beta\sim\operatorname{Beta}(\alpha,\beta),
\qquad X_g\mid p_g\sim\operatorname{Binomial}(n_g,p_g).
$$

这里的第二层是组内观测，第一层是各组率围绕同一 Beta 分布的来源；给定固定的 $\alpha,\beta$，各组独立更新。若组 $g$ 有 $s_g$ 次成功、$f_g$ 次失败，则

$$
p_g\mid D_g,\alpha,\beta\sim
\operatorname{Beta}(\alpha+s_g,\beta+f_g).
$$

记先验均值为 $\mu_0=\alpha/(\alpha+\beta)$，组内 MLE 为 $\widehat p_g=s_g/n_g$。当 $n_g>0$ 时，后验均值可重写为

$$
\mathbb E[p_g\mid D_g]
=\underbrace{\frac{n_g}{\alpha+\beta+n_g}}_{w_g}\widehat p_g
+\underbrace{\frac{\alpha+\beta}{\alpha+\beta+n_g}}_{1-w_g}\mu_0.
$$

这不是“把结果随便拉回平均数”：权重来自后验代数。$n_g$ 小时 $w_g$ 小，组估计更多受共享先验影响；数据变多时 $w_g\to1$，该组证据逐渐主导。

## 可运行实验：冻结组、公开先验与收缩权重

```python
from projects.naive_bayes_spam.hierarchical_beta_binomial import (
    hierarchical_beta_binomial_certificate,
    hierarchical_beta_binomial_report,
)

groups = [
    {"group_id": "small", "successes": 1, "failures": 0},
    {"group_id": "large", "successes": 80, "failures": 20},
]
report = hierarchical_beta_binomial_report(groups, alpha=2, beta=2)
small, large = report["groups"]
assert small["mle"] == 1.0
assert small["posterior"]["mean"] == .6
assert small["partial_pooling"]["data_weight"] < large["partial_pooling"]["data_weight"]
assert hierarchical_beta_binomial_certificate(groups, 2, 2, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_hierarchical_beta_binomial`。报告绑定每组成功/失败数、固定超参数、先验强度、后验方差和加权恒等式；证书从输入完整重建。篡改某组后验均值、组计数或超参数都会失败。

例中先验均值为 0.5、强度为 4。`small` 的权重为 $1/(4+1)$，所以一次成功后的后验均值是 $(2+1)/(2+2+1)=0.6$，而不是 1；`large` 的权重为 $100/(4+100)$，因此其 0.8 的数据均值几乎不被改变。

## 后验方差与“组越小越不确定”

若组后验参数为 $a_g,b_g$，则

$$
\operatorname{Var}(p_g\mid D_g)=
\frac{a_gb_g}{(a_g+b_g)^2(a_g+b_g+1)}.
$$

它衡量的是当前模型下组率的不确定性，不是跨组真实异质性的直接估计。课程代码保存此方差，以免读者只看到收缩后的点估计而忘记组信息量不同。

注意：本实验中的 $\alpha,\beta$ 是**外部固定输入**，并没有从这些组反推“总体分布”。若要根据多组数据估计超参数，就进入 empirical Bayes 或完整层级贝叶斯推断，需要额外的拟合诊断、先验敏感性和计算方法。

## 正确性与工程边界

代码逐组实现 Beta–Binomial 共轭更新，并显式核对后验均值的加权形式；因此在计数非负、至少两组且 $\alpha,\beta>0$ 时与上述有限模型一致。它做不到、也不声称做到：

- **验证组可交换。** 地区、时间段或设备是否可视为来自同一分布，是领域假设而非证书能证明的事实。
- **拟合超参数。** 固定先验并不等于从数据学得合理先验；更不能把当前组的结果循环用于选择有利超参数。
- **处理时间相关与失访。** 连续用户轨迹和标签缺失需要相应的观测/相关结构；请结合[失访与逆概率加权](/probability-ml/attrition-observation-ipw)与时间分层课程另行设计。
- **给出因果组效应。** 组间构成、暴露与收集机制不同，后验均值差不是处理效应。

## 常见误区

- “共享先验代表所有组真实相同。”错：模型允许不同 $p_g$，只是假定它们有共同来源分布。
- “小组向整体收缩说明小组错了。”错：这是信息量较低时的正则化，不是事实裁决。
- “后验均值就是总体汇总率。”错：每组后验和合并总体回答不同问题。
- “多组就自动是层级模型。”若每组各自随意选先验，没有共享层就没有本课的部分汇聚结构。

## 练习

1. **基础**：Beta$(2,2)$ 先验、组计数为 3 成功 1 失败时，计算后验参数与均值。
2. **推导**：把后验均值展开并整理为 $w_g\widehat p_g+(1-w_g)\mu_0$。
3. **编码**：新增一个零观测组，预测其后验均值与方差；解释为何不能把它删除后声称完成了该组预测。
4. **开放**：为按周、地区和设备三重分组的校准监控写出一个层级/时间模型草案，并列出可交换性、失访和隐私约束。

## 练习答案提示

1. 后验为 Beta$(5,3)$，均值为 $5/8$。
2. 将分子拆成 $s_g$ 与 $\alpha$，把 $s_g$ 写为 $n_g\widehat p_g$。
3. 零观测组的均值等于先验均值，方差是先验方差；删除它会改变“报告哪些预定义组”的声明。
4. 先区分重复单位与时间趋势，再决定哪个层共享分布；不要把三维切片当作独立样本。

## 延伸

[共轭先验与后验预测](/probability-ml/conjugate-priors-predictive)给出单组更新与批量预测；[子群体性能](/probability-ml/subgroup-performance-uncertainty)讨论为何先看样本量。下一步可学习可估计超参数的层级贝叶斯、后验预测检查与时间序列状态空间模型。
