---
title: 项目：朴素贝叶斯垃圾邮件分类器
description: 从词袋、拉普拉斯平滑到稳定后验、混淆矩阵与校准评估的可测试概率分类器。
---

# 项目：朴素贝叶斯垃圾邮件分类器

## 目标

将[贝叶斯更新](/probability-ml/bayes)和[最大似然](/probability-ml/maximum-likelihood)落实为可测试分类器：先用独立的二元后验轨迹审计先验、似然、证据概率与连续更新，用有限分布矩和全方差报告验证期望、组内波动与组间差异，用协方差报告验证中心化、对称性与方差非负，并以二次关系展示零相关不等于独立，用重复伯努利抽样对照样本均值的 $1/\sqrt n$ 标准误缩放与经验覆盖，用计数诊断比较均值、方差与泊松零值基线，用双侧置换检验审计“标签在零假设下可交换”的 p 值模拟，再从带标签文本估计先验和词条件概率，在对数域比较后验，并以混淆矩阵与[校准指标](/probability-ml/calibration-reliability)审查输出。另有[生成模型与逻辑回归](/probability-ml/generative-discriminative-logistic)的最小批量梯度下降实现，用于比较直接学习后验的路径；[Metropolis–Hastings](/probability-ml/metropolis-hastings)模块则演示仅知道未归一化权重时如何采样。

## 运行

```bash
python -m unittest discover -s projects/naive_bayes_spam -p "test_*.py"
```

## 数学与验证

对类别 $y$ 和词 $w$，拉普拉斯平滑概率为

$$P(w\mid y)=\frac{\operatorname{count}(w,y)+1}{\sum_{w'}\operatorname{count}(w',y)+|V|}.$$

预测时累加 $\log P(y)+\sum_w\log P(w\mid y)$，避免小概率相乘下溢。两类分数的差经稳定 sigmoid 转为 $P(y=1\mid x)$；项目会计算精确率、召回率、F1、Brier 分数和可靠性分箱。二元后验模块验证低基率下的证据归一化、无信息证据和条件独立的连续更新；配套伯努利模块验证 MLE、端点对数似然和 Beta 先验下的 MAP。测试覆盖两类训练前提、未见词平滑、概率归一化、混淆矩阵及分箱计数守恒。

## 工程边界

这是教学词袋模型，不是生产反垃圾邮件系统：没有真实中文分词、特征审计、数据漂移监测或对抗鲁棒性。虽然现在能生成可靠性分箱，但小样本图形不能证明校准；必须在独立验证集上检查，并同时报告每箱样本量。准确率也不足以评价低基率任务，必须结合精确率、召回率、Brier 分数与校准。

## 挑战

1. 比较不平衡训练数据下的阈值与精确率/召回率；
2. 为每个可靠性箱加入置信区间；
3. 用 [Beta–Bernoulli 后验预测](/probability-ml/conjugate-priors-predictive)比较拉普拉斯平滑与显式先验；
4. 用独立验证集实现简单再校准，并审计测试集泄漏。
5. 在相同训练/验证切分上比较词袋朴素贝叶斯与逻辑回归，记录 F1、Brier 分数和失败样本。
6. 用 MCMC 近似一个没有共轭解的小型后验，并报告接受率、不同初值轨迹与有效样本量限制。
