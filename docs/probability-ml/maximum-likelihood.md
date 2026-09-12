---
courseLevel: "2（推导与建模）"
prerequisites: "概率分布、对数与微分"
estimatedMinutes: 85
experiment: "实现伯努利 MLE 与拉普拉斯平滑"
title: 最大似然：从数据估计参数
description: 从伯努利计数推导 MLE、经验交叉熵与 KL 分解，并区分 MLE、MAP 和后验预测。
---

# 最大似然：从数据估计参数

## 文章元信息

- **建议阅读层级**：2–3 · 推导、优化与机器学习应用
- **前置知识**：[贝叶斯更新](/probability-ml/bayes)、导数、对数函数
- **预计学习时间**：85 分钟
- **配套实验**：垃圾邮件分类器的参数估计与校准评估

## 学习目标

读完后，你能把独立观测写成似然与对数似然；推导伯努利 MLE 的样本均值形式及边界情形；证明平均负对数似然等于经验交叉熵、与最优经验分布的差正是 KL 散度；区分 MLE、MAP 和后验预测；并说明先验、模型错设与数值下溢为何不能被“最大化”自动解决。

## 从一个计算问题开始

观察一枚硬币 10 次，其中 8 次正面。程序需要一个正面概率 $p$，应填 $0.5$、$0.8$ 还是别的数？最大似然不是问“参数本身的概率”，而是问：在已固定一个参数候选后，哪个候选最能解释已经看到的数据？

这个问题还有一个容易被掩盖的版本：训练里经常最小化交叉熵，为什么教材又在说最大化似然？下面会让这两个目标在同一条等式里相遇。

## 定义：数据概率与参数评分

固定观测 $x_1,\ldots,x_n$，将模型密度 $p(x_i\mid\theta)$ 看成参数 $\theta$ 的函数，称为似然：

$$L(\theta)=\prod_{i=1}^{n}p(x_i\mid\theta).$$

独立样本使概率相乘；单调的对数不改变最优点，并将连乘改为求和：

$$\ell(\theta)=\log L(\theta)=\sum_i\log p(x_i\mid\theta).$$

对固定 $\theta$，$p(x_i\mid\theta)$ 是模型分给观察的概率；把观察固定、让 $\theta$ 变化时，$L(\theta)$ 是未归一化评分，不是“参数为真的概率”。只有另加先验并归一化后，才得到参数的后验分布。

## 分步推导：伯努利 MLE 的驻点、边界与唯一性

若正面次数为 $h$、反面次数为 $t$，则

$$L(p)=p^h(1-p)^t,\qquad \ell(p)=h\log p+t\log(1-p).$$

对 $0<p<1$ 求导：

$$
\frac{d\ell}{dp}=\frac{h}{p}-\frac{t}{1-p}=0
\quad\Longrightarrow\quad \hat p=\frac{h}{h+t}.
$$

对混合样本 $h,t>0$，二阶导数

$$
\frac{d^2\ell}{dp^2}=-\frac h{p^2}-\frac t{(1-p)^2}<0
$$

严格为负，故样本均值是唯一内部最大点。若全为正面，$\ell(p)=n\log p$ 随 $p$ 增大，最大点在 $p=1$；若全为反面，则在 $p=0$。这两个边界不是实现错误，而是有限数据下 MLE 的真实结论。

## 同一个目标的训练语言：经验交叉熵与 KL

令经验正面频率为 $\hat q=h/n$。把对数似然除以样本数、再取负号：

$$
\begin{aligned}
-\frac1n\ell(p)
&=-\hat q\log p-(1-\hat q)\log(1-p)\\
&=H(\operatorname{Bern}(\hat q),\operatorname{Bern}(p)).
\end{aligned}
$$

所以“最大化总对数似然”等价于“最小化经验交叉熵”；两者不是两条相似的技巧，而是相差一个正比例和符号。再把交叉熵拆开：

