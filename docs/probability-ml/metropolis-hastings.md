---
title: Metropolis–Hastings：用拒绝采样修正马尔可夫链
description: 从详细平衡推导 MH 接受率，解释 burn-in、相关样本和混合诊断，并用有限状态链验证长期频率。
courseLevel: 3
prerequisites: 条件概率、马尔可夫链直觉、蒙特卡洛、重要性采样
estimatedMinutes: 65
experiment: projects/naive_bayes_spam/metropolis_hastings.py
---

# Metropolis–Hastings：用拒绝采样修正马尔可夫链

## 学习目标

读完后，你能从详细平衡推出 Metropolis–Hastings 接受率；实现带非对称提议修正的有限状态链；区分“目标分布正确”与“有限步已经混合”；并以接受轨迹和长期频率审计采样。

## 从“无法直接采样后验”开始

很多贝叶斯模型的后验只知道成比例形式 $\pi(x)\propto p(x)p(D\mid x)$，归一化常数难算，因而不能直接从 $\pi$ 独立抽样。MCMC 不强求每步独立：它构造一条长期停留比例为目标分布的马尔可夫链。代价是样本相关、初值影响和混合诊断都成为结果的一部分。

## 定义与直觉

从当前状态 $x$ 先按提议分布 $q(y\mid x)$ 候选 $y$，再以概率 $\alpha(x,y)$ 接受；拒绝则留在 $x$。若希望 $\pi$ 是平稳分布，一个足够条件是每对状态满足详细平衡：

$$\pi(x)P(x\to y)=\pi(y)P(y\to x).$$

对 $x\ne y$，转移概率为 $P(x\to y)=q(y\mid x)\alpha(x,y)$。选择

$$\alpha(x,y)=\min\left(1,\frac{\pi(y)q(x\mid y)}{\pi(x)q(y\mid x)}\right)$$

即可使两边相等：若比值小于一，正向乘上该比值后恰好等于反向；若比值大于一则交换角色。比例中的归一化常数消掉，因此只要能算未归一化权重即可。

## 手算一个两状态链

令目标权重为 $\pi(0):\pi(1)=1:3$，提议总是在两个状态间切换。$0\to1$ 的比值为 3，故必接受；$1\to0$ 的比值为 $1/3$，只以三分之一概率接受。长期看状态 1 的频率趋向 $3/4$，而不是提议链本身的 $1/2$。接受/拒绝正是把容易提出的状态修正成正确驻留比例。

## 可运行实现

```python
from projects.naive_bayes_spam.metropolis_hastings import (
    detailed_balance_report,
    empirical_probabilities,
    metropolis_hastings,
    metropolis_hastings_trace_certificate,
)

target = {0: 1.0, 1: 3.0}
proposal = {0: {1: 1.0}, 1: {0: 1.0}}
samples, trace = metropolis_hastings(target, proposal, initial=0, steps=10_000, seed=2026)
print(empirical_probabilities(samples[500:]))  # state 1 接近 0.75
assert metropolis_hastings_trace_certificate(target, proposal, 0, samples, trace, seed=2026)

balance = detailed_balance_report(target, proposal)
assert abs(balance["kernel"][1][0] - 1 / 3) < 1e-12
assert abs(balance["kernel"][1][1] - 2 / 3) < 1e-12
assert balance["detailed_balance_holds"]
assert balance["certificate"]["valid"]
```

运行 `python -m unittest projects.naive_bayes_spam.test_metropolis_hastings`。实现允许未归一化目标权重与非对称提议，并显式计算 $q(x\mid y)/q(y\mid x)$；每轮记录候选、接受率和实际状态。`metropolis_hastings_trace_certificate` 从公开种子重放两次伪随机抽取，再独立计算 Hastings 比值并逐项核对轨迹。`detailed_balance_report` 则在小状态空间中显式构造包含拒绝自环的转移核，列出每一行和与 $\pi(x)P(x,y)$ 的双向流；它的证书从 $\pi,q$ 重新生成整张核，因此篡改任一转移概率会被拒绝。前者验证一段程序运行遵循实现契约，后者验证目标分布确为该有限核的平稳分布；两者都不证明链已经混合。测试还验证长期频率、非对称修正、提议行和为一、反向概率存在、初值合法和空样本边界。

有限状态、显式提议表的一步成本为 $O(d)$（$d$ 为当前候选数）；真实高维模型通常只计算局部对数密度差，不能把整个状态空间写成字典。

## 正确性与停止边界

详细平衡说明目标分布是平稳分布，却不说明链在第 1,000 步已接近平稳，也不保证从任意状态可达全部正概率状态。通常还需要不可约、非周期等条件。丢弃早期 `burn-in` 样本可能降低初值影响，但不是自动证明；抽稀 `thinning` 减少存储却通常不能免费增加有效样本数。

相关样本意味着 $N$ 个状态不等于 $N$ 个独立样本。应查看轨迹、多条不同初值链、接受率、自相关和有效样本量；单一链的均值稳定或接受率“好看”都不足以证明混合。

## 失败案例与常见误区

- **提议不连通**：若链永远到不了一个高权重区域，详细平衡再漂亮也无用。
- **提议步长太小**：接受率高但移动极慢；太大则多数候选被拒绝。两者都会降低有效样本量。
- **忽略非对称修正**：只用 $\pi(y)/\pi(x)$ 会让非对称提议收敛到错误分布。
- **把 MCMC 当独立采样**：置信区间必须考虑自相关，不能直接套 i.i.d. 公式。

## 练习

1. **基础**：验证两状态例子中 $\pi(0)P(0\to1)=\pi(1)P(1\to0)$。
2. **推导**：按接受率比值小于/大于一两种情形证明详细平衡。
3. **编码**：为轨迹计算接受率与滞后一自相关；比较不同随机种子；篡改 `detailed_balance_report` 的一个转移概率，确认其证书拒绝。
4. **开放**：为一个双峰目标设计局部随机游走提议，解释为何链会卡在一个峰，并提出平行回火或独立提议等改进方向。

## 练习答案提示

1. 写出两状态转移概率和目标权重，分别计算两侧乘积；应相等，且要注意自环概率也使每行和为一。
2. 接受率取两方向流量的较小者，分比值不小于/小于 1 两种情形代入即可证明详细平衡；这只给平稳性，不给混合速度。
3. 接受率为接受次数除提议次数；滞后一自相关需中心化相邻状态，多个种子只能提示诊断一致性，不能替代收敛证明。详细平衡证书必须重算包含拒绝自环的整张核，而不是只检查采样频率。
4. 局部提议跨越低密度谷的概率很小，链会长时间停在一峰；平行回火借高温链帮助跨峰，独立提议则需要足够覆盖两峰，二者都应报告 ESS 与多链诊断。

## 下一步

[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)解释独立样本与权重退化；[共轭先验与后验预测](/probability-ml/conjugate-priors-predictive)展示不需要 MCMC 的可解后验。继续学习 Gibbs sampling、Hamiltonian Monte Carlo、$\hat R$ 与有效样本量诊断。
