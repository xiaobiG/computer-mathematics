---
title: 数据漂移监控：何时不应再相信校准概率
description: 以分类分布的 PSI 和总变差距离检测输入漂移，区分协变量、标签与概念漂移，并把告警限制为人工审查触发器。
courseLevel: "3（概率模型评估与工程验证）"
prerequisites: "经验分布、对数、概率校准、验证集与测试集"
estimatedMinutes: 60
experiment: "比较参考期与当前期的词类别分布，生成含 PSI、总变差距离和可重放证书的漂移报告"
---

# 数据漂移监控：何时不应再相信校准概率

## 学习目标

读完后，你能区分协变量漂移、标签漂移和概念漂移；从经验类别分布推导 PSI 与总变差距离；实现能显式报告新类别的输入漂移检查；解释告警为何只触发人工审查；并用重放证书发现被篡改的漂移结论。

## 从一个计算问题开始

一个垃圾邮件模型上月经过验证集再校准：预测 $0.8$ 的邮件大约八成是真垃圾。这个月，系统接入了新的发件人来源，词汇中突然出现大量 `invoice`。即使模型代码、阈值和校准器参数完全不变，过去“0.8”的频率承诺也未必仍适用。

监控先回答一个更窄的问题：**当前输入分布是否明显不同于参考期？** 它不能仅凭输入说明标签政策为何改变、攻击者做了什么，或模型是否应自动重训。

## 三种容易混淆的变化

设特征为 $X$、标签为 $Y$。

| 类型 | 改变了什么 | 仅看输入分布能否发现 |
| --- | --- | --- |
| 协变量漂移 | $P(X)$ 变化，例如新词来源增多 | 有时可以 |
| 标签漂移 | $P(Y)$ 变化，例如垃圾比例变化 | 需要及时标签或代理信号 |
| 概念漂移 | $P(Y\mid X)$ 变化，例如同一词对标签的含义变化 | 通常不能只靠 $P(X)$ |

因此，输入漂移报告是风险信号，而不是模型错误的判决书。它尤其无法检测“词分布没变，但人工标注规则改变”的概念漂移。

## 从类别频率到 PSI

在参考期和当前期分别统计类别 $j$ 的频率。为让新类别也有有限对数，将每个并集类别加入一个很小的平滑量 $\varepsilon>0$：

$$
p_j=\frac{n_j^{(ref)}+\varepsilon}{n^{(ref)}+m\varepsilon},\qquad
q_j=\frac{n_j^{(cur)}+\varepsilon}{n^{(cur)}+m\varepsilon}.
$$

其中 $m$ 是两个时期类别的并集数。Population Stability Index 定义为

$$
\mathrm{PSI}(p,q)=\sum_j(q_j-p_j)\log\frac{q_j}{p_j}.
$$

它对调换 $p,q$ 是对称的，且每一项在两频率相等时为零。PSI 的数值会受分箱、样本量、平滑和业务风险影响；阈值不是自然常数，必须写入报告并经人工审查。

总变差距离提供另一种更直观的量：

$$
\mathrm{TV}(p,q)=\frac12\sum_j|p_j-q_j|.
$$

它位于 $[0,1]$，可理解为两个分类分布可区分程度的一种上界刻画。PSI 与 TV 都只描述观察到的输入分布差异，不衡量公平性、因果机制或预测性能。

## 可运行实验：新类别不能被静默丢弃

```python
from projects.naive_bayes_spam.drift_monitoring import (
    categorical_drift_certificate,
    categorical_drift_report,
)

reference = ["ham"] * 50 + ["prize"] * 50
current = ["ham"] * 80 + ["prize"] * 10 + ["invoice"] * 10
report = categorical_drift_report(reference, current, psi_threshold=0.1)

print(report["psi"], report["total_variation"], report["needs_review"])
print(categorical_drift_certificate(reference, current, report))
```

运行：

```bash
python -m unittest projects.naive_bayes_spam.test_drift_monitoring
```

