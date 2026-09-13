---
title: 相关样本的置信区间：AR(1) 下为什么会欠覆盖
description: 用平稳 AR(1) 的有限窗口方差与可重放模拟，审计把相关观测误当独立样本时的区间欠覆盖。
search: false
courseLevel: "3（时间相关与不确定性）"
prerequisites: "协方差、置信区间、两状态 Markov 链的有限窗口方差"
estimatedMinutes: 85
experiment: "stationary-ar1-mean-interval-coverage/v1：相关序列的已知方差区间覆盖率对照"
---

# 相关样本的置信区间：AR(1) 下为什么会欠覆盖

## 学习目标

- 推导相关均值的有限窗口方差；
- 用覆盖率实验看见朴素区间的欠覆盖；
- 以声明的 Bartlett 带宽估计长程方差，并与 Oracle 对照；
- 区分已声明模型的结论与真实日志推断。

## 问题：同样 40 条记录，为什么区间会错

设 $X_t=\phi X_{t-1}+\varepsilon_t$，其中 $|\phi|<1$，创新独立且方差为 $\sigma_\varepsilon^2$。平稳起点下

$$
\gamma_0=\operatorname{Var}(X_t)=\frac{\sigma_\varepsilon^2}{1-\phi^2},
\qquad
\operatorname{Cov}(X_t,X_{t+k})=\gamma_0\phi^k.
$$

把每个 $X_t$ 当独立观测会用 $\gamma_0/n$；正相关时它漏掉窗口内的正协方差。

## 有限窗口推导：不能直接把极限搬到样本上

令 $\bar X_n=n^{-1}\sum_{t=1}^nX_t$。每个 lag $k$ 出现 $n-k$ 次，因此精确公式是

$$
\operatorname{Var}(\bar X_n)=\frac{\gamma_0}{n^2}
\left[n+2\sum_{k=1}^{n-1}(n-k)\phi^k\right].
$$

定义 $n_{\mathrm{eff}}=\gamma_0/\operatorname{Var}(\bar X_n)$。$\phi=.8,n=40$ 时它远小于 40。长程方差近似只适用于大样本；本页报告保留上述精确求和。

## 可运行实验：两种区间面对同一批相关序列

```python
from projects.naive_bayes_spam.dependent_interval_coverage import (
    ar1_mean_interval_coverage_certificate,
    ar1_mean_interval_coverage_report,
)

report = ar1_mean_interval_coverage_report(.8, 1.0, 40, 2000, 17)
assert report["naive_iid_interval_coverage"] < .80
assert report["exact_finite_window_interval_coverage"] > .90
assert report["effective_independent_sample_size"] < 40
assert ar1_mean_interval_coverage_certificate(.8, 1.0, 40, 2000, 17, 1.96, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_dependent_interval_coverage`。两种区间都知道正确边际方差；差别仅是朴素版本删掉了 lag 协方差。

## 从已知模型到数据估计：Bartlett HAC

真实序列不会交出 $\phi$。固定带宽 $m$ 后，以样本中心化自协方差 $\hat\gamma_k$ 计算

$$
\hat\sigma^2_{\mathrm{HAC}}=\hat\gamma_0+
2\sum_{k=1}^{m}\left(1-\frac{k}{m+1}\right)\hat\gamma_k.
$$

`ar1_bartlett_hac_interval_coverage_report(.8, 1, 80, 8, 2000, 29)` 会并列重放：样本方差 i.i.d. 区间、Bartlett HAC 区间与知道真模型的 Oracle 区间。此有限样本设置里 HAC 明显改善欠覆盖，却仍低于 Oracle；带宽是报告输入，不是脚本偷偷挑出的“最佳答案”。若估计为非正，报告会计数而不会伪造区间。

## 正确性与工程边界

平稳 AR(1) 的 $k$ 步协方差为 $\gamma_0\phi^k$，代入双重求和即得上式。重复模拟的真均值是零，故可审计覆盖率。真实日志还须检查趋势、结构突变、簇与失访，并审查 HAC、块 bootstrap 或时间序列模型。

## 常见误区

- “观测很多，区间自然可靠。”错：正态近似不补回协方差。
- “ESS 是记录条数。”错：它是指定方差模型下的等价量。
- “HAC 自动解决时间序列推断。”错：带宽和适用模型仍要声明、诊断。
- “代码校准了真实指标。”错：它没有从数据拟合 $\phi$。

## 练习

1. **基础**：令 $\phi=0$，化简方差与 $n_{\mathrm{eff}}$。
2. **推导**：为何 lag $k$ 有 $n-k$ 对？
3. **编码**：改为 $\phi=-.4$，比较方差与 ESS。
4. **工程**：列出用户监控区间前需冻结的时间窗、簇与失访假设。

## 练习答案提示

1. 正 lag 项为零，故为 $\gamma_0/n$ 与 $n$。
2. 更大的起点会越出窗口。
3. 负协方差抵消波动，仍需检查模型。
4. 不能把按日行数当独立用户，也不能忽略失访。

## 延伸

[两状态 Markov 链方差](/probability-ml/markov-dependent-sample-mean)给出离散状态版本；[时间块 Bootstrap](/probability-ml/block-bootstrap-calibration)是不完全指定 AR(1) 时的重采样入口。
