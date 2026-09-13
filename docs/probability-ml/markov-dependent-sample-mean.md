---
title: 时间相关观测的样本均值：两状态 Markov 链的精确方差
description: 在平稳二状态 Markov 模型中，将滞后协方差精确累加为均值方差与有效独立样本量。
courseLevel: "3（时间相关与不确定性）"
prerequisites: "期望与方差、大数定律与中心极限定理、Metropolis–Hastings"
estimatedMinutes: 70
experiment: "stationary-two-state-markov-mean-variance/v1：平稳转移矩阵下的有限窗口方差"
---

# 时间相关观测的样本均值：两状态 Markov 链的精确方差

## 学习目标

- 展开相关样本均值的协方差项，而不是沿用 i.i.d. 的方差公式；
- 从两状态 Markov 转移概率推导平稳均值与滞后相关；
- 计算有限窗口的精确均值方差和等价独立样本量；
- 说明这份模型不等于从日志自动识别时间序列、混合或因果机制。

## 100 条连续日志，不必等于 100 次新证据

连续状态有惯性：边缘成功率相同不代表交叉协方差为零。令 $X_t\in\{0,1\}$，转移概率为

$$
\Pr(X_{t+1}=1\mid X_t=0)=a,
\qquad
\Pr(X_{t+1}=0\mid X_t=1)=b,
$$

并假定 $X_1$ 已从该链的平稳分布抽取。于是

$$
p=\Pr(X_t=1)=\frac{a}{a+b},
\qquad \rho=1-a-b.
$$

$\rho$ 是相关衰减因子：

$$
\operatorname{Cov}(X_t,X_{t+k})=p(1-p)\rho^k.
$$

当 $a=b=.1$ 时 $\rho=.8$；当 $a=b=.5$ 时 $\rho=0$，退回 i.i.d. 协方差结构。

## 有限窗口方差：每个滞后出现的次数并不相同

令 $\bar X_n=n^{-1}\sum_{t=1}^nX_t$。将方差展开并按滞后 $k$ 收集配对，得到

$$
\operatorname{Var}(\bar X_n)=
\frac{p(1-p)}{n^2}
\left[n+2\sum_{k=1}^{n-1}(n-k)\rho^k\right].
$$

滞后 $k$ 只出现 $n-k$ 对；独立公式则是 $p(1-p)/n$。定义 $n_{\mathrm{eff}}$ 使

$$
\operatorname{Var}(\bar X_n)=\frac{p(1-p)}{n_{\mathrm{eff}}}.
$$

正相关时 $n_{\mathrm{eff}}<n$；负相关时可能更大，表示声明模型中的波动抵消。

## 可运行实验：把每一个滞后协方差交给报告

```python
from projects.naive_bayes_spam.two_state_markov_variance import (
    stationary_two_state_markov_mean_variance_certificate,
    stationary_two_state_markov_mean_variance_report,
)

report = stationary_two_state_markov_mean_variance_report(.1, .1, 10)
assert report["declared_chain"]["stationary_probability_of_one"] == .5
assert report["declared_chain"]["second_eigenvalue_rho"] == .8
assert report["mean_variance"] > report["iid_same_marginal_variance"]
assert report["effective_independent_sample_size"] < 10
assert stationary_two_state_markov_mean_variance_certificate(.1, .1, 10, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_two_state_markov_variance`。报告和证书绑定每个 lag、i.i.d. 对照、方差与有效样本量；公开所有 lag 使报告为 $O(n)$ 空间。

## 正确性与边界

平稳方程给出 $p$；转移矩阵的偏离每步乘 $\rho$，故协方差为 $p(1-p)\rho^k$。代入均值双重求和即得公式。报告仅适用于正确参数、平稳起点的一阶二状态链；它不验证拟合、burn-in、多用户、失访或干预。现实推断仍需[时间块 Bootstrap](/probability-ml/block-bootstrap-calibration)、[时间分层簇级 Bootstrap](/probability-ml/time-stratified-cluster-bootstrap)或受审查的时间序列模型。

## 常见误区

- “边缘概率相同，所以 i.i.d.”错：边缘相同不等于联合独立。
- “有效样本量一定是整数。”错：它是等价方差的连续量。
- “$\rho$ 接近零证明独立。”错：高阶依赖和非平稳性仍可能存在。
- “抽稀 MCMC 会免费增加信息。”错：它只改变存储和相关结构。

## 练习

1. **基础**：令 $a=b=0.5$，证明公式如何化为 i.i.d. 方差。
2. **推导**：为什么 lag $k$ 在长度 $n$ 的窗口中只出现 $n-k$ 对？
3. **编码**：比较 $(a,b)=(.1,.1)$ 和 $(.5,.5)$ 在 $n=20$ 的有效样本量，并解释差异。
4. **开放**：为同一用户每日回访的监控设计一个模型检查计划，分别说明平稳性、用户簇与失访如何被审计。

## 练习答案提示

1. 此时 $\rho=0$，所有正 lag 项都为零。
2. 配对可从位置 1 到 $n-k$ 开始，超过该位置会越出窗口。
3. 前者有正相关，方差较 i.i.d. 大；后者正 lag 协方差为零。
4. 先固定时间窗和用户单位，再检查趋势/结构变化与回访缺失；不要直接把行数当独立量。

## 延伸

[大数定律与中心极限定理](/probability-ml/laws-of-large-numbers-clt)给出独立样本的基线；[Metropolis–Hastings](/probability-ml/metropolis-hastings)说明 MCMC 的相关状态与混合诊断。更一般的时间序列需要状态空间模型、谱密度或 HAC 方差估计等额外工具。
