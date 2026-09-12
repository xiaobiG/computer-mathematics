---
title: 重要性采样诊断：权重、ESS 与方差不是同一件事
description: 在有真值的一维积分上比较均匀采样与 q(x)=2x，重放权重、标准误和有效样本量。
courseLevel: "3（随机积分与数值诊断）"
prerequisites: "蒙特卡洛、期望与方差、数值积分"
estimatedMinutes: 60
experiment: "importance-sampling-x8/v1：均匀与重要性采样的固定种子报告"
---

# 重要性采样诊断：权重、ESS 与方差不是同一件事

## 学习目标

你将能从提议分布推导重要性权重；在真值已知的积分中比较均匀和重要性采样；解释 ESS 与最大归一化权重；并知道一个固定种子报告不能证明任意提议分布可靠。

## 从一个计算问题开始

目标积分为

$$I=\int_0^1x^8\,dx=\frac19.$$

均匀采样把大部分预算花在接近 0 的低贡献区域。令 $U\sim\operatorname{Unif}(0,1)$、$X=\sqrt U$，则 $X$ 的密度为 $q(x)=2x$，更常访问接近 1 的区域。无偏估计器是

$$\hat I_q=\frac1N\sum_{i=1}^N\frac{X_i^8}{2X_i}=\frac1N\sum_{i=1}^N\frac{X_i^7}{2}.$$

## 定义与诊断

一般地，$q(x)>0$ 覆盖目标支撑时，$f(x)/q(x)$ 的样本均值估计积分。权重并不自动好：常用诊断

$$ESS=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}$$

接近 $N$ 表示权重较均匀，远小于 $N$ 则少数样本主导。ESS 不是误差界，也不能替代重复运行、标准误或提议分布的支撑检查。

## 可运行实验

```python
from projects.floating_point_museum.importance_sampling import importance_sampling_certificate, importance_sampling_report

report = importance_sampling_report(200, 17)
assert report["exact_value"] == 1 / 9
assert 0 < report["importance"]["effective_sample_size"] <= 200
assert importance_sampling_certificate(200, 17, report)
```

运行 `python -m unittest projects.floating_point_museum.test_importance_sampling`。报告固定样本数和种子，重放两种估计的误差、估计标准误、ESS 与最大归一化权重；篡改任一诊断会使证书失效。生成与累加均为 $O(N)$ 时间和 $O(N)$ 额外空间（为清楚计算诊断而保留权重）。

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

这个例子故意使用会令 `exp(1000)` 溢出的输入；实现先平移再指数化，因此仍可重放全部诊断。算法为 $O(N)$ 时间和 $O(N)$ 输出空间。它只接受有限对数权重：`NaN`、无穷值和少于两项的输入都明确拒绝，避免把不可解释的数值状态伪装成 ESS。

## 正确性与边界

变量替换给出 $q(x)=2x$，因此对 $x>0$ 有 $x^8/q(x)=x^7/2$；零点是零测度，但伪随机数可能精确产生 0，教学实现明确重抽而不进行除零。报告的标准误来自当前有限样本的经验方差，不能保证覆盖真值。

该提议恰好适合单调 $x^8$ 基准，不代表适合尖峰、厚尾、高维或未知归一化密度。现实高维权重应在对数域计算，并报告尾部诊断与多种种子。对数域只改变数值表示，不会让支撑遗漏、无限方差或低 ESS 神奇消失。

## 失败案例与工程边界

- **支撑遗漏。** 若目标非零处 $q=0$，权重无定义，不能靠更多样本修复。
- **权重退化。** ESS 小意味着估计由少数样本决定，点估计不应被过度解释。
- **固定种子选择偏差。** 种子用于重放，不可挑选“看起来最好”的一次。
- **高维下溢。** 连乘密度会下溢；生产实现需使用 log-weight 和 log-sum-exp。
- **无界域或奇异目标。** 目标/提议比值可能没有有限方差，甚至积分本身未定义；先证明可积性、覆盖与尾部条件，不能只把权重改写为对数。
- **事后自适应提议。** 用同一批样本挑选提议再报告同一批估计会改变推断语义；需要预先规定的适应规则、独立评估或专门的序贯方法。

## 常见误区

- **“ESS 大就一定准确。”** 它只诊断权重集中度。
- **“重要性采样总比均匀好。”** 提议差时方差可以更大。
- **“自归一化和本课估计器一样。”** 未知归一化时的自归一化估计有限样本一般有偏。
- **“标准误是误差上界。”** 它是模型和有限样本下的估计量。

## 练习

1. 从 $X=\sqrt U$ 推导 $q(x)=2x$。
2. 为什么 $q(x)=2x$ 对靠近 0 的目标函数可能是坏提议？
3. 将 $x^8$ 改为 $x^p$，讨论如何选择更匹配的提议。
4. 写出需要记录哪些信息，才能独立重放一次重要性采样报告；解释为什么对数权重稳定化不能证明无界域目标可积。

## 练习答案提示

1. $P(X\le x)=P(U\le x^2)=x^2$，求导得到 $2x$。
2. 它很少抽到 0 附近，可能产生大的补偿权重。
3. 应让 $q$ 向主要贡献区域倾斜且不遗漏支撑；仍要检查权重诊断。
4. 目标函数、域、提议、采样变换、样本数、种子、估计器和所有诊断参数。对数平移只防止有限数的溢出/下溢；可积性、尾部和支撑是独立的数学前提。

## 延伸

[多维积分的结构化采样](/numerical-computing/multidimensional-integration)对照网格预算；[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)给出概率视角；[稳定求和](/numerical-computing/kahan-summation)解释长权重和的数值边界。
