---
title: 项目：浮点数错误博物馆
description: 用可复现实验观察舍入、累计误差、消去误差与蒙特卡洛抽样波动，并验证稳定改写。
---

# 项目：浮点数错误博物馆

## 目标

这个项目收录数值程序中常见的陷阱：直接相等比较、长序列求和、相近数相减，以及把一次随机模拟当成结论。每个案例都同时提供“容易出错的写法”和更稳定的处理方式。

## 数学连接

- [浮点数](/numerical-computing/floating-point)：为何十进制小数常被近似存储；
- [Kahan 求和](/numerical-computing/kahan-summation)：如何补偿累计时丢失的低位；
- [条件数](/numerical-computing/condition-number)：为何有些表达式对误差天生敏感。
- [随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)：抽样误差、固定种子与重复报告。

## 运行

```bash
python projects/floating_point_museum/examples.py
python projects/floating_point_museum/simulation.py
python -m unittest projects.floating_point_museum.test_examples
python -m unittest projects.floating_point_museum.test_simulation
python -m unittest projects.floating_point_museum.test_root_finding
```

## 三个案例

1. `0.1 + 0.2`：说明二进制近似与容差比较；
2. `1e16 + 1 + 1 - 1e16`：比较普通累加、Kahan 与固定归约树的 pairwise 求和；观察 pairwise 改善误差层数，却不保证修复每个抵消顺序。
3. $\sqrt{x+1}-\sqrt{x}$：通过有理化避免消去误差。
4. 单位圆蒙特卡洛：用多个固定 seed 估计 $\pi$，报告均值、样本标准差和标准误，而不是挑选一次结果。
5. 割线法：不提供导数求解 $x^2-2=0$，并观察零割线斜率如何被拒绝。

## 工程边界

没有“万能 epsilon”。容差必须随业务尺度、允许误差和量纲决定；随机实验还必须区分抽样波动与浮点误差。金额通常应使用最小货币单位整数或十进制定点类型。
