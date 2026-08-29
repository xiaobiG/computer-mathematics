---
courseLevel: "2（推导与建模）"
prerequisites: "概率分布、对数与微分"
estimatedMinutes: 55
experiment: "实现伯努利 MLE 与拉普拉斯平滑"
title: 最大似然：从数据估计参数
description: 推导伯努利模型的最大似然估计，并连接 MAP、交叉熵与数值稳定性。
---

# 最大似然：从数据估计参数

## 文章元信息

- **建议阅读层级**：2–3 · 推导、优化与机器学习应用
- **前置知识**：[贝叶斯更新](/probability-ml/bayes)、导数、对数函数
- **预计学习时间**：55 分钟
- **配套实验**：垃圾邮件分类器的参数估计与校准评估

## 从一个计算问题开始

观察一枚硬币 10 次，其中 8 次正面。程序需要一个正面概率 $p$，应填 0.5、0.8 还是别的数？最大似然不是问“参数本身的概率”，而是问：哪个参数最能解释已经看到的数据？

## 定义与直觉

固定观测 $x_1,\ldots,x_n$，将模型密度 $p(x_i\mid\theta)$ 看成参数 $\theta$ 的函数，称为似然：

$$L(\theta)=\prod_{i=1}^{n}p(x_i\mid\theta).$$

独立样本使概率相乘；单调的对数不改变最优点，并将连乘改为求和：$\ell(\theta)=\sum_i\log p(x_i\mid\theta)$。这也是训练时常见损失函数采用“负对数似然”的原因。

## 分步推导：伯努利硬币

若正面次数为 $h$、反面次数为 $t$，则

$$L(p)=p^h(1-p)^t,\qquad \ell(p)=h\log p+t\log(1-p).$$

对 $0<p<1$ 求导：

$$\frac{d\ell}{dp}=\frac{h}{p}-\frac{t}{1-p}=0
\quad\Longrightarrow\quad \hat p=\frac{h}{h+t}.$$

二阶导数 $-h/p^2-t/(1-p)^2<0$，所以这是最大值。8 正 2 反的估计为 $0.8$。若全为正面，最优点落在边界 $p=1$，这提醒我们样本有限时极端估计并不可靠。

## 算法实现与复杂度

```python
from math import log


def bernoulli_mle(observations):
    if not observations or any(value not in (0, 1) for value in observations):
        raise ValueError("observations must be non-empty zeros and ones")
    return sum(observations) / len(observations)


def bernoulli_log_likelihood(observations, probability):
    if not 0 < probability < 1:
        return float("-inf")
    return sum(log(probability) if value else log(1 - probability) for value in observations)


assert bernoulli_mle([1] * 8 + [0] * 2) == 0.8
```

扫描 $n$ 条观测的时间为 $O(n)$、额外空间为 $O(1)$。实际分类器会最小化平均负对数似然，也就是交叉熵；用 `logsumexp` 等技巧处理极小概率，避免下溢。

## 正确性与工程边界

`bernoulli_mle` 返回样本均值，正是上面唯一内部驻点；二阶导数证明其最大化对数似然。最大似然只优化数据拟合，不表达先验偏好：3 次全正面给出 $p=1$。加入 Beta 先验得到 MAP，可避免零概率并表达平滑假设。模型错设、样本非独立或训练/部署分布漂移时，即使精确最大化似然也可能泛化很差。

## 常见误区

- 似然 $L(\theta)$ 不是“参数为真的概率”；参数固定时它是未归一化评分。
- 高似然不等于因果解释，也不保证校准。
- 将概率直接相乘会下溢；最大化对数似然不是可选的记号替换。

## 练习

1. **基础**：为 3 正 7 反计算 MLE 和对数似然。
2. **推导**：写出 Beta$(\alpha,\beta)$ 先验下的 MAP 估计，并指出何时存在内部解。
3. **编码**：为全 0、全 1、非法观测和空列表增加测试。
4. **开放**：说明高斯噪声假设下最小二乘如何等价于最大似然，并指出离群点为什么会破坏该假设。

## 延伸与下一步

MLE 将数据转为参数；[常见分布](/probability-ml/common-distributions)帮助选择 $p(x\mid\theta)$ 的形式，而[假设检验](/probability-ml/hypothesis-testing)讨论从有限样本得出的结论应有多大把握。
