---
title: 失访不是缺失行：观测过程与逆概率加权
description: 把“谁的标签被观测到”作为随机过程建模，用有限总体的 Horvitz–Thompson 与 Hájek 估计审计选择偏差边界。
courseLevel: "3（观测机制与不确定性）"
prerequisites: "期望与方差、抽样误差、时间分层簇级 Bootstrap"
estimatedMinutes: 75
experiment: "attrition-ipw-observation-audit/v1：冻结入组队列、声明观测概率与加权均值审计"
---

# 失访不是缺失行：观测过程与逆概率加权

## 学习目标

- 将“是否得到标签”与结果值分开表示，而不是直接删除未观测行；
- 推导 Horvitz–Thompson 均值为何在已声明观测机制下无偏；
- 区分完整案例、HT 与 Hájek 估计，并识别 positivity 失败；
- 重放一份冻结队列的观测审计，同时拒绝把它误称为因果结论或真实世界补全方案。

## 从一个看似普通的平均数开始

模型上线两周后，只有完成回访的人有真实标签。若回访倾向与结果有关，`mean(observed outcomes)` 的分母已悄悄从“入组用户”变成“留下来的用户”。删行不是中性的预处理；它等于假定留下的人足以代表所有入组者。

先固定有限入组队列 $i=1,\ldots,N$。令 $Y_i$ 是目标结果，$R_i\in\{0,1\}$ 表示该结果是否被观测到，且把观测机制中的概率写为

$$
\pi_i=\Pr(R_i=1).
$$

目标并不是“已观测行的均值”，而是入组总体均值

$$
\mu=\frac{1}{N}\sum_{i=1}^{N}Y_i.
$$

若每个 $\pi_i$ 都为正、且它确实是当前冻结设计下的观测概率，HT 估计为

$$
\widehat{\mu}_{\mathrm{HT}}=\frac{1}{N}\sum_{i=1}^{N}\frac{R_iY_i}{\pi_i}.
$$

这里的 $R_i$ 很关键：失访者的结果不可见，但其贡献为零，且分母仍然是所有入组者 $N$。

## 推导：无偏来自观测指示变量，不来自“加权很神奇”

在 $Y_i$ 与声明的 $\pi_i$ 固定时，$\mathbb{E}[R_i]=\pi_i$，所以

$$
\mathbb{E}\!\left[\frac{R_iY_i}{\pi_i}\right]
=\frac{Y_i}{\pi_i}\mathbb{E}[R_i]
=Y_i.
$$

逐项相加并除以 $N$，得到 $\mathbb{E}[\widehat{\mu}_{\mathrm{HT}}]=\mu$。这个结论仅对声明的观测随机化取期望；一次具体样本仍会波动，也不允许把错误的 $\pi_i$ 变正确。

常见的归一化权重版本是 Hájek 估计：

$$
\widehat{\mu}_{\mathrm{H}}=
\frac{\sum_iR_iY_i/\pi_i}{\sum_iR_i/\pi_i}.
$$

它避免某次样本中总权重偏离 $N$ 的尺度问题，但这是比值估计，通常并非精确无偏。完整案例均值、HT、Hájek回答的是不同的有限样本问题，报告三者比只给一个“修正后数字”更诚实。

## 可运行审计：保留完整入组队列

下面的合同要求每位入组者出现一次；只有 `observed=True` 时才允许携带 `outcome`。`observation_probability` 是外部已经声明/审计过的教学输入，代码不会用结果反推它，也不会拟合倾向模型。

