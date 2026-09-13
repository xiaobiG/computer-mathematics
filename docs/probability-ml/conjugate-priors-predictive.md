---
title: 共轭先验与后验预测：平滑为什么有数学含义
description: 从 Beta–Bernoulli 共轭更新推导后验、MAP、单次与 Beta–Binomial 批量后验预测，并实现可验证的小样本平滑实验。
courseLevel: "2–3（贝叶斯推断、推导与工程建模）"
prerequisites: "条件概率、伯努利分布、最大似然与期望"
estimatedMinutes: 60
experiment: "实现 Beta–Bernoulli 后验参数、MAP、下一次与批量观测的后验预测"
---

# 共轭先验与后验预测：平滑为什么有数学含义

## 学习目标

读完后，你能推导 Beta–Bernoulli 后验；区分 MLE、MAP、单次和批量后验预测；解释拉普拉斯平滑的伪计数意义及参数不确定性为何增大批量预测方差；实现可验证的更新函数；并识别先验不是“自动客观”、数据漂移也不会被平滑消除。

## 从一次全正面开始

只观察到一枚硬币一次正面，MLE 给出 $\hat p=1$。若下一次反面，模型立刻把其概率设为零，既不稳健也不符合有限样本直觉。与其临时加一个常数，不如明确写出我们在数据前的分布假设，并让它通过贝叶斯公式更新。

## 严格定义与共轭推导

伯努利参数 $p$ 的 Beta 先验为

$$p\sim\mathrm{Beta}(\alpha,\beta),\qquad \pi(p)\propto p^{\alpha-1}(1-p)^{\beta-1}.$$

若数据中成功 $h$ 次、失败 $t$ 次，似然正比于 $p^h(1-p)^t$。相乘得到

$$p\mid D\sim\mathrm{Beta}(\alpha+h,\beta+t).$$

先验与后验属于同一族称为共轭；更新只需加计数，无需数值积分。$\alpha-1,\beta-1$ 可看作对模式位置有影响的伪计数，但这只是有用直觉，不能掩盖其来自先验选择。

## MAP 与后验预测不是一回事

当后验两个参数都大于 1，内部 MAP 为

$$p_{MAP}=\frac{\alpha+h-1}{\alpha+\beta+h+t-2}.$$

而下一次为正的后验预测是对参数积分：

$$P(X_{next}=1\mid D)=E[p\mid D]=\frac{\alpha+h}{\alpha+\beta+h+t}.$$

均匀先验 $\mathrm{Beta}(1,1)$、一次正面时，MAP 落在边界而后验预测为 $2/3$。因此“平滑后的概率”通常对应后验预测，不能无条件标成 MAP。

## 批量后验预测：不要把不确定的参数塞回一个点估计

令 $\alpha'=\alpha+h,\beta'=\beta+t$，并令未来 $r$ 次中的成功总数为 $Y$。给定同一个未知参数 $p$，有 $Y\mid p,D\sim\mathrm{Binomial}(r,p)$；但后验预测不是把 $p$ 替换成均值后停止，而是继续对后验积分：

$$P(Y=k\mid D)=\binom{r}{k}\frac{B(\alpha'+k,\beta'+r-k)}{B(\alpha',\beta')},\qquad 0\le k\le r.$$

这就是 Beta–Binomial 分布。它的均值与把 $p$ 替换为后验均值 $q=\alpha'/(\alpha'+\beta')$ 相同：

$$E[Y\mid D]=rq.$$

但方差不同：

$$\operatorname{Var}(Y\mid D)=\frac{r\alpha'\beta'(\alpha'+\beta'+r)}{(\alpha'+\beta')^2(\alpha'+\beta'+1)},\qquad \operatorname{Var}_{\mathrm{plug\text{-}in}}(Y)=rq(1-q).$$

差额来自同一个尚未确定的 $p$ 被未来的多次试验共享：在条件模型内试验独立，并不代表把 $p$ 积分掉以后它们仍独立。比如均匀先验下观测一次成功，未来两次的 $Y=0,1,2$ 概率是 $1/6,1/3,1/2$；点估计 Binomial$(2,2/3)$ 会给出 $1/9,4/9,4/9$，低估两端事件。

## 可运行实验

```python
from projects.naive_bayes_spam.beta_bernoulli import beta_bernoulli_report

report = beta_bernoulli_report([1, 1, 0], 2, 3)
assert report["posterior"] == (4, 4)
assert report["posterior_predictive_success"] == 1 / 2
assert report["interior_map"] == 1 / 2
assert report["certificate"]["valid"]

endpoint_report = beta_bernoulli_report([1], 1, 1)
assert endpoint_report["posterior_predictive_success"] == 2 / 3
assert endpoint_report["interior_map"] is None
```

