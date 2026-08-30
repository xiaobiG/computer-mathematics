---
title: 交叉熵与 KL 散度：模型的概率承诺要付多少代价
description: 从编码长度和负对数似然推导交叉熵与 KL 散度，并用有限分布验证分解恒等式与零概率边界。
courseLevel: "2–3（统计建模与机器学习）"
prerequisites: "概率分布、对数、期望与最大似然"
estimatedMinutes: 60
experiment: "计算有限分布的熵、交叉熵、KL 散度与分解残差"
---

# 交叉熵与 KL 散度：模型的概率承诺要付多少代价

## 学习目标

读完后，你能说明熵、交叉熵和 KL 散度分别测量什么；从期望负对数概率推导三者关系；解释为什么给真实可能事件分配零概率会导致无穷损失；并能用分解恒等式审计分类模型的概率分布。

## 从一次错误但自信的预测开始

两个垃圾邮件模型都预测“垃圾邮件”的概率为 $0.9$，其中一个样本实际是正常邮件。准确率只把这件事算作一次错误；概率模型却还要为“把真实事件说成几乎不可能”付出多大代价。对数损失会把这种过度自信显式放大，这正是交叉熵在分类训练中比单纯 0/1 错误更有信息的原因。

## 从编码与似然推导

真实分布记为 $P$，模型分布记为 $Q$。若事件 $x$ 发生，按模型 $Q$ 编码它的理想长度为 $-\log Q(x)$（以自然对数计，单位为 nat）。按真实分布取平均得到**交叉熵**：

$$H(P,Q)=-\sum_xP(x)\log Q(x).$$

若模型恰好等于真实分布，得到 $P$ 自己的不确定性，即熵：

$$H(P)=-\sum_xP(x)\log P(x).$$

两式相减并合并对数：

$$H(P,Q)-H(P)=\sum_xP(x)\log\frac{P(x)}{Q(x)}=D_{KL}(P\|Q).$$

于是

$$H(P,Q)=H(P)+D_{KL}(P\|Q).$$

KL 散度不是对称距离：交换 $P,Q$ 一般改变结果，也不满足三角不等式。Gibbs 不等式保证 $D_{KL}(P\|Q)\ge0$，且在相同分布时为零。因此交叉熵最小化等价于在真实分布固定时最小化 KL。

对独热标签 $y\in\{0,1\}$，上式退化为二元交叉熵 $-[y\log q+(1-y)\log(1-q)]$，正是[逻辑回归](/probability-ml/generative-discriminative-logistic)中的负对数似然。

## 算法实现：用恒等式检查计算

```python
from projects.naive_bayes_spam.distribution_metrics import (
    information_report,
    information_report_certificate,
    categorical_cross_entropy_from_logits,
    logit_cross_entropy_certificate,
    logit_cross_entropy_report,
)

actual = {"spam": 0.2, "ham": 0.8}
predicted = {"spam": 0.3, "ham": 0.7}
report = information_report(actual, predicted)

assert report["kl_divergence"] > 0.0
assert abs(report["cross_entropy"] - report["entropy"] - report["kl_divergence"]) < 1e-12
assert information_report_certificate(actual, predicted, report)["valid"]

# 概率模型通常输出未归一化分数（logits），不应先直接求 exp(1000)。
logit_report = logit_cross_entropy_report([1000.0, -1000.0], target_index=1)
assert categorical_cross_entropy_from_logits([1000.0, -1000.0], 1) == 2000.0
assert logit_cross_entropy_certificate([1000.0, -1000.0], 1, logit_report)["valid"]
```

运行 `python -m unittest projects.naive_bayes_spam.test_distribution_metrics`。实现要求两张表具有相同的结果集合、每格非负有限且各自和为一。`information_report` 返回熵、交叉熵、KL 和分解残差；`information_report_certificate` 从两张分布重新计算全部字段，能拒绝被篡改的 KL 或残差，并将有限分解与无穷损失分开审计。后者应接近零，是比“函数返回了一个数”更强的计算证据。

