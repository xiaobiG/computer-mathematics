---
title: 概率校准与可靠性曲线：0.8 到底意味着什么
description: 从条件频率定义模型校准，推导 Brier 分数与可靠性分箱，并为朴素贝叶斯分类器实现可复核的概率评估。
courseLevel: "2–3（统计推断、模型评估与工程实验）"
prerequisites: "条件概率、期望、二分类与朴素贝叶斯"
estimatedMinutes: 55
experiment: "为垃圾邮件分类器计算 Brier 分数并生成可靠性分箱报告"
---

# 概率校准与可靠性曲线：0.8 到底意味着什么

## 学习目标

读完后，你能区分分类正确与概率可信；写出二分类校准的条件频率定义；计算 Brier 分数；实现带 Wilson 区间的可靠性分箱；并解释为什么小样本、数据漂移和在测试集上调参会让一张“漂亮校准图”失去意义。

## 从一个计算问题开始

两个垃圾邮件过滤器都把 100 封邮件判对了 90 封。A 对每封判为垃圾的邮件都报 $0.99$，B 都报 $0.60$。仅有准确率时，它们并列；若系统要按概率决定“自动隔离”还是“交给人工”，两者显然不同。

概率预测 $p_i$ 的承诺是：在许多同样报出 $0.8$ 的样本里，约 $80\%$ 应为正类。它不是“这一次一定有八成把握”的心理感受，而是一个可由重复样本审查的频率主张。

## 严格定义：条件频率应匹配预测值

设 $Y\in\{0,1\}$ 是真实标签，模型对特征 $X$ 输出 $S=s(X)\in[0,1]$。理想校准满足

$$P(Y=1\mid S=q)=q.$$

连续分数通常不会恰好重复，实践中把区间 $B_k=[k/K,(k+1)/K)$ 作为近似。第 $k$ 个非空箱的平均预测与经验正例率为

$$\bar p_k=\frac1{n_k}\sum_{i:S_i\in B_k}S_i,\qquad
\bar y_k=\frac1{n_k}\sum_{i:S_i\in B_k}Y_i.$$

可靠性图以 $\bar p_k$ 为横轴、$\bar y_k$ 为纵轴；点落在 $y=x$ 附近表示该箱的预测和观测相符。它是诊断图，不是证明：每个箱的 $n_k$ 与不确定性必须一并报告。

对第 $k$ 箱的正例数 $r_k$，Wilson 区间避免了小样本下正态近似的负下界或超过 1 的上界。令 $\hat p=r_k/n_k$，正态临界值为 $z$，则

$$
\frac{\hat p+z^2/(2n_k)\;\pm\;z\sqrt{\bigl(\hat p(1-\hat p)+z^2/(4n_k)\bigr)/n_k}}{1+z^2/n_k}.
$$

默认 $z=1.96$ 对应常用的约 95% 报告区间；它量化的是给定箱内观测频率的抽样不确定性，不能验证独立性、代表性或模型本身正确。

## Brier 分数：把概率误差变成一个数

二分类的 Brier 分数是均方概率误差：

$$\operatorname{BS}=\frac1n\sum_{i=1}^n(p_i-y_i)^2.$$

因为 $p_i,y_i\in[0,1]$，它位于 $[0,1]$，越小越好。对于同一个真实正例，报 $0.99$ 的损失是 $(0.99-1)^2$，报 $0.60$ 的损失是 $(0.60-1)^2$；它会奖励既正确又诚实的置信度。它同时反映校准和区分能力，不能单独诊断究竟是哪一项出了问题，所以必须和可靠性图、混淆矩阵一起看。

## 从朴素贝叶斯的对数分数推导后验

教学分类器先计算两个未归一化对数分数 $\ell_1,\ell_0$。把指数化并归一化：

$$P(Y=1\mid x)=\frac{e^{\ell_1}}{e^{\ell_1}+e^{\ell_0}}
=\frac1{1+e^{-(\ell_1-\ell_0)}}.$$

最后一式只计算差值 $d=\ell_1-\ell_0$。当 $d\ge0$，计算 $1/(1+e^{-d})$；当 $d<0$，计算 $e^d/(1+e^d)$。两种写法都避免直接指数化两个极小对数分数而造成下溢。

