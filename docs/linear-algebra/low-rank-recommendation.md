---
title: 低秩推荐：缺失评分如何变成可学习的向量
description: 从秩一评分矩阵与交替最小二乘推导协同过滤，审计观测残差、缺失预测与冷启动边界。
courseLevel: "3（低秩建模、优化与工程边界）"
prerequisites: "矩阵乘法、最小二乘、SVD 与低秩近似"
estimatedMinutes: 70
experiment: "对带缺失评分矩阵运行秩一交替最小二乘并重放每轮坐标最小化"
---

# 低秩推荐：缺失评分如何变成可学习的向量

## 学习目标

读完后，你能把稀疏评分表写成只在观测集合上定义的低秩目标；从固定一侧因子推导交替最小二乘更新；运行并重放秩一拟合轨迹；并能区分训练残差、未观测预测、冷启动和真实推荐质量。

## 从一个计算问题开始

用户没有给电影评分，通常表示“没看过或没反馈”，不是给了零分。若把空格当 0，矩阵会被大量人造负反馈主导；若只在已观测位置拟合，又如何为未评分电影产生预测？这就是协同过滤的基本建模选择。

## 直觉与严格定义

令 $R_{ui}$ 是用户 $u$ 对物品 $i$ 的评分，仅在观测集合 $\Omega$ 中存在。秩一模型以两个标量表示每位用户和物品：

$$\hat R_{ui}=p_uq_i.$$

带 L2 正则的目标不是完整矩阵误差，而是

$$
J(p,q)=\sum_{(u,i)\in\Omega}(R_{ui}-p_uq_i)^2
+\lambda\left(\sum_up_u^2+\sum_iq_i^2\right),\qquad\lambda>0.
$$

低秩假设说评分可由少数潜在偏好解释；它不是说所有用户或物品真的只有一个特征。秩一只用于让每个更新可手算、可审计。

## 分步推导：固定一侧时是岭回归

固定所有 $q_i$，与用户 $u$ 有关的部分为

$$J_u(p_u)=\sum_{i:(u,i)\in\Omega}(R_{ui}-p_uq_i)^2+\lambda p_u^2.$$

求导并令零：

$$
-2\sum_iq_i(R_{ui}-p_uq_i)+2\lambda p_u=0
\quad\Longrightarrow\quad
p_u=\frac{\sum_iR_{ui}q_i}{\lambda+\sum_iq_i^2}.
$$

固定 $p$ 同理得到 $q_i=\sum_uR_{ui}p_u/(\lambda+\sum_up_u^2)$。交替更新 $p$、$q$ 是 **ALS**。每个子问题有唯一的正则化最小点；整个双线性目标却不是联合凸优化，不能把一条下降轨迹误当作全局最优证明。

## 可运行实验：只拟合观测评分

```python
from projects.linear_algebra_lab.recommendation import (
    rank_one_als_report,
    rank_one_als_trace_certificate,
)

ratings = [[5.0, None, 2.0], [4.0, 2.0, None], [None, 1.0, 1.0]]
report = rank_one_als_report(ratings, iterations=20, regularization=0.1)

assert report.observed_rmse < 0.7
assert report.predictions[0][1] != 0.0  # 空格得到模型预测，但不是观测事实
assert rank_one_als_trace_certificate(ratings, report, iterations=20, regularization=0.1)
```

运行 `python -m unittest projects.linear_algebra_lab.test_recommendation`。报告保存每轮用户因子、物品因子与已观测平方误差；证书独立重放每个坐标最小化，并会拒绝篡改的因子或误差。设 $|\Omega|$ 为评分数、秩为 $k$，常规 ALS 每轮约为 $O(|\Omega|k^2)$；此课 $k=1$，因此每轮线性扫描观察项。真实系统会以稀疏格式和并行线性代数实现，而非 Python 双重循环。

## 正确性与工程边界

对固定物品因子，上式是严格凸一元二次函数，故更新确实最小化该用户子问题；物品更新同理。轨迹证书只说明实现按此递推执行、观测误差如何变化。它不证明未观测评分正确，也不证明某次迭代找到了全局最优。

- **冷启动**：没有任何评分的用户或物品没有可解的分子/分母信息；实验显式拒绝，生产系统要引入内容特征、热门先验或探索策略。
- **尺度不唯一**：不加正则时 $p\to cp,q\to q/c$ 给相同预测；正则和初始化会影响数值表示。
- **选择偏差**：用户会选择自己想看的物品来评分；观测集不是随机抽样，低 RMSE 不等于满意度或公平性。
- **离线与在线差异**：预测分高不等于会点击、喜欢或长期留存；必须在留出集和产品实验中评估。

## 常见误区

1. “缺失就是 0。”错误：它改变了优化目标并通常制造系统性偏差。
2. “低秩等于 SVD。”错误：完整矩阵的截断 SVD 与带缺失、正则化的矩阵分解不是同一个问题。
3. “训练 RMSE 下降就证明推荐更好。”错误：还需要时间切分、留出评估、校准和业务指标。
4. “ALS 没有梯度，所以不算优化。”错误：它在每个坐标块上精确解最小二乘子问题。

## 练习

1. **基础题**：对一个用户的两个观测评分和固定 $q$，手算上式的 $p_u$ 更新。
2. **推导题**：从 $J_u(p_u)$ 展开并逐项求导，推导分母为何多出 $\lambda$。
3. **编码题**：为同一评分表比较不同正则系数，报告观测 RMSE 与未观测格预测；验证证书会拒绝篡改的某轮误差。
4. **开放题**：设计一个带用户/物品偏置、时间切分与冷启动策略的离线评估协议，并说明哪些结果不能由 RMSE 单独推出。

## 练习答案提示

1. 固定 $q$ 后将两个残差平方和与 $\lambda p_u^2$ 写成一元二次式，分子是 $\sum r_{ui}q_i$、分母是 $\sum q_i^2+\lambda$。
2. 展开平方后对 $p_u$ 求导并令零；正则项导数给出 $2\lambda p_u$，与误差项公共因子 2 可约去。
3. 固定初始化和迭代次数；将观测集误差与未观测预测分开报告，并篡改保存轨迹中的一个误差以验证证书确实重放更新。
4. 时间切分应避免用未来评分训练；冷启动需定义没有历史时的默认策略，RMSE 之外还要报告覆盖率、校准、群体差异和在线效应。

## 延伸

[SVD](/linear-algebra/svd)解释完整矩阵的最佳低秩近似；[最小二乘](/linear-algebra/least-squares)给出本课每个固定因子子问题的语言；[概率校准](/probability-ml/calibration-reliability)提醒预测数值还需要解释与验证。继续学习可检索 matrix factorization、implicit feedback、Bayesian personalized ranking、temporal validation。