分类训练通常不先构造概率表，而是从 logits $z_1,\ldots,z_k$ 出发。直接计算 $e^{1000}$ 会溢出，所以实验的 `log_softmax` 使用

$$
\log\sum_j e^{z_j}=z_{\max}+\log\sum_j e^{z_j-z_{\max}}.
$$

减去同一个 $z_{\max}$ 不改变 softmax 的概率比，而所有指数项至多为 $1$。`categorical_cross_entropy_from_logits` 因而直接返回 $-\log\operatorname{softmax}(z)_y$；`logit_cross_entropy_certificate` 会重算对数概率、目标损失与 $\log\sum_j e^{\log p_j}=0$ 的归一化证据。对 $k$ 个类别，分布指标和该稳定实现都是 $O(k)$ 时间与 $O(1)$ 额外空间（不计输入/报告）。

## 零概率、稳定性与工程边界

若某个 $P(x)>0$ 而模型给 $Q(x)=0$，则 $-\log Q(x)=+\infty$，交叉熵和 $D_{KL}(P\|Q)$ 都应是无穷。这不是异常值修补的借口，而是“模型宣称真实事件不可能”的数学后果。训练中通常以平滑、softmax/logits 的稳定实现或最小概率下界避免有限数据把可发生事件硬置零；报告时仍须说明这些近似。

- **KL 不对称**：$D_{KL}(P\|Q)$ 惩罚遗漏 $P$ 的高概率区域；反向 KL 的行为不同，不能随意互换。
- **经验分布不是总体真相**：测试集交叉熵是样本估计，会随数据漂移、抽样误差和标签噪声变化。
- **低损失不等于公平或安全**：它衡量概率拟合，不能替代分组审计、对抗鲁棒性或业务代价分析。
- **数值实现**：不要先算极小概率再取对数；生产训练直接用稳定的 log-softmax / log-sum-exp。极端 logits 的损失可以很大但仍应是有限数，例如 $[1000,-1000]$ 对第二类的损失为 $2000$，不是溢出异常。

## 练习

1. **基础**：对 $P=(0.5,0.5)$、$Q=(0.9,0.1)$ 计算交叉熵和 KL（可保留对数形式）。
2. **推导**：由 $H(P,Q)-H(P)$ 逐步推导 KL 公式，并说明 $P=Q$ 时为何为零。
3. **编码**：篡改一份有限 `information_report` 的 KL 或残差，确认其证书拒绝；再篡改极端 logits 报告的损失，确认 log-sum-exp 证书拒绝，并测试有正概率事件被预测为零时返回无穷。
4. **开放**：比较两套垃圾邮件模型的准确率、交叉熵和可靠性曲线；构造一个准确率更高但交叉熵更差的情形并解释原因。

## 练习答案提示

1. 交叉熵是 $-0.5\log0.9-0.5\log0.1$；KL 再减去 $H(P)=\log2$，保留符号可避免小数舍入。
2. 代入定义后 $-\sum P\log Q+\sum P\log P=\sum P\log(P/Q)$；当 $P=Q$ 每项对数为 0。
3. bit 单位用自然对数结果除以 $\log2$；证书应重新计算全部字段并区分有限残差和无穷损失。logits 先减去最大值再求指数，不能直接计算 $e^{1000}$。若 $P(x)>0,Q(x)=0$ 直接返回无穷，不能用静默截断掩盖数学事件。
4. 准确率只看最终类别，交叉熵还惩罚高置信错误；可靠性曲线检查分桶概率是否兑现，三者需要在相同留出集和分组上报告。

## 延伸

[最大似然](/probability-ml/maximum-likelihood)说明为何训练最小化负对数似然；[概率校准与可靠性曲线](/probability-ml/calibration-reliability)审查概率承诺能否兑现；[蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)则会在更复杂分布上估计期望。
