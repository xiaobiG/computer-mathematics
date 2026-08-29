---
title: 项目：浮点数错误博物馆
description: 用可复现实验观察舍入、累计误差与消去误差，并验证稳定改写。
---

# 项目：浮点数错误博物馆

## 目标

这个项目收录三个在生产代码中常见的数值陷阱：直接相等比较、长序列求和和相近数相减。每个案例都同时提供“容易出错的写法”和更稳定的处理方式。

## 数学连接

- [浮点数](/numerical-computing/floating-point)：为何十进制小数常被近似存储；
- [Kahan 求和](/numerical-computing/kahan-summation)：如何补偿累计时丢失的低位；
- [条件数](/numerical-computing/condition-number)：为何有些表达式对误差天生敏感。

## 运行

```bash
python projects/floating_point_museum/examples.py
python -m unittest projects.floating_point_museum.test_examples
```

## 三个案例

1. `0.1 + 0.2`：说明二进制近似与容差比较；
2. `1e16 + 1 + 1 - 1e16`：比较普通累加与 Kahan 求和；
3. $\sqrt{x+1}-\sqrt{x}$：通过有理化避免消去误差。

## 工程边界

没有“万能 epsilon”。容差必须随业务尺度、允许误差和量纲决定；金额通常应使用最小货币单位整数或十进制定点类型。
