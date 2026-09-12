---
title: 冻结窗口的校准比较：先定义，再看差异
description: 用两个预先命名的带标签窗口、固定分箱与可重放证书比较校准差异，并限制结论为人工复核。
courseLevel: "3（概率校准与监控审计）"
prerequisites: "概率校准、带标签窗口、分组校准与抽样误差"
estimatedMinutes: 55
experiment: "重放两个冻结窗口的 ECE、Brier 差异与人工复核信号"
---

# 冻结窗口的校准比较：先定义，再看差异

## 学习目标

你将能在比较前冻结参考/当前窗口、分箱数、最小样本量和复核阈值；计算两个窗口的 ECE 与 Brier 差；区分描述性差异、抽样波动与因果归因；并用证书拒绝事后改政策的报告。

## 从“本月 ECE 变了”开始

如果先查看很多日期、分箱和切分方式，再只报告最大差异，差异本身已被选择过程放大。正确的起点不是问“哪里最坏”，而是预先写下：哪一个窗口是参考、哪一个是当前、每个窗口至少多少标签、使用多少箱，以及多大差异只进入人工复核。

## 直觉与定义：同一口径下的两个描述

对固定 $K$ 个箱，分别算参考与当前窗口的 $operatorname{ECE}_{K,r}$、$operatorname{ECE}_{K,c}$，并记录

$$Delta_{mathrm{ECE}}=operatorname{ECE}_{K,c}-operatorname{ECE}_{K,r}.$$

它描述同一报告口径下观测到的变化，不是模型退化的因果证明，也不是未来校准误差的置信区间。Brier 差也一并报告，因为 ECE 与平方损失回答不同问题。

## 可运行实验：冻结名称和政策

```python
from projects.naive_bayes_spam.window_calibration_comparison import (
    window_calibration_comparison_certificate,
    window_calibration_comparison_report,
)

reference = {"contract_version": "labeled-window/v1", "probabilities": [0.5] * 10, "labels": [1] * 5 + [0] * 5}
current = {"contract_version": "labeled-window/v1", "probabilities": [0.8] * 10, "labels": [1] * 5 + [0] * 5}
report = window_calibration_comparison_report("2025-Q1", reference, "2025-Q2", current, bins=5, minimum_window_size=10, ece_delta_review_threshold=.2)
assert report["comparison"]["expected_calibration_error_delta"] == .3
assert report["comparison"]["needs_review"]
assert report["causal_interpretation"] == "not_established"
assert window_calibration_comparison_certificate("2025-Q1", reference, "2025-Q2", current, report)
```

运行：

```bash
python -m unittest projects.naive_bayes_spam.test_window_calibration_comparison
```

报告拒绝相同窗口名、样本不足和无效政策；证书会重建两个窗口、每个分箱、阈值和差异。篡改 Brier 差或把阈值改大以抹除信号都会失败。

## 正确性与边界

每个窗口的 ECE 与 Brier 都复用固定分箱定义，因此两个值可在该政策下相减。若任一窗口样本量未达到门槛，合同拒绝生成比较，避免将小窗口噪声标为趋势。`needs_review` 只是阈值比较；没有自动动作、因果解释、群体排序或再校准。

复杂度为两个窗口样本数之和的 $O(n_r+n_c)$。这不控制多窗口、多分箱或多群体的选择偏差；这些比较对象必须在看结果前治理，若要量化抽样不确定性还需预先指定重采样或区间设计。

## 失败案例与工程边界

- **事后选窗口。** 不能把“最近表现最差的 7 天”与基线比较后称为预先注册检验。
- **把差异当原因。** 标签政策、输入分布、模型版本和随机波动都可能改变指标。
- **自动再校准。** 本合同只产生人工复核信号；高风险动作需要独立验证和治理。
- **忽略标签延迟。** 当前窗口必须是标签已成熟、口径与参考一致的带标签快照。

## 常见误区

- **“ECE 上升就证明模型变差。”** 不对；它只是在固定分箱下的观测差异。
- **“阈值是统计显著性。”** 不对；它是治理用复核政策。
- **“固定窗口名就足够。”** 不够；还要冻结分箱、最低样本和标签定义。
- **“没有信号就证明稳定。”** 不对；只是此政策未触发复核。

## 练习

1. 说明为何两个窗口要使用同一分箱数。
2. 若当前窗口只有 8 个标签、门槛是 20，合同应输出什么？
3. 解释 $Delta_{ECE}=0$ 为什么不表示两个窗口的分箱图完全相同。
4. 为人工复核写出两个可检查步骤，且不包含自动改模型。

## 练习答案提示

1. 分箱改变 ECE 定义；不同箱数的数值不能直接相减。
2. 拒绝比较并要求更多冻结、成熟标签，而非填 0。
3. 不同箱的正负变化和权重可以抵消；仍需查看每箱与 Brier。
4. 核对标签政策/模型版本和数据质量；在独立保留窗口复核，再决定是否做受控实验。

## 延伸

[分组校准](/probability-ml/subgroup-calibration-uncertainty)讨论总体掩盖局部差异；[带标签窗口](/probability-ml/labeled-window-performance-degradation)冻结性能口径；[随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)说明为何固定一次随机结果不等于不确定性分析。
