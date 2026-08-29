---
title: 条件概率与贝叶斯更新：证据为什么不等于结论
description: 从全概率公式推导后验概率，理解低基率、朴素贝叶斯与校准边界。
---

# 条件概率与贝叶斯更新：证据为什么不等于结论

## 文章元信息

- **建议阅读层级**：1–3 · 核心概念、推导与工程应用
- **前置知识**：集合、乘法法则、百分比
- **预计学习时间**：55 分钟
- **配套实验**：下一阶段的垃圾邮件贝叶斯分类器与校准评估

## 从一个计算问题开始

过滤器发现某个敏感词后报告“像垃圾邮件”。这个词在垃圾邮件中出现率为 $90\%$，在正常邮件中也有 $5\%$ 出现率；而垃圾邮件只占全部邮件的 $1\%$。报告为阳性后，邮件究竟有多大概率是垃圾？仅看 $90\%$ 会严重高估结论。

## 直觉模型

把一万封邮件分桶：约 100 封垃圾邮件中有 90 封带词；9,900 封正常邮件中约 495 封也带词。因此带词的 585 封中，垃圾邮件只有 90 封。观察到的证据必须和“这种证据总体有多常见”一起解释。

## 严格定义与推导

对事件 $A,B$ 且 $P(B)>0$，条件概率定义为

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}.$$

乘法法则给出 $P(A\cap B)=P(B\mid A)P(A)$。若 $A$ 与 $\neg A$ 构成完备划分，全概率公式给出

$$P(B)=P(B\mid A)P(A)+P(B\mid\neg A)P(\neg A).$$

代入便得到贝叶斯公式：

$$P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B\mid A)P(A)+P(B\mid\neg A)P(\neg A)}.$$

此例后验为 $0.9\times0.01/(0.9\times0.01+0.05\times0.99)\approx15.4\%$。先验、似然与证据概率分别限制了后验，三者不可互换。

## 算法实现与复杂度

```python
def posterior(prior, sensitivity, false_positive):
    """Return P(A|B) for a binary event and one binary observation."""
    if not all(0 <= value <= 1 for value in (prior, sensitivity, false_positive)):
        raise ValueError("probabilities must lie in [0, 1]")
    evidence = sensitivity * prior + false_positive * (1 - prior)
    if evidence == 0:
        raise ValueError("observation has zero probability")
    return sensitivity * prior / evidence

assert round(posterior(0.01, 0.90, 0.05), 3) == 0.154
```

单个证据的计算为 $O(1)$。朴素贝叶斯对 $d$ 个特征在对数域累加 $\log P(x_i\mid y)$，预测成本为 $O(d\cdot\text{类别数})$；使用对数避免许多小概率连乘下溢。

## 正确性与工程边界

代码逐项实现全概率分母与贝叶斯分子，因此在输入是合法概率且证据概率非零时恰好返回定义的后验。朴素贝叶斯假设“给定类别后特征条件独立”，词语高度相关时该假设会重复计数证据。模型分数还必须校准：预测 0.8 的一组样本不一定真的有约 80% 为正类。

## 常见误区

- 将 $P(A\mid B)$ 与 $P(B\mid A)$ 混为一谈，即“逆概率谬误”。
- 忽略先验，导致低基率事件的假阳性被误判为强证据。
- 把模型输出当作客观频率；数据漂移会使后验和校准失效。

## 练习

1. **基础**：先验改为 20%，计算新的后验并与 15.4% 比较。
2. **推导**：从 $P(A\cap B)=P(B\cap A)$ 独立推导贝叶斯公式。
3. **编码**：为 `posterior` 添加零证据与非法概率的测试。
4. **开放**：设计一个医疗筛查例子，说明改变阈值如何在假阳性和假阴性间权衡。

## 延伸与下一步

[最大似然](/probability-ml/maximum-likelihood)解释如何从训练数据估计似然参数；[期望与方差](/probability-ml/expectation-variance)则描述概率模型的平均行为与不确定性。
