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

读完后，你能区分分类正确与概率可信；写出二分类校准的条件频率定义；计算 Brier 分数；实现可靠性分箱；并解释为什么小样本、数据漂移和在测试集上调参会让一张“漂亮校准图”失去意义。

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
from projects.naive_bayes_spam.main import (
    NaiveBayesSpam, classification_metrics, reliability_bins,
)

train = [
    ("win cash prize now", True), ("claim free prize", True),
    ("meeting notes attached", False), ("project meeting tomorrow", False),
]
test = [("cash prize", True), ("meeting notes", False)]
model = NaiveBayesSpam().fit(train)

print(classification_metrics(model, test))
for row in reliability_bins(model, test, bins=4):
    print(row)
```

运行全部测试：

```bash
python -m unittest projects.naive_bayes_spam.test_main
```

分箱算法对每个样本计算一次概率，再以 `min(int(p * K), K - 1)` 放入箱。`p=1` 必须进入最后一箱；空箱必须省略，不能伪造为零正例。时间复杂度为 $O(n\cdot d+K)$，其中 $d$ 是文本 token 数。

## 正确性与可验证边界

`predict_proba` 的两支计算都代数等价于 sigmoid，故在有限指数可表示范围内返回 $[0,1]$ 内的归一化后验。可靠性分箱逐样本恰好加入一个箱，非空箱的计数之和必为评估样本数；项目测试显式检验了这一守恒量以及非法箱数的拒绝。

但是，朴素贝叶斯的“后验”依赖条件独立和训练分布不变。词语相关、类别比例变化或垃圾邮件策略变化都会使高分不再对应高频率。校准应在独立验证集上拟合和检查；最终测试集只用于一次报告。

## 常见误区

- **“准确率高就校准。”** 错。只报 0 或 1 的分类器可能准确却过度自信。
- **“一张靠近对角线的图就证明校准。”** 错。每箱只有几个样本时，随机波动足以画出假象。
- **“Brier 小就没有偏差。”** 错。它混合了校准与区分，需查看分箱残差。
- **“用测试集反复选择分箱数或温度仍是测试。”** 错。那已把测试信息泄漏进模型选择。

## 练习

1. **基础题**：对真实标签 $1$，分别计算预测 $0.5$、$0.8$、$0.99$ 的 Brier 单样本损失。
2. **推导题**：从 $e^{\ell_1}/(e^{\ell_1}+e^{\ell_0})$ 推导稳定的 sigmoid 差值公式。
3. **编码题**：为 `reliability_bins` 增加每箱 Wilson 置信区间，并测试计数为 1 的边界。
4. **开放题**：某模型在训练后六个月出现校准恶化。设计监控指标、再校准触发规则与不应自动采取的高风险动作。

## 延伸

[贝叶斯更新](/probability-ml/bayes)说明后验从何而来；[置信区间与抽样误差](/probability-ml/confidence-intervals-sampling)说明为什么要报告分箱样本量；[垃圾邮件分类器项目](/projects/naive-bayes-spam)将三者连为可运行实验。下一步可以研究验证集上的 Platt scaling、isotonic regression 与分布漂移监控，但必须避免把校准器当作安全或公平性的替代证明。