```python
from projects.naive_bayes_spam.beta_bernoulli import beta_binomial_predictive_report

batch_report = beta_binomial_predictive_report([1], future_trials=2, alpha=1, beta=1)
assert batch_report["posterior"] == (2, 1)
assert abs(sum(batch_report["success_count_probabilities"]) - 1) < 1e-12
assert batch_report["predictive_variance"] > batch_report["plugin_binomial_variance"]
assert batch_report["certificate"]["valid"]
```

```bash
python -m unittest projects.naive_bayes_spam.test_beta_bernoulli
```

单次报告扫描观测一次，时间 $O(n)$、额外空间 $O(1)$；批量报告额外枚举 $0$ 到 $r$ 的成功数，时间 $O(n+r)$、额外空间 $O(r)$。`beta_bernoulli_report` 显式交出成功/失败计数、后验参数、后验预测和（若存在）内部 MAP；`beta_binomial_predictive_report` 使用对数 Gamma 函数稳定计算每个有限概率质量，并交出批量均值、两个方差与差额。两个证书都会从原始输入重算结论：篡改预测值、后验参数、批量观测或将端点众数伪装成内部 MAP 都会被拒绝。

## 正确性与工程边界

函数直接实现后验参数相加、后验均值和 Beta–Binomial 概率质量公式，故在 $\alpha,\beta>0$、数据为 0/1 且未来试验数为非负整数时与推导一致。批量分布依赖一个明确的联合模型：未来观测在给定同一 $p$ 时条件独立且同分布；若每次试验有不同概率、存在时间漂移或层级相关，就不该把这份方差公式当作数据生成机制。报告证书只审计该模型内的代数关系：它不能证明独立同分布，也不能替你选择先验。邮件词频、用户行为和时间序列常违反这些假设；强先验会在小样本中显著影响结果，弱先验也不会修复错误特征、标签偏差或部署分布变化。

## 常见误区

1. “先验就是主观，所以不能用。”错误：应公开、敏感性分析和验证，而不是假装不存在假设。
2. “MAP 等于后验均值。”错误：一般不同，边界情形尤其明显。
3. “伪计数是真实历史数据。”错误：它是先验的解释方式，不是观测记录。
4. “平滑能处理数据漂移。”错误：它只调节有限样本估计，不处理分布变化。

## 练习

1. **基础题**：用 Beta$(2,3)$ 先验与 4 正 1 反计算后验参数和后验预测。
2. **推导题**：从先验与似然相乘推导后验比例式，并说明归一化常数为何仍是 Beta 分布。
3. **编码题**：篡改 `beta_bernoulli_report` 的预测值、后验参数和 `interior_map`，确认 `beta_bernoulli_certificate` 分别拒绝；再对未来 $r$ 次实现 Beta–Binomial 质量，验证其方差不小于同均值 plug-in Binomial 方差。
4. **开放题**：为低基率垃圾邮件事件选择一组先验，写明领域依据、敏感性分析和何时应重新估计。

## 练习答案提示

1. 后验参数为 $(2+4,3+1)$，下一次成功的后验预测是 $\alpha'/(\alpha'+\beta')$；区分后验参数与 MAP。
2. 相乘后幂次分别为成功数加 $\alpha-1$、失败数加 $\beta-1$，正是 Beta 核；归一化常数由积分有限且参数为正保证。
3. 证书应从原始观测重算成功/失败数、后验参数和预测均值；只有两个后验参数都大于 1 时才接受内部 MAP。批量质量应对 $k=0,\ldots,r$ 求和为 1，方差差额是正的（当 $r>0$ 且后验参数有限为正）。保持先验均值 $\alpha/(\alpha+\beta)$ 不变，只改变总量；小样本下强先验更难被数据拉动，数据很多时差异应减小。
4. 写明基率来源和先验等效样本量，扫描合理区间并在时间漂移、标签定义或数据源改变后重新审计；先验不是替代验证的理由。

## 延伸

[最大似然](/probability-ml/maximum-likelihood)提供没有先验时的极值估计；[贝叶斯更新](/probability-ml/bayes)给出一般公式；[垃圾邮件分类器](/projects/naive-bayes-spam)将平滑用于词条件概率。下一步可学习 Dirichlet–Categorical、层级模型和后验预测检查。
