# 机器学习需要的概率论

概率论为不确定性提供语言；统计学让我们从有限数据推断未知规律。深度版的主线是“证据如何更新判断，数据如何估计参数，结论如何量化不确定性”。

## 按层进入

| 层级 | 先学什么 | 达成的能力 | 建议入口 |
| --- | --- | --- | --- |
| 0 · 预备 | 事件、函数与有限求和 | 用可枚举样本空间表达概率 | [符号、函数、求和与 Python](/foundations/functions-summation-python) → [概率空间与事件](/probability-ml/probability-space-events) |
| 1 · 核心 | 条件概率、随机变量、期望与方差 | 正确解释概率与平均行为 | [条件概率与贝叶斯更新](/probability-ml/bayes) → [期望与方差](/probability-ml/expectation-variance) |
| 2 · 推导与算法 | 似然、先验、交叉熵与估计 | 从数据推导参数与预测规则 | [最大似然](/probability-ml/maximum-likelihood) → [共轭先验与后验预测](/probability-ml/conjugate-priors-predictive) |
| 3 · 工程与前沿 | 校准、再校准、漂移监控、带标签性能审计、联合证据、重要性采样、MCMC | 审计不确定性、相关样本与模型分数 | [概率校准与可靠性曲线](/probability-ml/calibration-reliability) → [概率再校准](/probability-ml/recalibration) → [数据漂移监控](/probability-ml/data-drift-monitoring) → [带标签窗口性能审计](/probability-ml/labeled-window-performance-degradation) → [联合证据](/probability-ml/joint-input-label-evidence) |

若你的目标是机器学习建模，至少完成层 1 后再进入最大似然；层 3 的实验仍依赖前面建立的概率语义与边界。

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
- [概率再校准：验证集把分数变回概率](/probability-ml/recalibration)：用独立验证集拟合 Platt scaling，避免测试集泄漏；
- [数据漂移监控：何时不应再相信校准概率](/probability-ml/data-drift-monitoring)：用 PSI 与总变差距离报告输入变化，并把告警限定为人工审查触发器；
- [带标签窗口：审计分类性能与概率退化](/probability-ml/labeled-window-performance-degradation)：在延迟标签到达后并列检查混淆矩阵、准确率区间、Brier 分数和对数损失；
- [联合证据：输入漂移与带标签性能如何一起审计](/probability-ml/joint-input-label-evidence)：将两类同窗口信号并列保留，并明确拒绝因果和自动行动声明；
- [概率论深度版路线](/probability-ml/rewrite-plan)：分层学习和垃圾邮件分类项目。

贯穿主线：模型给出的概率，究竟代表什么？