报告的类别取两期并集，故 `invoice` 显示参考计数为 0、当前计数为 10，而不是被过滤掉。平滑避免 $\log 0$；它并不表示参考期真的观察过该类别。证书从原始两期数据、平滑量和阈值独立重建整份报告，所以改写 `needs_review`、计数或距离都会被拒绝。

## 同一距离不等于同样稳定

点估计不会自动告诉我们样本量是否足够。两组窗口若同为 $80\%/20\%$ 对 $20\%/80\%$，PSI 与 TV 几乎相同；小窗口的重采样区间却更宽。下面的报告冻结初始类别并逐条重抽，只在“类别观测近似独立同分布”的教学假设下描述有限样本波动：

```python
from projects.naive_bayes_spam.categorical_drift_bootstrap import categorical_drift_bootstrap_report

small = categorical_drift_bootstrap_report(["ham"] * 8 + ["spam"] * 2, ["ham"] * 2 + ["spam"] * 8, repeats=200, seed=11)
large = categorical_drift_bootstrap_report(["ham"] * 800 + ["spam"] * 200, ["ham"] * 200 + ["spam"] * 800, repeats=200, seed=11)
print(small["psi_percentile_interval"], large["psi_percentile_interval"])
```

证书重放点距离、类别宇宙、样本量、种子和区间；区间不是显著性、因果原因或自动重训的证明。时间、簇或纵向相关会使逐条重抽低估共同波动，应改用[时间块](/probability-ml/block-bootstrap-calibration)、[簇级](/probability-ml/cluster-bootstrap-calibration)或[配对纵向](/probability-ml/time-stratified-cluster-bootstrap)设计。

## 告警后的决策边界

`needs_review` 只触发人工检查数据管道、来源、标签延迟、带标签性能与业务风险。它绝不等于 `retrain()`：新来源可能合法，重训也可能引入泄漏或遗忘。

## 正确性、边界与反例

当两期类别计数相同，平滑后的 $p_j=q_j$，PSI 和 TV 都为零；实现测试此不变量。任意出现新类别时，正平滑保证每个份额为正，报告仍完整且两侧份额和为一。

反例：词频相同但 `invoice` 的标签含义改变时，$P(X)$ 不变而 $P(Y\mid X)$ 变了；PSI/TV 仍可能很小，必须依赖延迟标签与性能审计。

## 常见误区

- **“PSI 超阈值就证明失效。”** 错；它只是复查触发器。
- **“PSI 小或两次相等，就没有问题。”** 错；前者遗漏概念漂移，后者遗漏抽样波动。
- **“零频率或固定阈值足够。”** 错；前者使对数无定义，后者依赖样本量和业务风险。

## 练习

1. **基础题**：若两期只有两个类别且频率均为 $(0.7,0.3)$，计算 PSI 与 TV。
2. **推导题**：说明 $q_j=p_j$ 时 PSI 的该项为何为零；解释为何新类别需要正平滑。
3. **编码题**：为报告增加最显著的三个 PSI 分量，但必须保留全部类别、并在计数相同的输入上测试排序稳定性。
4. **开放题**：为一个有标签延迟的一周滚动监控设计参考窗口、当前窗口和人工审查清单；分别指出哪些信号能支持协变量、标签和概念漂移的判断。

## 练习答案提示

1. 两个有限求和的每项都为零。
2. 差为零、比值为一；平滑只让零频率可计算。
3. 稳定排序但保留全部类别，否则改变份额与证书。
4. 冻结时间窗口与数据/标注版本；无标签时不能断言概念漂移。

## 延伸

[概率再校准](/probability-ml/recalibration)说明校准器只能在相近验证分布上解释概率；[概率校准与可靠性曲线](/probability-ml/calibration-reliability)提供带标签时的频率审计。下一步可把同一“可信输出”思路带到数值线性代数：残差小为何仍不足以保证解可靠。
