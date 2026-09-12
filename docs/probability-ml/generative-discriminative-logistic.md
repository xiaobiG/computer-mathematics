---
title: 生成模型、朴素贝叶斯与逻辑回归
description: 从伯努利似然推导交叉熵和批量梯度下降，并比较生成式与判别式分类的假设和边界。
courseLevel: 2
prerequisites: 条件概率、最大似然、导数与向量点积
estimatedMinutes: 55
experiment: projects/naive_bayes_spam/logistic_regression.py
---

# 生成模型、朴素贝叶斯与逻辑回归

## 学习目标

读完后，你能从伯努利似然推导二元交叉熵和批量梯度，解释线性分数为何作用在对数赔率上，实现 L2 正则化，并用 Brier 分数区分“分类正确”和“概率可信”。

## 从一个分类决策开始

垃圾邮件分类器既可以先分别学习“垃圾邮件怎样生成文字”和“正常邮件怎样生成文字”，再由贝叶斯公式得到类别；也可以直接学习特征 $x$ 出现时为垃圾邮件的概率。前者是生成模型，后者是判别模型。两者都能输出概率，但它们的错误来源不同。

## 直觉与符号

把一封邮件编码为特征向量 $x\in\mathbb{R}^d$，令 $y\in\{0,1\}$ 表示类别。逻辑回归先计算线性分数

$$z=b+w^\mathsf{T}x,$$

再用 sigmoid 压到数学上的 $(0,1)$：

$$p=P(Y=1\mid x)=\sigma(z)=\frac{1}{1+e^{-z}}.$$

其中 $b$ 是截距，$w$ 是权重。$z=0$ 对应 $p=0.5$；每让 $z$ 增加一，正类对数赔率增加一。这个线性假设作用在**对数赔率**上，而不是直接作用在概率上。

把 sigmoid 方程移项即可看到这件事：

$$
\frac{p}{1-p}=e^z,\qquad \log\frac{p}{1-p}=z=b+w^\mathsf{T}x.
$$

因此一个特征权重 $w_j=\log 2$ 的含义不是“概率增加 $\log2$”，而是在其他特征不变时把正类赔率乘以 2。靠近 $p=0$ 或 $p=1$ 时，同样的赔率变化对应的概率增量很小；这是不能直接做线性概率回归的原因。

## 从伯努利似然推导交叉熵

对单个标签，伯努利模型的似然为

$$P(y\mid x)=p^y(1-p)^{1-y}.$$

对 $n$ 个独立训练样本取负对数，并代入 $p_i=\sigma(b+w^\mathsf{T}x_i)$，得到平均损失

$$L(b,w)=-\frac{1}{n}\sum_{i=1}^{n}[y_i\log p_i+(1-y_i)\log(1-p_i)].$$

链式法则给出关键的简化：$\frac{\partial L}{\partial z_i}=p_i-y_i$。因此

$$\nabla_w L=\frac{1}{n}\sum_i(p_i-y_i)x_i,\qquad
\frac{\partial L}{\partial b}=\frac{1}{n}\sum_i(p_i-y_i).$$

梯度为正表示该特征组合预测得过高，梯度下降就降低相应权重；为负则相反。这正是实现中 `residual = probability - target` 的来源。

不省略中间步骤时，对单个样本的负对数似然 $\ell=-y\log p-(1-y)\log(1-p)$，有

$$
\frac{\partial\ell}{\partial p}=-\frac yp+\frac{1-y}{1-p},
\qquad \frac{\partial p}{\partial z}=p(1-p).
$$

相乘后分母消去：$\partial\ell/\partial z=p-y$。再由 $z=b+w^\mathsf T x$ 得到 $\partial z/\partial w_j=x_j$，这正是每个特征梯度中 `residual * feature` 的来历。推导也说明了两项前提：标签必须是伯努利的 $0/1$，而且损失必须接收连续概率，不能先阈值化。

## 手算一次更新

从 $b=0,w=0$ 开始，对样本 $x=[2],y=1$，有 $p=0.5$，残差为 $-0.5$。学习率 $\eta=0.1$ 时：

$$b\leftarrow0-0.1(-0.5)=0.05,\quad w\leftarrow0-0.1(-0.5\times2)=0.1.$$

新的分数为 $0.25$，概率约为 $0.562$，比原来的 $0.5$ 更接近正类。批量梯度下降只是在一次更新前把所有样本的同类贡献相加并取平均。

## 可运行实验

项目中的实现只依赖标准库，训练一个二维、线性可分的小数据集。`l2` 是 $\lambda$，它只惩罚特征权重、不惩罚截距：

