---
title: 第一阶段练习提示
description: 十篇核心课的分层练习起点、验证口径与开放题报告框架。
---

# 第一阶段练习提示

这些提示只给出下一步，不替代推导或代码。每题完成后仍应以原文的公式、测试或边界条件复核。

| 课程 | 基础/推导提示 | 编码/开放提示 |
| --- | --- | --- |
| [向量与点积](/linear-algebra/vectors-dot-product) | 先写点积与范数，再检查零向量。 | 用同形与零范数作边界；报告相似度不代表语义。 |
| [高斯消元](/linear-algebra/gaussian-elimination) | 每次行变换后保留同一解集。 | 重放主元、交换与消元；加入奇异或近零主元。 |
| [最小二乘](/linear-algebra/least-squares) | 从 $A^Tr=0$ 开始。 | 同时报残差与条件性，比较正规方程和 QR。 |
| [循环不变量](/discrete-math/loop-invariants) | 写初始化、保持、终止三段。 | 枚举空数组、单元素和不存在目标。 |
| [Dijkstra](/discrete-math/dijkstra) | 用“已确定点距离最短”写归纳。 | 负边必须显式拒绝或转用 Bellman–Ford。 |
| [贝叶斯更新](/probability-ml/bayes) | 先计算证据概率作分母。 | 测低基率、零证据与校准，不只看后验最大类。 |
| [最大似然](/probability-ml/maximum-likelihood) | 取对数后求导，检查端点。 | 固定数据比较 MLE/MAP，并报告小样本假设。 |
| [浮点数表示](/numerical-computing/floating-point) | 查看二进制邻近数与 ULP。 | 用容差和量纲写断言，勿直接比较相等。 |
| [条件数](/numerical-computing/condition-number) | 区分输入扰动、残差与解扰动。 | 构造近奇异例，报告前向与后向误差。 |
| [RSA](/number-theory-crypto/rsa) | 用 $ed\equiv1\pmod{\varphi(n)}$ 推导。 | 只用教学小参数；列出裸 RSA、填充与侧信道边界。 |

## 使用方式

对每道开放题至少记录：输入/假设、采用的公式或不变量、可复现命令、指标，以及结果**不能**证明什么。
