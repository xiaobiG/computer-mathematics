---
courseLevel: "2–3（算法稳定性）"
prerequisites: "浮点表示、循环与求和"
estimatedMinutes: 50
experiment: "比较普通、Kahan 与 pairwise 求和"
title: Kahan 与 pairwise 求和：怎样不让低位悄悄消失
description: 从舍入误差推导补偿求和和分治求和，比较稳定性、复杂度与适用边界。
---

# Kahan 与 pairwise 求和：怎样不让低位悄悄消失

## 文章元信息

- **建议阅读层级**：2–3 · 稳定算法、误差分析与工程取舍
- **前置知识**：[浮点数表示](/numerical-computing/floating-point)、[条件数](/numerical-computing/condition-number)
- **预计学习时间**：50 分钟
- **配套实验**：[浮点数错误博物馆](/projects/floating-point-museum)

## 学习目标

- 解释普通累加为何依赖输入顺序；
- 实现 Kahan 补偿求和和 pairwise 求和；
- 选择排序、补偿或更高精度的合适边界。

## 从一个计算问题开始

数学上 $10^{16}+1+1-10^{16}=2$，但二进制浮点普通累加常得到 0：当 1 加入巨大累计和时，尾数没有足够位保存它。若程序在统计、积分或财务模拟中沉默地丢失上万次这种低位，结果仍可“看起来合理”。

## 直觉与推导

一次浮点加法可写为 $\operatorname{fl}(a+b)=(a+b)(1+\delta)$，其中 $|\delta|$ 受机器精度限制。普通从左到右求和在每一步舍入，且大数先出现时小数的有效位最脆弱。

Kahan 算法用 `compensation` 保存本轮未写入 `total` 的低位：下一轮先计算 $y=x-c$，再加到和中，最后由 $(t-s)-y$ 重建新的舍入损失。它不改变数学目标 $\sum x_i$，只将被舍去的信息延迟回收。

## 算法实现与复杂度

```python
def kahan_sum(values):
    total = compensation = 0.0
    for value in values:
        corrected = value - compensation
        next_total = total + corrected
        compensation = (next_total - total) - corrected
        total = next_total
    return total


def pairwise_sum(values):
    values = list(values)
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    middle = len(values) // 2
    return pairwise_sum(values[:middle]) + pairwise_sum(values[middle:])


assert kahan_sum([1e16, 1.0, 1.0, -1e16]) == 2.0
```

两者时间均为 $O(n)$。Kahan 使用 $O(1)$ 额外空间；上面的递归 pairwise 实现因切片额外占空间，生产实现应以索引或迭代树避免它。pairwise 将误差增长从线性层数改善为对数层数，且易并行。

## 正确性与工程边界

Kahan 的补偿量等于本轮加法中无法表示的部分（符号按实现约定存储），所以下轮先抵消该损失；它通常显著降低累计误差，但不能精确恢复所有病态序列。对于正负大数抵消，问题本身可能病态；排序求和、更高精度或代数重构更可靠。金额应使用整数/十进制定点，不应以 Kahan 替代正确的数据类型。

## 常见误区

- Kahan 不是“总能得到精确结果”的算法。
- `sum` 的顺序不是无关紧要的实现细节。
- pairwise 的并行性不等于任意并行归约都可复现；树形顺序仍需固定。

## 练习

1. **基础**：比较普通、Kahan、pairwise 对示例序列的结果。
2. **推导**：说明为何 pairwise 的加法树高度为 $O(\log n)$。
3. **编码**：实现无切片的 pairwise，并在空列表和奇数长度上测试。
4. **开放**：设计可复现的并行求和协议，说明固定归约树的价值。

## 延伸与下一步

补偿求和减少算法引入的误差；[数值积分](/numerical-computing/numerical-integration)和蒙特卡洛模拟中仍需同时分析离散化与随机误差。
