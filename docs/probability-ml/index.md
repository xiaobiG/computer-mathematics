# 机器学习需要的概率论

概率论为不确定性提供语言；统计学让我们从有限数据推断未知规律。深度版的主线是“证据如何更新判断，数据如何估计参数，结论如何量化不确定性”。

## 课程地图

1. 条件概率与贝叶斯公式
2. 随机变量、分布与期望
3. 方差、协方差与相关性
4. 抽样、估计与置信区间
5. 最大似然与交叉熵
6. 生成模型、朴素贝叶斯与逻辑回归
7. 蒙特卡洛、MCMC 与模型不确定性
8. 朴素贝叶斯、EM 与模型不确定性

## 当前深度版

- [概率空间与事件](/probability-ml/probability-space-events)：有限样本空间、集合运算、条件化与独立性；
- [条件概率与贝叶斯更新](/probability-ml/bayes)：全概率、低基率与校准边界；
- [联合、边缘与条件分布](/probability-ml/joint-marginal-conditional)：有限联合表、边缘化、条件化与独立性证书；
- [协方差、相关性与特征](/probability-ml/covariance-correlation)：共同变化、协方差矩阵、PCA 与因果边界；
- [大数定律与中心极限定理](/probability-ml/laws-of-large-numbers-clt)：样本均值、标准误缩放、近似正态与独立性边界；
- [抽样误差、置信区间与覆盖率](/probability-ml/confidence-intervals-sampling)：标准误、覆盖率、bootstrap 与实验设计边界；
- [最大似然](/probability-ml/maximum-likelihood)：对数似然、MAP 与参数估计；
- [交叉熵与 KL 散度](/probability-ml/cross-entropy-kl)：概率承诺、分布比较与零概率边界；
- [生成模型、朴素贝叶斯与逻辑回归](/probability-ml/generative-discriminative-logistic)：伯努利似然、梯度下降与两条概率分类路径；
- [共轭先验与后验预测](/probability-ml/conjugate-priors-predictive)：Beta–Bernoulli 更新、平滑与小样本边界；
- [常见分布](/probability-ml/common-distributions)：从生成机制选择伯努利、泊松、指数与正态模型；
- [假设检验与 p 值](/probability-ml/hypothesis-testing)：置换检验、错误率与实验决策边界；
- [蒙特卡洛与重要性采样](/probability-ml/monte-carlo-importance-sampling)：随机积分、权重与有效样本量；
- [Metropolis–Hastings](/probability-ml/metropolis-hastings)：详细平衡、接受率、相关样本与混合边界；
- [概率校准与可靠性曲线](/probability-ml/calibration-reliability)：把分类分数变为可审计的概率承诺；
- [概率论深度版路线](/probability-ml/rewrite-plan)：分层学习和垃圾邮件分类项目。

贯穿主线：模型给出的概率，究竟代表什么？
