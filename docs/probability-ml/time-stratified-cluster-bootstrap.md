---
title: 时间分层簇级 Bootstrap：趋势与用户相关不能各抽各的
description: 在冻结时间层与互不重叠簇的受限合同下，按时间层内完整簇重采样校准差异。
courseLevel: "3（相关数据与监控设计）"
prerequisites: "时间块 Bootstrap、簇级 Bootstrap、概率校准"
estimatedMinutes: 70
experiment: "time-stratified-cluster-calibration-bootstrap/v1：层内整簇重采样 ECE 差"
---

# 时间分层簇级 Bootstrap：趋势与用户相关不能各抽各的

## 学习目标

- 识别逐条、时间块与簇级重采样各自保留和破坏的相关结构；
- 在冻结时间层内按完整簇重采样，并重放 ECE 差区间；
- 解释跨层重复簇为何需要配对纵向设计，而不是套用本课合同；
- 区分可重放的描述性不确定性与因果、自动行动结论。

## 从一个计算问题开始

日夜变化与同一设备连续上报同时存在时，逐条抽样会打碎两种结构，时间块会拆设备，按设备又会混合早晚流量。故本课冻结时间层、层内完整簇，并要求簇不跨层；它不是长时序、重复用户或因果设计的万能 bootstrap。

## 定义：先冻结两个轴，再抽样

设参考窗口按时间层排列为 $S_1,\ldots,S_T$。每一层含预定义簇

$$S_t=(C_{t,1},\ldots,C_{t,G_t}).$$

一次重采样不抽时间层，也不把观测行拆开。对每个固定的 $t$，独立抽取 $G_t$ 个层内簇索引 $I_{t,1},\ldots,I_{t,G_t}$，并拼接

$$C_{t,I_{t,1}}\Vert\cdots\Vert C_{t,I_{t,G_t}}.$$

早晚层不会互换，被抽到的簇保留全部观测。对参考/当前窗口各自重采样、重算 ECE，再保存

$$\Delta^*=\mathrm{ECE}_{current}^*-\mathrm{ECE}_{reference}^*$$

的固定百分位区间；分层不消除趋势，只保留冻结位置。

## 算法实验：逐层重抽完整簇

```python
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.stratified_cluster_calibration_bootstrap import (
    time_stratified_cluster_calibration_bootstrap_certificate,
    time_stratified_cluster_calibration_bootstrap_report,
)

def cluster(identifier, probabilities, labels):
    return {"cluster_id": identifier, "window": {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": probabilities, "labels": labels,
    }}

old = [
    {"time_stratum_id": "early", "clusters": [cluster("r-1", [.5], [1]), cluster("r-2", [.5], [0])]},
    {"time_stratum_id": "late", "clusters": [cluster("r-3", [.5], [1]), cluster("r-4", [.5], [0])]},
]
new = [
    {"time_stratum_id": "early", "clusters": [cluster("c-1", [.8], [1]), cluster("c-2", [.8], [0])]},
    {"time_stratum_id": "late", "clusters": [cluster("c-3", [.8], [1]), cluster("c-4", [.8], [0])]},
]
report = time_stratified_cluster_calibration_bootstrap_report(
    "old", old, "new", new, minimum_window_size=4, repeats=20, seed=7,
)
assert report["bootstrap_policy"]["resampling_unit"] == "predefined_cluster_within_frozen_time_stratum"
assert time_stratified_cluster_calibration_bootstrap_certificate("old", old, "new", new, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_stratified_cluster_calibration_bootstrap`。报告绑定层/簇形状、策略、种子和区间；证书从原始输入完整重建，篡改任一项会失败。

算法每次重复扫描所有被抽到的观测来计算两份 ECE。若总观测数为 $n$、重复次数为 $B$，成本约为 $O(Bn)$；更多 repeats 仅减少有限 Monte Carlo 的随机波动，不能增加时间层或独立簇的数量。

## 正确性：报告究竟证明什么

固定输入与种子决定层内簇索引；实现保留层顺序、原层簇数和整簇观测。证书重新规范化、采样并计算 ECE 差，而不相信报告端点。

这种可重放性只证明报告执行了声明的有限程序；它不保证层内可交换、层边界足够表达趋势、簇数足够、两个窗口可比，或差异由模型变更造成。`automatic_action` 固定为 `none`：区间是人工复核证据，不是自动重训、调阈值或上线授权。

