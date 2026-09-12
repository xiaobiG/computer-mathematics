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

一周内的模型请求既有日间/夜间的系统性变化，也有同一设备连续上报的相关记录。逐条 bootstrap 会同时打碎两种结构；只按时间块抽样又会拆开设备；只按设备抽样则可能把早期与晚期流量混合。若目标是描述固定窗口的校准差异，我们至少要让重采样单位同时说明**它属于哪个时间层**与**它保留哪个完整簇**。

本课建立一个刻意狭窄的教学合同：时间层在分析前冻结、每层含至少两个完整簇、同一簇不跨层出现。它让读者看见怎样保留两种结构；它不是为真实长时序、重复用户或因果评估提供万能 bootstrap。

## 定义：先冻结两个轴，再抽样

设参考窗口按时间层排列为 $S_1,\ldots,S_T$。每一层含预定义簇

$$S_t=(C_{t,1},\ldots,C_{t,G_t}).$$

一次重采样不抽时间层，也不把观测行拆开。对每个固定的 $t$，独立抽取 $G_t$ 个层内簇索引 $I_{t,1},\ldots,I_{t,G_t}$，并拼接

$$C_{t,I_{t,1}}\Vert\cdots\Vert C_{t,I_{t,G_t}}.$$

因此早期层仍是早期层，晚期层仍是晚期层；某个设备簇被抽到时，它的概率、标签和全部观测仍一起出现。对参考/当前窗口各自重采样、重算 ECE，再保存

$$\Delta^*=\mathrm{ECE}_{current}^*-\mathrm{ECE}_{reference}^*$$

的固定百分位区间。这里的“分层”不是让时间趋势消失，而是拒绝让重采样把已冻结的时间位置互换。

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

运行 `python -m unittest projects.naive_bayes_spam.test_stratified_cluster_calibration_bootstrap`。报告保存每层的 ID、层内簇 ID 与观测数、分箱策略、重复次数、种子和区间。证书从原始层/簇输入完整重建报告，因此修改某层的簇大小、策略、种子或区间都会失败。

算法每次重复扫描所有被抽到的观测来计算两份 ECE。若总观测数为 $n$、重复次数为 $B$，成本约为 $O(Bn)$；更多 repeats 仅减少有限 Monte Carlo 的随机波动，不能增加时间层或独立簇的数量。

## 正确性：报告究竟证明什么

固定输入与种子后，伪随机序列决定每一层内的簇索引。实现按原时间层顺序处理，且每个层恰抽与原层簇数相同的次数；所以它不会将 `early` 的簇放进 `late`，也不会只复制簇中的一条记录。证书并不相信报告声称的大小或端点，而是重新规范化输入、重新采样、重新计算 ECE 差并逐字段比较。

这种可重放性证明的是：**这份报告忠实执行了声明的有限重采样程序**。它不证明以下统计假设：

- 每个时间层内的簇可交换；
- 层边界足够表达趋势或季节性；
- 簇数量足以支持稳定区间；
- 参考与当前窗口具有可比的人群或采样机制；
- ECE 差异由某次模型变更造成。

所以 `automatic_action` 固定为 `none`。区间是人工复核的证据，不是自动重训、调阈值或上线的授权。

## 失败案例与工程边界

**同一用户跨层。** 若 `u-17` 既在早期又在晚期出现，分别在两层抽它会破坏同一用户的纵向关联。本合同直接拒绝跨层重复的 `cluster_id`；这不是数据清洗建议，而是提醒你转向配对簇、层级模型或领域统计审查。

**层内只有一个簇。** 一个层没有簇间抽样变化。代码要求每层至少两个簇；把更多 repeats 写得再大也不能制造第二个独立单位。

**趋势比层更细。** 若每小时机制都不同，而你只冻结“上午/下午”，层内可交换仍可能不成立。需要更合适的分层、块设计或显式时间序列模型。

**事后划层或选簇。** 先看 ECE 再决定把哪些小时或设备合并，会把选择过程藏入输入。层、簇、最小窗口、分箱、重复次数和复核政策都应先冻结。

**因果解释。** 同一时间内重抽簇并不能控制营销活动、流量来源或标签延迟；它不把描述性差异升级为模型改动的效果。

## 常见误区

- “分层簇 bootstrap 同时解决所有相关性。”不对；它只保留已声明的两个结构轴。
- “同一个用户跨时间更应该出现在每层。”不在这个合同里；那是需要显式配对的不同设计。
- “区间不跨零就可以自动行动。”不对；业务风险、漂移原因和数据质量仍需人工判断。

## 练习

1. **基础**：说明一次层内抽样为何不能把 `early` 簇变成 `late` 簇。
2. **推导**：给每层 $G_t$ 个簇，写出一次重采样总共抽取的簇数 $\sum_tG_t$，并解释为什么这不等于独立观测行数。
3. **编码**：将同一 `cluster_id` 放入两个时间层，确认合同拒绝输入；解释这比悄悄接受更诚实的原因。
4. **开放**：为跨七天、同一用户每天回访的监控任务设计替代方案，明确配对单位、趋势模型、预注册政策与人工复核步骤。

## 练习答案提示

1. 外层循环固定时间层，只在该层的簇索引集合中有放回抽样；拼接顺序不跨层。
2. 每层抽回原层簇数，合计为 $\sum_tG_t$；每个簇携带的观测行数不同，不能把行数当成独立证据数。
3. 跨层同 ID 暗示纵向依赖，而独立层内抽样会破坏它；拒绝迫使分析者选择能表达该依赖的设计。
4. 例如按用户配对整个时间轨迹，再将日/周趋势作为模型成分；说明何时停止、如何排除数据及谁审核结论。

## 延伸与下一步

先复习[时间块 Bootstrap](/probability-ml/block-bootstrap-calibration)和[簇级 Bootstrap](/probability-ml/cluster-bootstrap-calibration)，理解本课为何不能简单拼接两个已有结论。真实纵向、季节性或干预评估应由统计领域人员选择层级、时间序列或因果模型。
