---
courseLevel: "1–2（核心概念与推导）"
prerequisites: "期望、方差、正态分布与抽样"
estimatedMinutes: 60
experiment: "用可复现模拟检验 95% 置信区间的长期覆盖率，并比较 bootstrap"
title: 抽样误差、置信区间与覆盖率
description: 从样本均值的抽样分布出发，推导置信区间，理解覆盖率、bootstrap 与常见误读。
---

# 抽样误差、置信区间与覆盖率

> 一个样本均值不是总体均值的“答案”，而是一次带随机性的测量。置信区间把这层随机性明确写进结论，并要求我们用重复抽样的视角解释它。

## 学习目标

完成本课后，你可以：

- 区分总体参数、统计量、抽样分布、标准差与标准误；
- 从独立样本的方差推导样本均值的标准误；
- 正确构造并解释均值的 95% 置信区间；
- 写出 bootstrap 百分位区间，并用模拟验证覆盖率；
- 识别独立性、选择偏差、小样本与多重比较造成的失效边界。

## 从一次 A/B 测试的“精确数字”开始

实验组 800 名用户的平均停留时长比对照组高 0.8 分钟。这个差值看上去很具体，却仍会随下次抽样而变化：换一批用户，可能是 0.2，也可能是 1.4。

要回答“效果有多不确定”，不能只看一个点估计 \(\hat\theta\)，还要研究它在重复抽样中的分布。置信区间表达的是：按预先固定的规则反复采样并构造区间，这些区间覆盖真参数的频率有多高。

## 四个对象：不要把它们混在一起

设总体随机变量为 \(X\)，总体均值 \(\mu=\mathbb E[X]\)，方差 \(\sigma^2\)。抽到独立样本 \(X_1,\ldots,X_n\) 后，样本均值

\[
\bar X=\frac1n\sum_{i=1}^n X_i
\]

是一个随机变量；已观察到的数 \(\bar x\) 才是一次实验的结果。

- **总体标准差 \(\sigma\)**：单个用户或单次观测的波动。
- **标准误 \(\operatorname{SE}(\bar X)\)**：统计量 \(\bar X\) 在重复实验中的波动。
- **点估计 \(\bar x\)**：本次实验给出的中心位置。
- **置信区间**：由数据和固定规则生成的随机区间。

将“样本标准差很大”直接说成“均值估计很不准”是错误的；只要样本量足够，均值的标准误仍会缩小。

## 从方差线性性推导标准误

独立同分布时，\(\mathbb E[\bar X]=\mu\)。同时

\[
\begin{aligned}
\operatorname{Var}(\bar X)
&=\operatorname{Var}\left(\frac1n\sum_{i=1}^nX_i\right)\\
&=\frac1{n^2}\sum_{i=1}^n\operatorname{Var}(X_i)\\
&=\frac{\sigma^2}{n}.
\end{aligned}
\]

第二步把交叉协方差设为零，恰恰依赖独立性。因此

\[
\operatorname{SE}(\bar X)=\frac{\sigma}{\sqrt n}.
\]

样本量翻四倍，标准误才减半。这是“多收集一点数据”常常效果有限的数学原因。若用户按会话、地区或时间簇相关，交叉协方差不为零，实际标准误会大于这个公式；此时不能把日志行数当成独立样本量。

## 正态近似与均值置信区间

当总体正态，或样本足够大且中心极限定理适用时，标准化统计量近似服从标准正态：

\[
\frac{\bar X-\mu}{\sigma/\sqrt n}\approx N(0,1).
\]

标准正态落入 \([-1.96,1.96]\) 的概率约为 95%。移项得到已知 \(\sigma\) 的近似 95% 区间：

\[
\bar x \pm 1.96\frac{\sigma}{\sqrt n}.
\]

现实中 \(\sigma\) 通常未知。用样本标准差 \(s\) 代替它，小样本、总体近似正态时应使用 Student \(t\) 分布的临界值：

\[
\bar x \pm t_{0.975,n-1}\frac{s}{\sqrt n}.
\]

\(n\) 增大后 \(t\) 临界值趋近 1.96。这个区间针对的是**总体均值**，不是“95% 的单个用户会落在这里”；后者需要预测区间，宽度通常大得多。

## 95% 到底是什么意思

在频率学派表述里，参数 \(\mu\) 是固定的，区间端点因样本不同而随机。若用同一规则无限次重复“抽样—构造区间”，约 95% 的区间会包含 \(\mu\)。

一次实验结束后，区间已经产生；它要么包含 \(\mu\)，要么不包含。说“\(\mu\) 有 95% 概率落在这个已计算区间内”不是该方法的严格解释。若需要直接对参数表达概率，需要明确先验并进行贝叶斯后验区间分析。

覆盖率也不是质量担保：规则在模型、抽样与独立性假设成立时才有目标覆盖率。非随机样本再宽的区间也无法修复系统性偏差。

