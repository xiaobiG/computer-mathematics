---
title: 分组校准：总体可信，为什么局部仍可能失真
description: 用固定分箱、ECE、最低样本量与可重放证书审计分组概率承诺，避免总体平均掩盖局部偏差。
courseLevel: "3（概率校准、分层评估与审计边界）"
prerequisites: "概率校准、带标签窗口、子群体性能、抽样误差"
estimatedMinutes: 60
experiment: "重放总体 ECE 为零而两个子群均失校准的抵消反例"
---

# 分组校准：总体可信，为什么局部仍可能失真

## 学习目标

你将能区分总体校准与预先定义子群的校准；从可靠性分箱推导期望校准误差（ECE）；识别总体平均如何掩盖方向相反的局部偏差；并用最低样本量、固定分箱政策和可重放证书约束结论。

## 从一个计算问题开始

一个审核模型对 20 个样本都报出 $0.8$。其中 16 个真的为正，于是总体经验频率也是 $16/20=0.8$。若只画总体可靠性图，这个箱恰好落在对角线上，ECE 也是零。

现在得知前 10 个来自预先治理并允许审计的组 A，只有 6 个为正；后 10 个来自组 B，10 个都为正：

$$
\bar p_A=\bar p_B=0.8,\qquad \bar y_A=0.6,\qquad \bar y_B=1.0.
$$

总体的两个偏差 $-0.2$ 与 $+0.2$ 正好抵消。它不表示任何组“天生”不同，更不建立原因；它只说明总体平均不能替代按既定审计维度检查概率承诺。

## 定义：分箱 ECE 与分组口径

固定把预测概率分到 $K$ 个等宽箱 $B_k$。对非空箱，令 $n_k$ 是计数、$\bar p_k$ 是平均预测、$\bar y_k$ 是经验正例率。常见的分箱 ECE 为

$$
\operatorname{ECE}_K=\sum_{k:n_k>0}\frac{n_k}{n}\lvert\bar p_k-\bar y_k\rvert.
$$

它介于 $[0,1]$，越小表示该**固定分箱**上的平均差距越小。它不是无分箱的真校准误差，也不会测量排序能力；改变 $K$ 就可能改变数值。因此报告必须保存 `bins`，而不能挑一个看起来最好的分箱数。

对组 $g$，只在 $n_g\ge m$ 时计算 $\operatorname{ECE}_{K,g}$ 与 Brier 分数。$m$ 是治理政策，不是普适定理：它受窗口长度、风险成本、隐私约束和可获得标签数影响。低于门槛时正确的输出是“证据不足”，不是 ECE 为零。

## 算法：一次分组，一次重放

报告输入是同一带标签窗口中的 `probabilities`、`labels` 和等长的预定义 `groups`。算法对总体及每个合格组执行相同的分箱：

1. 将每个 $p_i$ 放入 `min(int(p_i * K), K - 1)`，使 $p_i=1$ 进入最后一箱；
2. 对非空箱计算计数、平均预测、正例率、绝对差和 $n_k/n$ 加权贡献；
3. 求贡献和得到 ECE，同时报告 Brier 分数；
4. 对 $n_g<m$ 的组拒绝指标结论；对合格组仅在 ECE 达到预先记录阈值时发出人工复核信号。

时间复杂度为 $O(n+K\cdot G)$：样本只扫描一次以形成分组索引，随后各组总计仍处理 $n$ 个样本。这里的 $G$ 是实际出现的组数；这不是允许枚举或发掘无限候选群体的许可。

## 可运行实验：平均抵消反例

```python
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.subgroup_calibration import (
    subgroup_calibration_certificate,
    subgroup_calibration_report,
)

window = {
    "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
    "probabilities": [0.8] * 20,
    "labels": [1] * 6 + [0] * 4 + [1] * 10,
}
groups = ["A"] * 10 + ["B"] * 10
report = subgroup_calibration_report(
    window, groups, bins=5, minimum_group_size=10, ece_review_threshold=0.15
)
print(report["overall_metrics"]["expected_calibration_error"])  # 0.0
print([(row["group"], row["metrics"]["expected_calibration_error"])
       for row in report["subgroups"]])  # A、B 都是 0.2
assert subgroup_calibration_certificate(window, groups, report)
```

