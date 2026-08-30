---
title: 共轭先验与后验预测：平滑为什么有数学含义
description: 从 Beta–Bernoulli 共轭更新推导后验、MAP 与后验预测，并实现可验证的小样本平滑实验。
courseLevel: "2–3（贝叶斯推断、推导与工程建模）"
prerequisites: "条件概率、伯努利分布、最大似然与期望"
estimatedMinutes: 60
experiment: "实现 Beta–Bernoulli 后验参数、MAP 与下一次观测的后验预测"
---

# 共轭先验与后验预测：平滑为什么有数学含义

## 学习目标

读完后，你能推导 Beta–Bernoulli 后验；区分 MLE、MAP 和后验预测；解释拉普拉斯平滑的伪计数意义；实现可验证的更新函数；并识别先验不是“自动客观”、数据漂移也不会被平滑消除。

## 从一次全正面开始

只观察到一枚硬币一次正面，MLE 给出 $\hat p=1$。若下一次反面，模型立刻把其概率设为零，既不稳健也不符合有限样本直觉。与其临时加一个常数，不如明确写出我们在数据前的分布假设，并让它通过贝叶斯公式更新。

## 严格定义与共轭推导

伯努利参数 $p$ 的 Beta 先验为

$$p\sim\operatorname{Beta}(\alpha,\beta),\qquad \pi(p)\propto p^{\alpha-1}(1-p)^{\beta-1}.$$

若数据中成功 $h$ 次、失败 $t$ 次，似然正比于 $p^h(1-p)^t$。相乘得到

$$p\mid D\sim\operatorname{Beta}(\alpha+h,\beta+t).$$

先验与后验属于同一族称为共轭；更新只需加计数，无需数值积分。$\alpha-1,\beta-1$ 可看作对模式位置有影响的伪计数，但这只是有用直觉，不能掩盖其来自先验选择。

## MAP 与后验预测不是一回事

当后验两个参数都大于 1，内部 MAP 为

$$p_{MAP}=\frac{\alpha+h-1}{\alpha+\beta+h+t-2}.$$

而下一次为正的后验预测是对参数积分：

$$P(X_{next}=1\mid D)=E[p\mid D]=\frac{\alpha+h}{\alpha+\beta+h+t}.$$

均匀先验 $\operatorname{Beta}(1,1)$、一次正面时，MAP 落在边界而后验预测为 $2/3$。因此“平滑后的概率”通常对应后验预测，不能无条件标成 MAP。

## 可运行实验

```python
from projects.naive_bayes_spam.beta_bernoulli import posterior_parameters, posterior_predictive_success

assert posterior_parameters([1, 1, 0], 2, 3) == (4, 4)
assert posterior_predictive_success([1], 1, 1) == 2 / 3
```

```bash
python -m unittest projects.naive_bayes_spam.test_beta_bernoulli
```

实现扫描观测一次，时间 $O(n)$、额外空间 $O(1)$。测试覆盖成功/失败计数、空数据下回到先验预测、MAP 的内部存在条件和非法输入。

## 正确性与工程边界

函数直接实现后验参数相加和后验均值公式，故在 $alpha,\beta>0$ 且数据为 0/1 时与推导一致。此模型假设观测在给定 $p$ 时独立同分布；邮件词频、用户行为和时间序列常违反这一假设。选择强先验会在小样本中显著影响结果，选择弱先验不会修复错误特征、标签偏差或部署分布变化。

## 常见误区

1. “先验就是主观，所以不能用。”错误：应公开、敏感性分析和验证，而不是假装不存在假设。
2. “MAP 等于后验均值。”错误：一般不同，边界情形尤其明显。
3. “伪计数是真实历史数据。”错误：它是先验的解释方式，不是观测记录。
4. “平滑能处理数据漂移。”错误：它只调节有限样本估计，不处理分布变化。

## 练习

1. **基础题**：用 Beta$(2,3)$ 先验与 4 正 1 反计算后验参数和后验预测。
2. **推导题**：从先验与似然相乘推导后验比例式，并说明归一化常数为何仍是 Beta 分布。
3. **编码题**：为后验预测加入“先验强度”参数化测试，比较相同均值、不同总强度的结果。
4. **开放题**：为低基率垃圾邮件事件选择一组先验，写明领域依据、敏感性分析和何时应重新估计。

## 练习答案提示

1. 后验参数为 $(2+4,3+1)$，下一次成功的后验预测是 $\alpha'/(\alpha'+\beta')$；区分后验参数与 MAP。
2. 相乘后幂次分别为成功数加 $\alpha-1$、失败数加 $\beta-1$，正是 Beta 核；归一化常数由积分有限且参数为正保证。
3. 保持先验均值 $\alpha/(\alpha+\beta)$ 不变，只改变总量；小样本下强先验更难被数据拉动，数据很多时差异应减小。
4. 写明基率来源和先验等效样本量，扫描合理区间并在时间漂移、标签定义或数据源改变后重新审计；先验不是替代验证的理由。

## 延伸

[最大似然](/probability-ml/maximum-likelihood)提供没有先验时的极值估计；[贝叶斯更新](/probability-ml/bayes)给出一般公式；[垃圾邮件分类器](/projects/naive-bayes-spam)将平滑用于词条件概率。下一步可学习 Dirichlet–Categorical、层级模型和后验预测检查。
