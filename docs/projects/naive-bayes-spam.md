---
title: 项目：朴素贝叶斯垃圾邮件分类器
description: 从词袋、拉普拉斯平滑到稳定后验、混淆矩阵与校准评估的可测试概率分类器。
---

# 项目：朴素贝叶斯垃圾邮件分类器

## 目标

将[概率空间与事件](/probability-ml/probability-space-events)、[贝叶斯更新](/probability-ml/bayes)和[最大似然](/probability-ml/maximum-likelihood)落实为可测试分类器：先用有限样本空间报告审计事件的并、交、补、条件化和独立性残差，再用独立的二元后验轨迹审计先验、似然、证据概率与连续更新，用有限分布矩和全方差报告验证期望、组内波动与组间差异，用协方差报告验证中心化、对称性与方差非负，并以二次关系展示零相关不等于独立，用重复伯努利抽样对照样本均值的 $1/\sqrt n$ 标准误缩放与经验覆盖，用计数诊断比较均值、方差与泊松零值基线，用双侧置换检验审计“标签在零假设下可交换”的 p 值模拟，再从带标签文本估计先验和词条件概率，在对数域比较后验，并以混淆矩阵与[校准指标](/probability-ml/calibration-reliability)审查输出。另有[生成模型与逻辑回归](/probability-ml/generative-discriminative-logistic)的最小批量梯度下降实现，用于比较直接学习后验的路径；[Metropolis–Hastings](/probability-ml/metropolis-hastings)模块则演示仅知道未归一化权重时如何采样，并从固定种子重放每一轮提议与接受决策。

## 运行

```bash
python -m unittest discover -s projects/naive_bayes_spam -p "test_*.py"
```

## 数学与验证

对类别 $y$ 和词 $w$，拉普拉斯平滑概率为

$$P(w\mid y)=\frac{\operatorname{count}(w,y)+1}{\sum_{w'}\operatorname{count}(w',y)+|V|}.$$

预测时累加 $\log P(y)+\sum_w\log P(w\mid y)$，避免小概率相乘下溢。两类分数的差经稳定 sigmoid 转为 $P(y=1\mid x)$；项目会计算精确率、召回率、F1、Brier 分数和可靠性分箱。每个非空箱还报告正例计数和 Wilson 区间，避免把计数为 1 的频率当作精确校准率。[Platt scaling 再校准器](/probability-ml/recalibration)只接收显式的验证分数与标签，以 logistic 后处理审计 Brier、对数损失与优化轨迹，避免把测试标签隐藏进 `fit`。[数据漂移报告](/probability-ml/data-drift-monitoring)用 PSI、总变差距离和独立重放证书比较参考期与当前期的类别频率；它报告风险信号而不自动决定重训。二元后验模块验证低基率下的证据归一化、无信息证据和条件独立的连续更新；配套伯努利模块验证 MLE、端点对数似然和 Beta 先验下的 MAP。测试覆盖两类训练前提、未见词平滑、概率归一化、混淆矩阵、分箱计数守恒、Wilson 边界、再校准输入契约与漂移报告篡改。

## 工程边界

这是教学词袋模型，不是生产反垃圾邮件系统：没有真实中文分词、特征审计、生产级数据漂移监测或对抗鲁棒性。虽然现在能生成可靠性分箱、Wilson 区间、验证集上的再校准和教学用的类别漂移报告，但小样本图形不能证明校准；必须在独立验证集上选择后处理，并在保留测试集上一次性报告。准确率也不足以评价低基率任务，必须结合精确率、召回率、Brier 分数、对数损失、校准与带标签窗口的性能审计。

## 挑战

1. 比较不平衡训练数据下的阈值与精确率/召回率；
2. 改变 Wilson 覆盖水平并审查极小样本箱的区间宽度；
3. 用 [Beta–Bernoulli 后验预测](/probability-ml/conjugate-priors-predictive)比较拉普拉斯平滑与显式先验；
4. 用独立验证集实现简单再校准，并审计测试集泄漏。
5. 在相同训练/验证切分上比较词袋朴素贝叶斯与逻辑回归，记录 F1、Brier 分数和失败样本。
6. 用 MCMC 近似一个没有共轭解的小型后验，并报告接受率、不同初值轨迹与有效样本量限制。
