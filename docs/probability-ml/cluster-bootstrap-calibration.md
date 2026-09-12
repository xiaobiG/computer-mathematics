---
title: 簇级 Bootstrap：相关用户不能逐条重抽
description: 在预先定义用户或设备簇的受限合同下，为校准窗口差异按完整簇重采样，并公开簇间可交换的假设。
courseLevel: "3（概率监控与相关观测边界）"
prerequisites: "冻结窗口差异的 Bootstrap、时间块 Bootstrap、概率校准"
estimatedMinutes: 60
experiment: "cluster-window-calibration-bootstrap/v1：固定种子下按完整用户/设备簇重采样 ECE 差"
---

# 簇级 Bootstrap：相关用户不能逐条重抽

## 学习目标

- 解释同一用户或设备的多条记录为何不能默认独立；
- 将预定义用户/设备簇作为完整重采样单位；
- 区分簇级区间、簇间可交换假设与部署决策；
- 判断何时应改用分层、加权、时间序列或专门的因果设计。

## 从一个计算问题开始

一名活跃用户可能在同一周贡献几十条模型评分；一台设备也可能因同一传感器偏差连续产生类似记录。若逐条放回抽样，这些记录会被拆散、又与其他用户任意混合，区间会把“有很多行”误读为“有很多独立证据”。

当问题关心用户或设备总体时，先在分析前冻结簇定义，再按完整簇抽样。这样不会消除簇间差异，却至少不会在重采样时把同一簇的共同结构拆碎。

## 定义与推导

设参考窗口有预定义簇 $C_1,\ldots,C_G$，每个 $C_g$ 内含该用户或设备的全部已标注观测。一次 bootstrap 先抽簇索引 $I_1,\ldots,I_G$，再拼接完整簇：

$$C_{I_1}\Vert C_{I_2}\Vert\cdots\Vert C_{I_G}.$$

对参考与当前窗口分别重复，重算 ECE 差 $\Delta=\mathrm{ECE}_{current}-\mathrm{ECE}_{reference}$，最后取固定百分位端点。簇内顺序和样本数都保留；同一簇可被抽到多次，也可能在某次重采样中未出现。

这个推导使用的不是“每一行独立”，而是“冻结后的簇在目标总体中近似可交换”。固定种子只能使簇索引重放，不能证明簇数量足够、簇间可交换或簇定义没有泄漏。

## 可运行实验：完整用户/设备簇重采样

```python
from projects.naive_bayes_spam.cluster_window_calibration_bootstrap import (
    cluster_window_calibration_bootstrap_certificate,
    cluster_window_calibration_bootstrap_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION

def cluster(identifier, probabilities, labels):
    return {"cluster_id": identifier, "window": {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": probabilities, "labels": labels,
    }}

old = [cluster("u-1", [.5, .5], [1, 0]), cluster("u-2", [.5], [0])]
new = [cluster("d-1", [.8, .8], [1, 0]), cluster("d-2", [.8], [0])]
report = cluster_window_calibration_bootstrap_report(
    "old", old, "new", new, minimum_window_size=3, repeats=20, seed=7,
)
assert report["bootstrap_policy"]["resampling_unit"] == "predefined_labeled_user_or_device_cluster"
assert report["bootstrap_policy"]["automatic_action"] == "none"
assert cluster_window_calibration_bootstrap_certificate("old", old, "new", new, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_cluster_window_calibration_bootstrap`。报告保存每个簇的标识和观测数、分箱政策、重复次数、种子及区间；证书重建整份报告，篡改簇大小、端点或行动策略都会被拒绝。

## 正确性与工程边界

在相同簇、政策和种子下，抽出的簇序列、每次 ECE 差和百分位区间都可重放。合同要求每个窗口至少两个非空且标识唯一的簇；一个簇没有可供簇间重采样的变化来源。

这只验证报告忠实执行了声明的簇级设计。它不证明用户是随机样本，不将“账户”误作独立个体，也不允许由区间自动重训、调阈值或上线；`automatic_action` 固定为 `none`。

## 失败案例与工程边界

- **同一用户跨窗口。** 若同一人同时出现在参考和当前窗口，两个窗口的差异可能配对相关；本合同不会自动改成配对 bootstrap。
- **少数超活跃簇。** 保留完整簇意味着重采样样本量会随抽到的簇变化；这不是错误，而是设计应报告的权重结构。
- **簇定义事后挑选。** 看完指标才改变设备分组会把选择偏差带入区间，必须预先冻结。
- **时间趋势仍存在。** 用户簇不能替代时间块；既有季节性或系统性趋势时要建模时间，或设计同时尊重时间和簇的方案。
- **簇标签不是因果处理。** 用户/设备 ID 不能单独证明某因素导致校准变化。

## 常见误区

- “簇 bootstrap 就保证独立。”不对，它只把独立性近似放在簇间。
- “一万条记录一定比十个用户可靠。”不一定；对用户总体而言，有效单位可能接近十而不是一万。
- “多抽几千次可修复簇数太少。”不对，更多 repeats 只降低模拟误差，不能创造新的簇信息。
- “区间越过零就能自动决策。”不对，统计报告不授予部署行动权限。

## 练习

1. 一个用户贡献 100 条记录、另外九位用户各贡献 1 条。解释逐条抽样为何会过度相信活跃用户。
2. 将簇大小列表写成 $[2,1]$ 与 $[20,1]$ 两种情况；说明为何每次重采样的观测总数可能变化。
3. 为“同一用户在两个窗口均出现”的情形写出配对簇 bootstrap 的伪代码，并说明它与本课合同的差异。
4. **开放**：设计一个同时有设备簇和日周期的监控实验；明确你会预先冻结哪些时间、簇与决策政策。

## 练习答案提示

1. 逐条抽样把同一人重复行为当作许多独立人，活跃用户的模式会被过度复制。
2. 每次抽中哪个完整簇决定拼接后的行数；报告应保留簇大小而不是假定固定行数。
3. 先用相同用户 ID 同时抽取其参考/当前记录，再在每一对内计算差异；这要求两个窗口具有明确可配对的簇集合。
4. 写出设备 ID、时间分块、纳入规则、最小簇数、区间和人工复核政策；不要从结果反推这些设置。

## 延伸与下一步

[时间块 Bootstrap](/probability-ml/block-bootstrap-calibration)处理短程时间相关；[冻结窗口差异的 Bootstrap](/probability-ml/frozen-window-bootstrap)说明逐观测抽样的更强前提；[子群体性能](/probability-ml/subgroup-performance-uncertainty)解释为什么先报告样本量政策。若簇与时间同时相关，应改用经领域审查的分层或时间序列设计，而不是把本教学合同拼接成生产统计系统。