$$
\begin{aligned}
H(\hat q,p)
&=-\hat q\log p-(1-\hat q)\log(1-p)\\
&=\underbrace{-\hat q\log\hat q-(1-\hat q)\log(1-\hat q)}_{H(\hat q)}
+\underbrace{\hat q\log\frac{\hat q}{p}
+(1-\hat q)\log\frac{1-\hat q}{1-p}}_{D_{\mathrm{KL}}(\hat q\Vert p)}.
\end{aligned}
$$

约定 $0\log0=0$。第一项只由已观察的数据决定；第二项非负，且在 $p=\hat q$ 时为零。因此这条 KL 分解既解释了 MLE 的最优性，也说明了它优化的对象：**模型分布到经验分布的距离**，不是对未知真实机制的直接证明。

对 8 正、2 反，平均负对数似然（单位：nat）为：

| 候选 $p$ | 平均负对数似然 | 相对 MLE 的额外损失 |
| ---: | ---: | ---: |
| $0.5$ | $0.6931$ | $0.1927$ |
| $0.8$（MLE） | $0.5004$ | $0$ |
| $0.9$ | $0.5448$ | $0.0444$ |

把表中的“额外损失”乘以 $n$，就是总对数似然相对于 MLE 少了多少；它也正是 $nD_{\mathrm{KL}}(\hat q\Vert p)$。这给训练损失提供了可手算的量纲：每条样本平均多付出的对数损失，而非模糊的“分数变差”。

## MLE、MAP 与后验预测回答三个问题

设先验为 $p\sim\operatorname{Beta}(\alpha,\beta)$。把其对数加到似然上，得到对数后验（忽略常数）：

$$
(h+\alpha-1)\log p+(t+\beta-1)\log(1-p).
$$

若两个更新后参数均大于 1，内部 MAP 是

$$
p_{\mathrm{MAP}}=\frac{h+\alpha-1}{n+\alpha+\beta-2}.
$$

后验预测则不是众数，而是对参数积分：

$$
P(X_{\mathrm{next}}=1\mid D)=E[p\mid D]
=\frac{h+\alpha}{n+\alpha+\beta}.
$$

例如只看到一次正面、取 $\operatorname{Beta}(2,2)$ 先验：

| 输出 | 数值 | 它回答的问题 |
| --- | ---: | --- |
| MLE | $1$ | 哪个单点参数最贴合这一次样本？ |
| MAP | $2/3$ | 加入该先验后，后验密度的内部众数在哪里？ |
| 后验预测 | $3/5$ | 积掉参数不确定性后，下一次正面的概率是多少？ |

三者不同不是实现分歧，而是目标不同。均匀 $\operatorname{Beta}(1,1)$ 先验、一次正面时，后验众数落在边界；因此代码拒绝把它伪装成“唯一内部 MAP”，而后验预测仍清楚地等于 $2/3$。

## 可运行实现与验证

```python
from projects.naive_bayes_spam.bernoulli_estimation import (
    bernoulli_log_likelihood, bernoulli_map, bernoulli_mle,
    bernoulli_mle_certificate,
)

observations = [1] * 8 + [0] * 2
assert bernoulli_mle(observations) == 0.8
assert bernoulli_log_likelihood(observations, 0.8) > bernoulli_log_likelihood(observations, 0.6)
assert bernoulli_map([1, 1, 0], alpha=2.0, beta=2.0) == 3 / 5
assert bernoulli_mle_certificate(observations, 0.8)["valid"]
```

运行 `python -m unittest projects.naive_bayes_spam.test_bernoulli_estimation`。实现将 $p=0$ 和 $p=1$ 的端点区分为“与观测一致时对数似然为 $0$”与“观察到不可能事件时为 $-\infty$”，不再把数学边界静默混为同一错误。`bernoulli_mle_certificate` 会从样本重新计算均值，并标出结果应当是唯一的内部驻点，还是全 0/全 1 数据的边界解；将候选值从 $0.8$ 篡改为 $0.7$ 会使证书失效。它核查定理结论，不替代上节的二阶导数与 KL 分解证明。测试验证 MLE 是样本均值、它优于邻近候选、MAP 的先验平滑，以及空样本/非法概率的失败契约。

