---
courseLevel: "1–2（抽样与推断）"
prerequisites: "期望、方差、独立随机变量"
estimatedMinutes: 55
experiment: "重复伯努利抽样，核对标准误的 1/sqrt(n) 缩放与经验覆盖率"
title: 大数定律与中心极限定理：样本均值为什么会稳定
description: 从样本均值的期望和方差推导标准误，区分收敛、近似正态与依赖/厚尾边界。
---

# 大数定律与中心极限定理：样本均值为什么会稳定

## 问题场景

产品转化率是 0.35 吗？一次抽到 100 名用户得到的比例可能是 0.29 或 0.41。为什么多收集数据通常会让均值稳定，却不能保证下一次样本恰好等于真值？

## 学习目标

读完后，你能推导样本均值的标准误；区分大数定律的收敛结论与 CLT 的分布近似；用可重复实验检查 $1/\sqrt n$ 缩放，并说明独立性、有限方差和样本设计何时失效。

## 直觉模型

把每个伯努利观察 $X_i\in\{0,1\}$ 看成一次硬币/转化事件，$P(X_i=1)=p$。样本均值 $\bar X_n$ 是比例。单次结果仍有噪声，但平均会相互抵消一部分独立波动；样本量翻四倍，典型波动只会约减半。

## 严格定义与分步推导

若 $X_1,\ldots,X_n$ 独立同分布、$\mathbb E[X_i]=\mu$、$\mathrm{Var}(X_i)=\sigma^2<\infty$，则

$$\bar X_n=\frac1n\sum_{i=1}^nX_i,\qquad
\mathbb E[\bar X_n]=\mu,$$

并且独立性消去交叉协方差：

$$
\mathrm{Var}(\bar X_n)=\frac1{n^2}\sum_{i=1}^n\sigma^2=\frac{\sigma^2}{n}.
$$

所以标准误为 $\sigma/\sqrt n$。弱大数定律说明 $\bar X_n$ 依概率收敛到 $\mu$；它不表示每个有限样本都接近。中心极限定理在适当条件下进一步给出

$$\frac{\sqrt n(\bar X_n-\mu)}{\sigma}\Rightarrow N(0,1),$$

其中 $\Rightarrow$ 是分布收敛：它给出大样本时误差形状的近似，不是说原始数据必须正态。

## 算法实现：检查缩放，而不是相信一次模拟

```python
from projects.naive_bayes_spam.sampling_limit_laws import sample_size_scaling_report

report = sample_size_scaling_report(0.5, 25, 100, trials=4000, seed=11)
assert report["expected_standard_error_ratio"] == 2.0
assert report["certificate"]["larger_sample_has_smaller_empirical_standard_error"]
assert report["certificate"]["observed_ratio_matches_inverse_sqrt_scaling"]
```

运行 `python -m unittest projects.naive_bayes_spam.test_sampling_limit_laws`。实验重复生成许多个伯努利样本均值，分别报告经验标准误、理论标准误与用 $\pm1.96\mathrm{SE}$ 形成的经验覆盖率。它的证书只检查固定参数和种子下的合理范围；模拟能揭示理论后果，不能替代 LLN/CLT 的证明。

生成 $T$ 次大小为 $n$ 的试验成本为 $O(Tn)$、储存为 $O(T)$（实现只保留均值）。生产统计系统会流式更新均值与方差，且必须记录抽样单位和随机种子。

## 反例实验：两百条日志不等于两百次独立观察

设有 $m$ 次真正独立的伯努利观察 $Z_1,\ldots,Z_m$，但日志管道将每一条完整复制一次：

$$
X_{2j-1}=X_{2j}=Z_j,\qquad j=1,\ldots,m.
$$

表面上得到 $2m$ 行记录，且每一行仍有相同的边缘概率 $P(X_i=1)=p$。但其均值不是 $2m$ 个独立量的平均：

$$
\bar X_{2m}=\frac1{2m}\sum_{j=1}^{m}(Z_j+Z_j)
=\frac1m\sum_{j=1}^{m}Z_j.
$$

因此真实方差为 $p(1-p)/m$；若只按行数套独立公式，会错误报告 $p(1-p)/(2m)$。标准误被低估为原来的 $1/\sqrt2$，即真实不确定性是天真报告的 $\sqrt2$ 倍。这不是“模拟偶尔不稳定”，而是同一潜在观测被重复使用造成的精确协方差结构。

```python
from projects.naive_bayes_spam.sampling_limit_laws import (
    duplicated_bernoulli_mean_report,
    duplicated_bernoulli_mean_report_certificate,
)

report = duplicated_bernoulli_mean_report(.5, 100, duplicates_per_draw=2, trials=4000, seed=13)
assert report["record_count"] == 200
assert report["expected_standard_error_inflation"] == 2 ** .5
assert report["certificate"]["cluster_aware_standard_error_exceeds_naive_iid"]
assert duplicated_bernoulli_mean_report_certificate(.5, 100, 2, 4000, 13, report)
```

这份固定种子报告不仅比较经验标准误，还同时给出按**独立抽样单位** $m$ 计算的理论标准误、按日志行数 $2m$ 得到的错误标准误及其比值；证书重放完整实验并拒绝修改其中任一结论。复制是最简单的相关结构，真实用户、会话或地区簇不必恰好成对，也不能仅凭这一例子得到通用簇稳健估计量；它只迫使我们在使用 $1/\sqrt n$ 前先问“$n$ 究竟数的是什么”。

## 正确性与工程边界

上面的方差推导真正依赖独立性。重复点击、同一用户的多条日志或按地区聚簇的数据会有正协方差，实际标准误可能远大于 $\sigma/\sqrt n$。极厚尾变量可能没有有限方差，CLT 的常规标准误近似也会失败；有偏抽样则即使 $n\to\infty$ 也只会稳定地收敛到错误总体。

## 常见误区

- “大数定律说明 100 个样本已经准确”：它是极限收敛，不给固定 $n$ 的误差保证。
- “CLT 说明数据正态”：它讨论标准化**均值**的近似分布。
- “日志越多越独立”：相关记录应按真正独立的用户、会话或簇处理。

## 练习

1. **基础**：伯努利 $p=0.2,n=400$ 的理论标准误是多少？
2. **推导**：在不独立时，把 $\mathrm{Var}(\sum_iX_i)$ 展开到协方差项。
3. **编码**：比较 $n=10,100,1000$ 的独立样本经验标准误；再把每条观察复制两次，比较按行数和按独立抽样单位计算的标准误。
4. **开放**：为按城市随机化的实验设计合适的重抽样/方差估计单位。

## 练习答案提示

1. 伯努利标准误为 $\sqrt{p(1-p)/n}$；代入 $p=0.2,n=400$，不要把单次观测方差直接当均值方差。
2. 展开 $\mathrm{Var}(\sum_iX_i)$，得到各方差之和加两两协方差；独立性正是在协方差为零处使用。
3. 对每个 $n$ 固定重复次数并记录种子，比较经验标准误与理论 $1/\sqrt n$ 比例；复制两次时均值仍只依赖原来的独立观察，天真行数公式会少一个 $\sqrt2$ 因子。单个 seed 的偏离是模拟噪声，不是理论反例。
4. 随机化在城市层就以城市/簇为重抽样或聚合单位；逐用户重抽样会错误假定同城用户独立，通常低估方差。

## 延伸

[抽样误差、置信区间与覆盖率](/probability-ml/confidence-intervals-sampling)将 CLT 近似变成区间；[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)把同一 $1/\sqrt n$ 规律用于随机积分。