## 失败案例与工程边界

**同一用户跨层。** 若 `u-17` 既在早期又在晚期出现，分别在两层抽它会破坏同一用户的纵向关联。本合同直接拒绝跨层重复的 `cluster_id`；这不是数据清洗建议，而是提醒你转向配对簇、层级模型或领域统计审查。

## 跨层重复簇：整条轨迹配对重抽

若每个用户在每个冻结层同时有参考/当前评估，重采样单位应是**完整用户轨迹**，而非某层中的用户片段。配对报告保存每层 ECE 差及首末层差异的趋势量：

```python
from projects.naive_bayes_spam.paired_longitudinal_calibration_bootstrap import (
    paired_longitudinal_cluster_calibration_bootstrap_certificate,
    paired_longitudinal_cluster_calibration_bootstrap_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION

def window(probabilities, labels):
    return {"contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": probabilities, "labels": labels}

trajectories = [
    {"cluster_id": "u-1", "time_strata": [
        {"time_stratum_id": "early", "reference_window": window([.5, .5], [1, 0]), "current_window": window([.8, .8], [1, 0])},
        {"time_stratum_id": "late", "reference_window": window([.4, .4], [1, 0]), "current_window": window([.95, .95], [1, 0])},
    ]},
    {"cluster_id": "u-2", "time_strata": [
        {"time_stratum_id": "early", "reference_window": window([.5, .5], [0, 1]), "current_window": window([.8, .8], [0, 1])},
        {"time_stratum_id": "late", "reference_window": window([.4, .4], [0, 1]), "current_window": window([.95, .95], [0, 1])},
    ]},
]
report = paired_longitudinal_cluster_calibration_bootstrap_report(
    "old", "new", trajectories, minimum_window_size=4, repeats=20, seed=7,
)
assert report["bootstrap_policy"]["resampling_unit"] == "whole_paired_cluster_trajectory_across_frozen_time_strata"
assert paired_longitudinal_cluster_calibration_bootstrap_certificate("old", "new", trajectories, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_paired_longitudinal_calibration_bootstrap`。每次抽取用户会同时复制其所有层和两侧窗口，轨迹必须有相同有序层；证书重放每层区间与首末趋势。它不是时间序列/层级模型，也不建立因果或自动行动结论。

**层内只有一个簇。** 一个层没有簇间抽样变化。代码要求每层至少两个簇；把更多 repeats 写得再大也不能制造第二个独立单位。

**趋势比层更细。** 每小时机制不同而只冻结“上午/下午”时，层内可交换仍可能失败；需要更合适的分层、块或时间序列模型。

**事后划层或选簇。** 先看 ECE 再合并小时或设备会把选择藏入输入；层、簇、分箱和复核政策应先冻结。

**因果解释。** 重抽簇不控制营销、流量来源或标签延迟，不能把描述性差异升级为模型改动效果。

## 常见误区

- “分层簇 bootstrap 解决所有相关性。”它只保留声明的两轴。
- “跨时间用户可独立层内抽。”那需要显式配对设计。
- “区间即可自动行动。”业务风险与数据质量仍需人工判断。

## 练习

1. **基础**：说明一次层内抽样为何不能把 `early` 簇变成 `late` 簇。
2. **推导**：给每层 $G_t$ 个簇，写出一次重采样总共抽取的簇数 $\sum_tG_t$，并解释为什么这不等于独立观测行数。
3. **编码**：将同一 `cluster_id` 放入两个时间层，确认合同拒绝输入；解释这比悄悄接受更诚实的原因。
4. **开放**：为跨七天、同一用户每天回访的监控任务设计替代方案，明确配对单位、趋势模型、预注册政策与人工复核步骤。

## 练习答案提示

1. 外层固定层，只在该层簇索引集合中抽样。
2. 总数为 $\sum_tG_t$；簇大小不同，行数不是独立证据数。
3. 跨层同 ID 表示纵向依赖，独立层内抽会破坏它。
4. 可按用户配对整条轨迹，并显式声明趋势与审核规则。

## 延伸与下一步

先复习[时间块 Bootstrap](/probability-ml/block-bootstrap-calibration)和[簇级 Bootstrap](/probability-ml/cluster-bootstrap-calibration)，理解本课为何不能简单拼接两个已有结论。真实纵向、季节性或干预评估应由统计领域人员选择层级、时间序列或因果模型。
