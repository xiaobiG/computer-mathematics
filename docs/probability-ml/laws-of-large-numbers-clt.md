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

若 $X_1,\ldots,X_n$ 独立同分布、$\mathbb E[X_i]=\mu$、$\operatorname{Var}(X_i)=\sigma^2<\infty$，则

$$\bar X_n=\frac1n\sum_{i=1}^nX_i,\qquad
\mathbb E[\bar X_n]=\mu,$$

并且独立性消去交叉协方差：

$$
\operatorname{Var}(\bar X_n)=\frac1{n^2}\sum_{i=1}^n\sigma^2=\frac{\sigma^2}{n}.
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

运行 `python -m unittest projects.naive_bayes_spam.test_sampling_limit_laws`。实验重复生成许多个伯努利样本均值，分别报告经验标准误、理论标准误与用 $\pm1.96\operatorname{SE}$ 形成的经验覆盖率。它的证书只检查固定参数和种子下的合理范围；模拟能揭示理论后果，不能替代 LLN/CLT 的证明。

生成 $T$ 次大小为 $n$ 的试验成本为 $O(Tn)$、储存为 $O(T)$（实现只保留均值）。生产统计系统会流式更新均值与方差，且必须记录抽样单位和随机种子。

## 正确性与工程边界

上面的方差推导真正依赖独立性。重复点击、同一用户的多条日志或按地区聚簇的数据会有正协方差，实际标准误可能远大于 $\sigma/\sqrt n$。极厚尾变量可能没有有限方差，CLT 的常规标准误近似也会失败；有偏抽样则即使 $n\to\infty$ 也只会稳定地收敛到错误总体。

## 常见误区

- “大数定律说明 100 个样本已经准确”：它是极限收敛，不给固定 $n$ 的误差保证。
- “CLT 说明数据正态”：它讨论标准化**均值**的近似分布。
- “日志越多越独立”：相关记录应按真正独立的用户、会话或簇处理。

## 练习

1. **基础**：伯努利 $p=0.2,n=400$ 的理论标准误是多少？
2. **推导**：在不独立时，把 $\operatorname{Var}(\sum_iX_i)$ 展开到协方差项。
3. **编码**：比较 $n=10,100,1000$ 的经验标准误，并记录不同 seed 的波动。
4. **开放**：为按城市随机化的实验设计合适的重抽样/方差估计单位。

## 延伸

[抽样误差、置信区间与覆盖率](/probability-ml/confidence-intervals-sampling)将 CLT 近似变成区间；[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)把同一 $1/\sqrt n$ 规律用于随机积分。
