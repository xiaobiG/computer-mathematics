---
title: 冻结窗口差异的 Bootstrap：区间不是部署结论
description: 为预先命名的校准窗口差异绑定固定种子、重采样单位和百分位区间，并保留描述性边界。
courseLevel: "3（概率监控与不确定性边界）"
prerequisites: "概率校准、冻结窗口比较、bootstrap 与置信区间"
estimatedMinutes: 60
experiment: "window-calibration-bootstrap/v1：固定种子下 ECE 差的百分位区间"
---

# 冻结窗口差异的 Bootstrap：区间不是部署结论

## 学习目标

你将能在比较两个预先命名的带标签窗口时，为 ECE 差构造固定设计的 bootstrap 百分位区间；说明重采样单位、种子和重复次数为何属于报告合同；并避免将区间写成因果、显著性或自动部署结论。

## 从一个计算问题开始

参考窗口与当前窗口的 ECE 差为 $\hat\Delta$。这只是一次有限样本的观察：若同一生成过程重新抽样，$\hat\Delta$ 会变化。bootstrap 从各自窗口内有放回抽取同样数量的**带标签观测**，每次重算 $\hat\Delta^{*(b)}$，用固定分位数描述该估计器在这个重采样模型下的变化。

## 定义与算法

对 $B$ 次重采样，百分位区间为

$$[q_{\alpha/2}(\hat\Delta^*),q_{1-\alpha/2}(\hat\Delta^*)].$$

本实验预先固定分箱、窗口、最小样本量、$B$、种子、置信水平与“观测级重采样”单位。种子不制造统计真实性，却让同一教学报告可以精确重放。窗口存在用户内相关、时间依赖或事后选组时，观测级 bootstrap 不再匹配数据生成过程。

## 可运行实验

```python
from projects.naive_bayes_spam.window_calibration_bootstrap import (
    window_calibration_bootstrap_certificate, window_calibration_bootstrap_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION

old = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.5] * 10, "labels": [1] * 5 + [0] * 5}
new = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.8] * 10, "labels": [1] * 5 + [0] * 5}
report = window_calibration_bootstrap_report("old", old, "new", new, minimum_window_size=10, repeats=40, seed=11)
assert report["bootstrap_policy"]["automatic_action"] == "none"
assert window_calibration_bootstrap_certificate("old", old, "new", new, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_window_calibration_bootstrap`。证书从窗口、策略、种子重建全部重采样序列与区间；篡改区间端点或种子都会失败。

## 正确性与边界

在固定伪随机生成器与输入下，重放得到同一索引序列、ECE 差列表和分位数。它证明报告忠实于声明的重采样设计，不证明总体差异方向、因果变化或未来校准质量。`automatic_action` 固定为 `none`。

## 失败案例与工程边界

- **时间依赖。** 连续事件不能任意按观测重抽；需预先定义 block bootstrap。
- **用户内相关。** 多次点击应按用户或簇重采样。
- **事后挑选窗口。** 区间不修复已发生的多重比较和选择偏差。
- **小样本或空分箱。** 重采样变化很大时应报告证据不足，而不是只挑好看的端点。

## 常见误区

- **“区间跨 0 就没有问题。”** 它只描述本合同下的抽样变化。
- **“固定种子就是独立复现。”** 它只使计算可重放。
- **“bootstrap 自动适合所有数据。”** 重采样单位必须匹配依赖结构。
- **“区间决定是否上线。”** 监控报告不具有自动行动授权。

## 练习

1. 为什么需要预先固定重采样单位？
2. 如何把按观测重采样改为按用户重采样？
3. 比较百分位区间与 ECE 差点估计各自回答的问题。
4. 列出一个区间存在却仍不应行动的场景。

## 练习答案提示

1. 它定义你假设可交换、独立的基本观测单位。
2. 先抽用户，再保留该用户所有观测；不要拆散相关记录。
3. 点估计是当前差异，区间是固定重采样模型下的有限样本变化。
4. 例如窗口是事后挑选、标签质量未知或业务风险需要额外审核。

## 延伸

[冻结窗口的校准比较](/probability-ml/frozen-window-calibration-comparison)给出点差异合同；[抽样误差与覆盖率](/probability-ml/confidence-intervals-sampling)讨论 bootstrap 假设；[子群体校准](/probability-ml/subgroup-calibration-uncertainty)说明最小样本量边界。