## 可运行实验：生成可靠性报告

项目已实现 `predict_proba`、`classification_metrics` 和 `reliability_bins`：

```python
from projects.naive_bayes_spam.main import NaiveBayesSpam, classification_metrics, reliability_bins

train = [
    ("win cash prize now", True), ("claim free prize", True),
    ("meeting notes attached", False), ("project meeting tomorrow", False),
]
test = [("cash prize", True), ("meeting notes", False)]
model = NaiveBayesSpam().fit(train)

print(classification_metrics(model, test))
for row in reliability_bins(model, test, bins=4):
    print(row["mean_prediction"], row["positive_rate"], row["wilson_low"], row["wilson_high"])
```

运行全部测试：

```bash
python -m unittest projects.naive_bayes_spam.test_main
```

分箱算法对每个样本计算一次概率，再以 `min(int(p * K), K - 1)` 放入箱。`p=1` 必须进入最后一箱；空箱必须省略，不能伪造为零正例。每个非空箱同时保留 `positive_count` 和 Wilson 上下界；`n=1` 也会返回合法区间，而非假装估计已经稳定。时间复杂度为 $O(n\cdot d+K)$，其中 $d$ 是文本 token 数。

## 正确性与可验证边界

`predict_proba` 的两支计算都代数等价于 sigmoid，故在有限指数可表示范围内返回 $[0,1]$ 内的归一化后验。可靠性分箱逐样本恰好加入一个箱，非空箱的计数之和必为评估样本数；Wilson 公式只接受 $0\le r\le n$ 和正的有限 $z$，并将边界截在 $[0,1]$。项目测试显式检验计数守恒、区间包含观察到的正例率、$n=1$ 边界和非法输入的拒绝。

但是，朴素贝叶斯的“后验”依赖条件独立和训练分布不变。词语相关、类别比例变化或垃圾邮件策略变化都会使高分不再对应高频率。校准应在独立验证集上拟合和检查；最终测试集只用于一次报告。

## 常见误区

- **“准确率高就校准。”** 错。只报 0 或 1 的分类器可能准确却过度自信。
- **“一张靠近对角线的图就证明校准。”** 错。每箱只有几个样本时，随机波动足以画出假象。
- **“Brier 小就没有偏差。”** 错。它混合了校准与区分，需查看分箱残差。
- **“用测试集反复选择分箱数或温度仍是测试。”** 错。那已把测试信息泄漏进模型选择。

## 练习

1. **基础题**：对真实标签 $1$，分别计算预测 $0.5$、$0.8$、$0.99$ 的 Brier 单样本损失。
2. **推导题**：从 $e^{\ell_1}/(e^{\ell_1}+e^{\ell_0})$ 推导稳定的 sigmoid 差值公式。
3. **编码题**：把 Wilson 区间改成可配置覆盖水平，并为极小箱数与边界正例数补齐测试。
4. **开放题**：某模型在训练后六个月出现校准恶化。设计监控指标、再校准触发规则与不应自动采取的高风险动作。

## 练习答案提示

1. Brier 单样本损失为 $(p-y)^2$，所以三项分别为 $0.25,0.04,0.0001$；这只测概率平方误差，不是分类准确率。
2. 提取共同的最大 logit 可避免直接计算巨大指数；两边同除以 $e^{\ell_0}$ 或使用符号分支，得到数值稳定的 sigmoid。
3. 从所需覆盖水平取得对应的 $z$ 值，并保持 $0\le r\le n$、`total > 0` 的输入契约；$n=1$ 是重要边界，空箱应省略而不是给伪区间。
4. 监控分箱偏差、Brier/对数损失、样本量和输入/标签漂移；触发后先人工审计数据与风险，不能仅凭自动再校准就改变高风险决策。

## 延伸

[贝叶斯更新](/probability-ml/bayes)说明后验从何而来；[置信区间与抽样误差](/probability-ml/confidence-intervals-sampling)说明为什么要报告分箱样本量；[垃圾邮件分类器项目](/projects/naive-bayes-spam)将三者连为可运行实验。下一步可以研究验证集上的 Platt scaling、isotonic regression 与分布漂移监控，但必须避免把校准器当作安全或公平性的替代证明。