```python
from projects.naive_bayes_spam.logistic_regression import LogisticRegression

samples = [([-2.0, -1.0], False), ([-1.0, -2.0], False),
           ([1.0, 2.0], True), ([2.0, 1.0], True)]
plain = LogisticRegression().fit(samples, learning_rate=0.5, steps=500, l2=0.0)
regularised = LogisticRegression().fit(samples, learning_rate=0.5, steps=500, l2=0.3)

def l2_norm(model):
    return sum(weight * weight for weight in model.weights[1:]) ** 0.5

assert l2_norm(regularised) < l2_norm(plain)
print(regularised.predict_proba([1.0, 1.0]))
print(regularised.loss(samples))
```

训练目标变为

$$
L_\lambda(b,w)=L(b,w)+\frac\lambda2\lVert w\rVert_2^2,
\qquad \nabla_wL_\lambda=\nabla_wL+\lambda w.
$$

运行 `python -m unittest projects.naive_bayes_spam.test_logistic_regression`。测试验证极端分数下 sigmoid 不发生指数溢出、交叉熵方向正确、训练损失下降、L2 会缩小非截距权重范数、特征维度不一致或负正则强度会被拒绝。有限精度下极端分数仍可能舍入为 `0.0` 或 `1.0`，因此训练生产模型通常直接使用以 logits 表示的稳定交叉熵实现。

时间复杂度为 $O(Tnd)$，其中 $T$ 为更新次数、$n$ 为样本数、$d$ 为特征数；模型本身占用 $O(d)$ 空间。

## 与朴素贝叶斯的分界

朴素贝叶斯建模 $P(x\mid y)P(y)$，再归一化得到 $P(y\mid x)$；它需要给特征的联合生成过程作假设，词袋版本尤其假设给定类别后词独立。逻辑回归直接建模 $P(y\mid x)$，避免该生成假设，但仍假设类别的对数赔率可由特征线性组合表示。

两者并无必然胜者：数据很少、生成假设较合理时，朴素贝叶斯常能快速工作；特征相关性强、标注数据足够时，逻辑回归通常更灵活。必须在独立验证集上以相同指标比较，而不是凭训练集准确率下结论。

## 分类阈值与概率校准是两件事

阈值 $0.5$ 把概率变成类别，适合计算准确率、精确率和召回率；但它会丢弃置信度。对二元标签，Brier 分数保留这部分信息：

$$
\operatorname{Brier}=\frac1n\sum_{i=1}^n(p_i-y_i)^2.
$$

一个预测 $0.51$ 和一个预测 $0.99$ 即使都被阈值化为正类，Brier 分数也会严格区分它们。它不是万能排名指标：类别不平衡、业务阈值和误报成本仍需单独报告；可靠性曲线则检查“预测约为 0.7 的样本中，正类频率是否也约为 0.7”。

## 失败案例与工程边界

若数据线性可分且没有正则化，继续最小化交叉熵会把权重推向无限大；概率会看似越来越自信，却不代表泛化更好。生产模型需要正则化、特征缩放、验证集和校准检查。本文代码是全批量、稠密特征教学实现，面对稀疏词袋或百万样本应使用成熟库的稀疏优化器。

另一个常见错误是先把概率阈值化为 $0/1$ 再计算交叉熵：$\log 0$ 无定义，也丢失了梯度。损失函数应使用连续概率，分类阈值只用于最终决策。

## 练习

1. **基础**：证明 $\sigma(-z)=1-\sigma(z)$，并解释为何这使二类概率互补。
2. **推导**：在损失中加入 $\lambda\lVert w\rVert_2^2/2$，推导权重梯度多出的项。
3. **编码**：为 `LogisticRegression` 加入 L2 正则化，并写一个测试，说明它会缩小权重范数。
4. **开放**：把垃圾邮件项目拆为训练、验证、测试集，比较朴素贝叶斯和逻辑回归的 Brier 分数；说明比较可能受哪些数据漂移影响。

## 练习答案提示

1. 直接代入定义：$\sigma(-z)=1/(1+e^z)$，将 $1-\sigma(z)$ 通分即可得到同一式子；这保证两类的条件概率和为 1。
2. 数据项梯度仍是 $X^\top(p-y)/n$；对 $\lambda\lVert w\rVert_2^2/2$ 求导得到 $\lambda w$。通常不对截距正则化，需在实现中明确这个约定。
3. 在训练梯度加上 `lambda_ * w`，并在损失加入相应二次项；用同一数据、初始化和学习率比较训练后 `norm(w)`，同时避免把“范数更小”误当作泛化必然更好。
4. 按时间或来源切分以避免泄漏，在同一保留测试集计算 Brier 分数和校准曲线；词汇、攻击策略、标签政策和类别比例变化都会导致分布漂移，故需记录切分与再训练策略。

## 下一步

回到[最大似然](/probability-ml/maximum-likelihood)理解对数似然的通用形式，使用[概率校准与可靠性曲线](/probability-ml/calibration-reliability)审查概率承诺，并在[垃圾邮件分类项目](/projects/naive-bayes-spam)中比较两种模型。接下来可进入正则化、重要性采样和更复杂的生成模型。