## Bootstrap：用数据近似重复抽样

均值之外的统计量（中位数、分位数、复杂模型分数）可能没有方便的标准误公式。非参数 bootstrap 的思想是把观测样本当作对未知分布的近似：

1. 从原始样本中**有放回**抽取 \(n\) 个值；
2. 计算统计量 \(T^*\)；
3. 重复很多次，得到 \(T^*\) 的经验分布；
4. 取 2.5% 和 97.5% 分位数作为百分位区间。

它不是魔法：样本太小、分布极重尾、统计量不光滑或数据有时间依赖时，bootstrap 可能覆盖不准。重采样单位也必须匹配数据生成过程：用户级实验应重采样用户，不应把同一用户的页面浏览拆开重采样。

## 可运行实验：长期覆盖率而非单次直觉

以下代码模拟许多次实验。为避免假装有完整 \(t\) 分布库，示例用较大样本的 1.96 正态近似；它的目的正是检验“区间规则的长期频率”这一解释。

```python
from math import sqrt
from random import Random


def mean(values):
    return sum(values) / len(values)


def sample_sd(values):
    if len(values) < 2:
        raise ValueError("至少需要两个样本")
    m = mean(values)
    return sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def normal_mean_ci(values, z=1.96):
    """大样本均值的近似置信区间。"""
    m = mean(values)
    margin = z * sample_sd(values) / sqrt(len(values))
    return m - margin, m + margin


def bootstrap_percentile_ci(values, repeats=4000, seed=0):
    if len(values) < 2 or repeats < 100:
        raise ValueError("样本至少为 2，重复次数至少为 100")
    rng = Random(seed)
    n = len(values)
    estimates = sorted(
        mean([values[rng.randrange(n)] for _ in range(n)])
        for _ in range(repeats)
    )
    return estimates[int(0.025 * repeats)], estimates[int(0.975 * repeats)]


def coverage_experiment(true_mean=10.0, sd=4.0, n=80, trials=1000, seed=7):
    rng = Random(seed)
    covered = 0
    for _ in range(trials):
        sample = [rng.gauss(true_mean, sd) for _ in range(n)]
        low, high = normal_mean_ci(sample)
        covered += low <= true_mean <= high
    return covered / trials


print(round(coverage_experiment(), 3))  # 通常接近 0.95，不会恰好等于它
```

把 `n` 改为 8，并把生成分布改成少数极端值很大的混合分布，观察覆盖率如何偏离 0.95。模拟不是证明，但它能让统计假设的后果变得可见。

## 两组差异与实验设计

若实验组和对照组独立，均值差 \(\hat\Delta=\bar X_T-\bar X_C\) 的标准误近似为

\[
\operatorname{SE}(\hat\Delta)
=\sqrt{\frac{s_T^2}{n_T}+\frac{s_C^2}{n_C}}.
\]

区间覆盖 0 并不等价于“没有业务价值”；它说明现有数据尚不能以该置信水平排除零差异。应同时报告效应量、区间、样本设计和业务最小可接受效果。若观测数据不是随机分组，区间还不解决混杂问题：它量化抽样波动，不会自动消除偏差。

## 常见误区与工程边界

- **把 CI 当作数据范围。** 均值的 CI 不是用户值的 95% 区间。
- **只增大日志行数。** 自相关、重复用户和簇抽样降低有效样本量；应按独立实验单位分析。
- **先看数据再决定何时停止。** 反复查看并在“显著”时停止，会提高假阳性率；需要预先设计或使用序贯方法。
- **忘记选择偏差。** 从“愿意填写问卷的人”得到的精确 CI，可能只精确描述这群人。
- **将 bootstrap 用于一切。** 有依赖时使用 block bootstrap 或分层重采样；极端小样本应承认信息不足。

## 练习

1. 在独立同分布假设下，完整推导 \(\operatorname{Var}(\bar X)=\sigma^2/n\)，并指出哪一步会被相关样本破坏。
2. 假设 \(s=12,n=144\)，用 1.96 近似计算均值的 95% 区间半宽。若半宽希望减半，样本量要变为多少？
3. 修改 `coverage_experiment`，比较 \(n=10,30,100\) 的经验覆盖率；说明为什么每次运行不必恰好为 0.95。
4. 为“每位用户有多次点击”的 A/B 测试设计重采样单位，并解释逐点击 bootstrap 为什么会过度自信。
5. 找一则包含“误差范围”的调查报道：写清它的目标总体、抽样框、区间对象与可能的非抽样误差。

## 下一步

置信区间与 [假设检验与 p 值](/probability-ml/hypothesis-testing) 使用相同的抽样分布视角；接下来将它们接到分类器的可靠性曲线与校准评估上，区分“预测是否准确”与“预测概率是否可信”。
