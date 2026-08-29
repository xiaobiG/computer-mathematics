---
title: 十二周计算机数学学习计划
description: 用现有专题文章、练习和项目建立从算法基础到密码学的学习节奏。
---

# 十二周计算机数学学习计划

每周建议投入 4–6 小时：两次阅读与推导、一次代码实验、一次复盘或练习。读到陌生概念时优先回看链接的前置文章，不必一次性掌握所有细节。

## 第一阶段：算法与线性表示（第 1–4 周）

| 周次 | 主题 | 必读 | 本周产出 |
| --- | --- | --- | --- |
| 1 | 正确性与规模 | [循环不变量](/discrete-math/loop-invariants)、[渐进复杂度](/discrete-math/asymptotic-complexity) | 为二分查找写出不变量 |
| 2 | 图与递归 | [BFS](/discrete-math/breadth-first-search)、[递推关系](/discrete-math/recurrences) | 输出无权图的一条最短路径 |
| 3 | 向量与矩阵 | [向量与点积](/linear-algebra/vectors-dot-product)、[矩阵乘法](/linear-algebra/matrix-multiplication) | 比较余弦相似度与欧氏距离 |
| 4 | 方程与拟合 | [高斯消元](/linear-algebra/gaussian-elimination)、[最小二乘](/linear-algebra/least-squares) | 用数据拟合一条直线 |

**阶段项目**：[算法可视化实验室](/projects/)——选择 BFS 或二分查找，把每轮状态、循环不变量和复杂度写进实验记录。

## 第二阶段：概率与数值可靠性（第 5–8 周）

| 周次 | 主题 | 必读 | 本周产出 |
| --- | --- | --- |
| 5 | 概率更新 | [贝叶斯更新](/probability-ml/bayes)、[期望与方差](/probability-ml/expectation-variance) | 解释一个低基率案例 |
| 6 | 数据建模 | [常见分布](/probability-ml/common-distributions)、[最大似然](/probability-ml/maximum-likelihood) | 为一个真实计数问题选择分布 |
| 7 | 浮点表示 | [浮点数](/numerical-computing/floating-point)、[Kahan 求和](/numerical-computing/kahan-summation) | 复现并修复累计误差 |
| 8 | 数值方法 | [牛顿法](/numerical-computing/newton-method)、[条件数](/numerical-computing/condition-number) | 记录一次成功和一次失败的迭代 |

**阶段项目**：[浮点数错误博物馆](/projects/)——至少收录两个可复现的错误案例，并说明容差、补偿或数据表示策略。

## 第三阶段：模运算与综合应用（第 9–12 周）

| 周次 | 主题 | 必读 | 本周产出 |
| --- | --- | --- |
| 9 | 模运算 | [模运算与快速幂](/number-theory-crypto/modular-arithmetic)、[最大公约数与模逆元](/number-theory-crypto/extended-euclid) | 实现并测试模逆元 |
| 10 | 公钥密码 | [RSA](/number-theory-crypto/rsa)、[中国剩余定理](/number-theory-crypto/chinese-remainder-theorem) | 手算教学参数并验证解密 |
| 11 | 项目整合 | [综合项目](/projects/) 与 [术语表](/glossary) | 选择一个项目撰写设计说明 |
| 12 | 复盘与迁移 | [学习路线](/roadmap)、[编辑流程](/editorial-workflow) | 写一篇自己的概念讲解或项目复盘 |

**阶段项目**：[密码学玩具箱](/projects/)——实现快速幂、模逆元和教学 RSA；必须在 README 中说明它不适用于生产环境。

## 完成标准

- 能用自己的话解释每周一个核心概念；
- 至少完成四个代码或手算实验；
- 能指出一个理论假设或工程边界；
- 完成一个综合项目的最小版本。

遇到术语遗忘时使用 [术语表](/glossary)，需要继续深入时回到各专题首页查看后续章节。