扫描 $n$ 条观测的时间为 $O(n)$、额外空间为 $O(1)$。实际分类器会最小化平均负对数似然，也就是交叉熵；用 `logsumexp` 等技巧处理极小概率，避免下溢。

## 正确性与工程边界

在 Bernoulli 模型内，样本均值既是严格凹对数似然的唯一内部最大点，也使经验 KL 项为零。这个双重证明不把经验频率升级为真实参数：如果样本不独立、记录机制有偏或真实分布不在模型族中，MLE 仍只是在给定模型族内找**经验交叉熵最小的投影**。更多数据会降低抽样波动，却不会修复错特征、错标签定义或部署分布变化。

MAP 把先验明确写入优化目标，可避免小样本的极端 MLE；它不能自动选择正确先验。后验预测反映参数不确定性，但也继承模型与先验假设。涉及校准、阈值和动作的结论仍要进入独立验证与人工审查，不能从训练损失直接推出。

## 常见误区

- **“似然是参数为真的概率。”** 参数固定时不是；需要先验和归一化才得到后验。
- **“交叉熵与 MLE 是两种不同训练目标。”** 对固定数据集和同一模型，它们仅差负号与样本数比例。
- **“MLE 找到真实概率。”** 它只最小化经验分布到模型的 KL 项；抽样、模型错设和漂移仍在。
- **“MAP 就是平滑后的预测概率。”** MAP 是后验众数，后验预测是后验均值；边界时差异尤其明显。
- **“把概率直接相乘也没关系。”** 长样本的连乘会下溢，应在对数域计算。

## 练习

1. **基础**：为 3 正 7 反计算 MLE、平均负对数似然和 $p=0.5$ 相对 MLE 的额外损失。
2. **推导**：从经验交叉熵逐项加减 $\hat q\log\hat q+(1-\hat q)\log(1-\hat q)$，推出熵加 KL 的分解。
3. **推导**：写出 Beta$(\alpha,\beta)$ 先验下的 MAP 估计，并指出何时存在内部解；再与后验预测比较。
4. **编码**：将 `bernoulli_mle_certificate` 的候选值篡改为非样本均值，确认它拒绝；再为全 0、全 1、非法观测和空列表增加测试。
5. **开放**：说明独立同方差高斯噪声下最小二乘为何等价于 MLE，并指出离群点为什么会破坏该假设。

## 练习答案提示

1. $\hat q=0.3$；每样本负对数似然是 $-\{0.3\log0.3+0.7\log0.7\}$。将 $p=0.5$ 代入交叉熵后相减，即得到 Bernoulli KL 项。
2. 加减的第一组项是 $H(\hat q)$，剩余对数比是 $D_{\mathrm{KL}}(\hat q\Vert p)$；前者不依赖候选 $p$。
3. 将 Bernoulli 对数似然与 $(\alpha-1)\log p+(\beta-1)\log(1-p)$ 相加；两个后验参数都大于 1 才有唯一内部众数。预测使用 $(\alpha+h)/(\alpha+\beta+n)$，不是 MAP 分式。
4. 全 0 与全 1 是合法边界样本；混合样本才有内部驻点。证书应从原始样本重算均值，而不是只相信传入候选。
5. 对联合高斯密度取对数，丢掉与参数无关的常数，剩下平方残差和；平方会放大离群点的影响。

## 延伸与下一步

[交叉熵与 KL 散度](/probability-ml/cross-entropy-kl)将这条分解推广到多类别与 logits；[共轭先验与后验预测](/probability-ml/conjugate-priors-predictive)继续处理 MLE 的小样本边界；[生成模型、朴素贝叶斯与逻辑回归](/probability-ml/generative-discriminative-logistic)展示不同模型如何把似然连接到分类。