```python
from projects.naive_bayes_spam.attrition_ipw_audit import (
    attrition_ipw_observation_audit_certificate,
    attrition_ipw_observation_audit_report,
)

cohort = [
    {"unit_id": "a", "observed": True,  "observation_probability": .8, "outcome": 1.0},
    {"unit_id": "b", "observed": True,  "observation_probability": .4, "outcome": 0.0},
    {"unit_id": "c", "observed": False, "observation_probability": .8},
    {"unit_id": "d", "observed": False, "observation_probability": .4},
]
report = attrition_ipw_observation_audit_report(cohort, positivity_floor=.5)
assert report["cohort_shape"]["enrolled_units"] == 4
assert report["observation_policy"]["positivity_review_required"]
assert report["estimates"]["horvitz_thompson_mean"] == .3125
assert attrition_ipw_observation_audit_certificate(cohort, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_attrition_ipw_audit`。报告的 `observed_fraction` 描述失访规模；`minimum_probability`、最大已观测权重和 positivity 标记描述权重是否可能由少数单位支配；证书从原始队列和阈值重建全部结果，篡改估计或偷偷给未观测者填结果都会失败。

若 $\pi_i$ 很小，权重 $1/\pi_i$ 会很大。例如 $\pi_i=0.01$ 意味着单个被观测者权重为 $100$。这不是可以靠更多 bootstrap repeats 修好的数值噪声：它表示观察设计几乎从未覆盖该类人，有限样本方差和模型依赖都会变得尖锐。

## 正确性与识别边界

这份报告可验证三件事：入组分母没有被失访行缩小；已观测的结果按声明概率加权；阈值、概率列表和三个估计都与冻结输入一致。它**不**验证下列前提：

- 观测概率是否由真实产品流程正确产生；
- 未观测结果在给定设计变量后是否满足所需的随机观测假设；
- 是否有未记录的病情、设备状态或人工跟进同时影响结果和回访；
- 当前队列是否能推广到未来用户，或任何差异是否由一次干预造成。

因此 `automatic_action` 固定为 `none`。在真实研究里，观测概率可能需要由实验设计、随访记录或受审查模型提供；对时间相关、用户簇或重复访问，还必须先定义簇/轨迹层面的观测机制，不能把本课逐单位权重直接套用。

## 失败案例与工程边界

**把未观测结果当零。** 这会把“没有标签”变成一个强行假设的结果值，通常同时改变目标量和分布。

**只对 observed 行归一化，却声称 HT。** 这实际更接近 Hájek；HT 的分母是冻结的所有入组单位 $N$。

**某类人的 $\pi_i=0$。** 该类从不被观测，有限数据无法用逆概率权重恢复其结果；合同直接拒绝零概率，而非返回无穷权重。

**事后按结果选择 $\pi_i$。** 若先看标签再指定概率，推导中的 $\mathbb{E}[R_i]=\pi_i$ 已没有可审计含义。

**把加权差异说成因果效果。** IPW 用于观测/失访并不自动控制处理分配、干扰、时间趋势或未观测混杂；它不能取代随机化和因果设计。

## 练习

1. **基础**：为什么 HT 均值的分母是 $N$，而不是 `observed_outcomes`？
2. **推导**：从 $\mathbb{E}[R_i]=\pi_i$ 推出单项 $R_iY_i/\pi_i$ 的期望。
3. **编码**：把一个未观测单位的 `observation_probability` 改为零，确认合同拒绝它；说明为何不能用一个很大的有限权重替代。
4. **开放**：为七日回访实验列出需预先冻结的入组定义、观测窗口、概率来源、positivity 阈值、簇/轨迹单位和人工复核条件。

## 练习答案提示

1. 目标是入组总体均值；缩小分母会改写目标。
2. 将常量 $Y_i/\pi_i$ 提出期望，代入 $\mathbb{E}[R_i]$。
3. 零概率没有可识别的该类观测；大权重不能凭空产生覆盖。
4. 这些选择决定“谁是总体、谁会被观测、什么相关结构被保留”，不能看到结果后再决定。

## 延伸与下一步

[时间分层簇级 Bootstrap](/probability-ml/time-stratified-cluster-bootstrap)讨论相关样本应该按什么单位重抽；本课补上“哪些结果进入样本”的观测过程。两者都依赖外部设计前提。若存在多阶段随访、非单调失访、复杂时间序列或需要拟合失访模型，应由统计领域人员制定正式分析计划并做敏感性分析。
