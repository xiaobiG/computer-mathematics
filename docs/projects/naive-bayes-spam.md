---
title: 项目：朴素贝叶斯垃圾邮件分类器
description: 从词袋、拉普拉斯平滑到对数后验和混淆矩阵的可测试概率分类器。
---

# 项目：朴素贝叶斯垃圾邮件分类器

## 目标

将[贝叶斯更新](/probability-ml/bayes)和[最大似然](/probability-ml/maximum-likelihood)落实为可测试分类器：从带标签文本估计先验和词条件概率，在对数域比较后验，并用混淆矩阵审查错误。

## 运行

```bash
python -m unittest projects.naive_bayes_spam.test_main
```

## 数学与验证

对类别 $y$ 和词 $w$，拉普拉斯平滑概率为

$$P(w\mid y)=\frac{\operatorname{count}(w,y)+1}{\sum_{w'}\operatorname{count}(w',y)+|V|}.$$

预测时累加 $\log P(y)+\sum_w\log P(w\mid y)$，避免小概率相乘下溢。测试覆盖两类训练前提、未见词平滑、预测和混淆矩阵。

## 工程边界

这是教学词袋模型，不是生产反垃圾邮件系统：没有真实中文分词、特征审计、数据漂移监测、对抗鲁棒性和概率校准。准确率也不足以评价低基率任务，必须结合精确率、召回率与校准。

## 挑战

1. 加入精确率、召回率和 F1；
2. 比较不平衡训练数据下的阈值；
3. 实现可靠性分箱，观察模型分数是否校准。