运行项目测试：

```bash
python -m unittest projects.naive_bayes_spam.test_subgroup_calibration
```

证书会重新生成窗口、组、分箱数、样本门槛和 ECE 阈值对应的整份报告。因此把阈值改大以消除信号、把 `causal_interpretation` 改成“已建立”，或篡改组内指标都会被拒绝。

## 正确性与证据边界

每个观测恰好进入一个箱：`min` 处理右端点，非空箱计数之和等于该组样本数。每箱的 `ece_contribution` 是非负的，且最多为其样本份额，所以 ECE 位于 $[0,1]$。这证明实现与给定分箱定义一致，不证明模型在未来、在其他分箱或在总体外部校准。

反例还揭示一个重要的聚合边界。总体的

$$
\left|\frac{n_A}{n}(\bar p_A-\bar y_A)+
\frac{n_B}{n}(\bar p_B-\bar y_B)\right|
$$

可以为零，即使每项的绝对值都很大；而分组 ECE 会先取绝对值，保留两个偏差。二者回答不同问题，不能互相替代。

## 失败案例与工程边界

- **事后搜索许多组。** 从几十个属性组合中只报告最大 ECE 会产生多重比较和选择偏差。组、窗口、门槛应在查看结果前治理并记录。
- **小样本稳定幻觉。** 此版本拒绝低于最小样本量的组，却还不把 ECE 转成置信区间；小而非零的 ECE 也可能是抽样波动。下一步需加入分组分箱的不确定性区间与重采样边界。
- **把描述性差异当成因果或公平结论。** 采集、标注、覆盖范围和条件分布都可能造成差异。报告的 `automatic_action` 始终为 `none`。
- **复用同一验证窗口调分箱和做最终报告。** 这会把诊断选择泄漏进结论。将策略冻结在独立设计阶段，最终用保留窗口一次性报告。

## 常见误区

- **“总体 ECE 很低，所以每个组都校准。”** 错；本页的抵消反例已给出反证。
- **“组内 ECE 高，所以模型歧视该组。”** 错；ECE 只是条件频率与预测的差距，不能单独解释原因或法律/伦理含义。
- **“样本不足就填 0。”** 错；这会把未知伪装成完美校准。
- **“换更多分箱一定更精确。”** 不一定；箱越细，每箱越稀疏。分箱是要预先记录的偏差—方差折中。

## 练习

1. 对两个等大的组，均预测 $0.7$；组一正例率为 $0.5$、组二为 $0.9$。计算总体和各组在单一非空箱下的 ECE。
2. 证明 ECE 的每项贡献非负，且总 ECE 不超过 1。
3. 构造一个 $n_g<m$ 的小组，其经验正例率看似与预测相差很大；解释为何报告仍应拒绝它。
4. 为此报告设计一个人工复核流程，明确列出哪些行动不能由 ECE 信号自动触发。

## 练习答案提示

1. 总体正例率也是 $0.7$，故总体 ECE 为 0；两个组分别为 $|0.7-0.5|=0.2$ 与 $|0.7-0.9|=0.2$。
2. 权重 $n_k/n$ 非负且和为 1，绝对差在 $[0,1]$，故加权和落在 $[0,1]$。
3. 分母太小会使频率大幅跳动；收集更多高质量标签或依据预先规则合并窗口，而不是发布确定性结论。
4. 信号可创建审计工单、检查数据与标签质量；不得自动重训、改阈值、限制服务或做因果归因。

## 延伸

[概率校准与可靠性曲线](/probability-ml/calibration-reliability)给出总体分箱定义；[子群体性能](/probability-ml/subgroup-performance-uncertainty)先建立最低样本量边界；[带标签窗口](/probability-ml/labeled-window-performance-degradation)说明标签延迟时应如何冻结比较口径。后续可在独立窗口上为每个分箱加入不确定性区间，但仍不能把统计区间变成自动决策器。
