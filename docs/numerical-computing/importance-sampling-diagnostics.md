---
title: 重要性采样诊断：权重、ESS 与方差不是同一件事
description: 在有真值的一维积分上比较均匀采样与 q(x)=2x，重放权重、标准误和有效样本量。
courseLevel: "3（随机积分与数值诊断）"
prerequisites: "蒙特卡洛、期望与方差、数值积分"
estimatedMinutes: 60
experiment: "importance-sampling-x8/v1 与 adaptive-importance-sampling-split/v1：固定提议和适配—估计分离报告"
---

# 重要性采样诊断：权重、ESS 与方差不是同一件事

## 学习目标

你将推导重要性权重、比较同一积分上的两种提议、解释 ESS，并区分固定提议、数值稳定化与选后自适应的边界。

## 从一个计算问题开始

目标积分为

$$I=\int_0^1x^8\,dx=\frac19.$$

均匀采样多落在接近 0 的低贡献区域。令 $U\sim\mathrm{Unif}(0,1)$、$X=\sqrt U$，则 $q(x)=2x$，更常访问接近 1。无偏估计器是

$$\hat I_q=\frac1N\sum_{i=1}^N\frac{X_i^8}{2X_i}=\frac1N\sum_{i=1}^N\frac{X_i^7}{2}.$$

## 定义与诊断

一般地，$q(x)>0$ 覆盖目标支撑时，$f(x)/q(x)$ 的样本均值估计积分。权重并不自动好：常用诊断

$$ESS=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}$$

接近 $N$ 表示权重较均匀；远小于 $N$ 表示少数样本主导。ESS 不是误差界或支撑检查。

## 可运行实验

```python
from projects.floating_point_museum.importance_sampling import importance_sampling_certificate, importance_sampling_report

report = importance_sampling_report(200, 17)
assert report["exact_value"] == 1 / 9
assert 0 < report["importance"]["effective_sample_size"] <= 200
assert importance_sampling_certificate(200, 17, report)
```

运行 `python -m unittest projects.floating_point_museum.test_importance_sampling`。报告重放误差、标准误、ESS 与最大权重；篡改会失败。生成与累加为 $O(N)$ 时间和 $O(N)$ 额外空间。

## 算法：在对数域归一化权重

在高维模型中，密度常是许多小因子的乘积，直接计算 $w_i$ 再求和会下溢；反过来，未归一化权重的指数也可能溢出。若已经获得有限对数权重 $\ell_i=\log w_i$，令 $m=\max_i\ell_i$，则

$$
\tilde w_i=\frac{\exp(\ell_i-m)}{\sum_j\exp(\ell_j-m)},
\qquad
\log\sum_iw_i=m+\log\sum_i\exp(\ell_i-m).
$$

减去同一 $m$ 不改变归一化比例，却保证每个指数的输入不大于 0。由归一化权重可稳定计算 $ESS=1/\sum_i\tilde w_i^2$ 和最大权重：

```python
from projects.floating_point_museum.importance_sampling import (
    log_weight_diagnostics, log_weight_diagnostics_certificate,
)

report = log_weight_diagnostics([1000.0, 999.0, 990.0])
assert abs(sum(report["normalized_weights"]) - 1.0) < 1e-12
assert log_weight_diagnostics_certificate([1000.0, 999.0, 990.0], report)
```

例子令 `exp(1000)` 溢出，但平移后仍可重放诊断。算法为 $O(N)$ 时间和输出空间，并拒绝 `NaN`、无穷和少于两项的输入。

## 自适应 pilot 不能悄悄成为最终估计

两点目标为 $(0.2,0.8)$、总和为 $1$；候选 $q_U=(.5,.5)$、$q_T=(.8,.2)$ 各抽一笔 pilot，并故意选择较大的估计。枚举四种组合：复用选中 pilot 的期望为 $1.6$；pilot 只选 $q$、再独立估计的条件及总体期望均为 $1$：

```python
from projects.floating_point_museum.importance_sampling import (
    adaptive_importance_sampling_split_certificate,
    adaptive_importance_sampling_split_report,
)

report = adaptive_importance_sampling_split_report(17)
analysis = report["exact_policy_analysis"]
assert analysis["reused_pilot_expectation"] == 1.6
assert analysis["split_estimate_expectation"] == report["target"]["exact_sum"] == 1.0
assert adaptive_importance_sampling_split_certificate(17, report)
```

这不是通用自适应 IS，也不说所有自适应有偏；它只表明：pilot 选 $q$ 后，不能无推导地复用作选后证据，须分离批次或给出序贯修正。

## 正确性与边界

变量替换给出 $q(x)=2x$，故 $x^8/q(x)=x^7/2$。零点虽为零测度，伪随机数仍可能产生它，故实现重抽。经验标准误不保证覆盖真值。

该提议适合 $x^8$，不代表适合尖峰、厚尾、高维或未知归一化密度。对数域只改变数值表示，不修复支撑、方差或 ESS。

## 失败案例与工程边界

- **支撑/尾部。** $q=0$、无限方差或未定义积分不能靠更多样本或对数权重修复。
- **权重退化。** ESS 小只说明少数样本主导，不能过度解释点估计。
- **种子与适配。** 种子只为重放；pilot 选提议后须分离最终估计或采用已推导的序贯修正。

## 常见误区

- **“ESS 大就一定准确。”** 它只诊断权重集中度。
- **“重要性采样总比均匀好。”** 提议差时方差可以更大。
- **“自归一化和本课估计器一样。”** 未知归一化时的自归一化估计有限样本一般有偏。
- **“标准误是误差上界。”** 它是模型和有限样本下的估计量。

## 练习

1. 从 $X=\sqrt U$ 推导 $q(x)=2x$。
2. 为什么它对靠近 0 的目标可能很差？
3. 将 $x^8$ 改为 $x^p$，如何选更匹配的提议？
4. 重放报告要记录什么？为何对数权重或一个 pilot 不能证明无界域目标可积？

## 练习答案提示

1. $P(X\le x)=P(U\le x^2)=x^2$，求导为 $2x$。
2. 它少抽 0 附近，补偿权重可能很大。
3. 向主要贡献区倾斜且不漏支撑，仍检查权重。
4. 目标、域、提议、变换、样本数、种子、估计器、诊断及 pilot/估计批次边界；对数平移不证明可积性、尾部或支撑。

## 延伸

[多维积分的结构化采样](/numerical-computing/multidimensional-integration)对照网格预算；[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)给出概率视角；[稳定求和](/numerical-computing/kahan-summation)解释长权重和的数值边界。
