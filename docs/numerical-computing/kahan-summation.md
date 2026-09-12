---
courseLevel: "2–3（算法稳定性）"
prerequisites: "浮点表示、循环与求和"
estimatedMinutes: 65
experiment: "比较普通、Kahan 与 pairwise 求和"
title: Kahan 与 pairwise 求和：怎样不让低位悄悄消失
description: 从舍入误差推导补偿求和和分治求和，比较稳定性、复杂度与适用边界。
---

# Kahan 与 pairwise 求和：怎样不让低位悄悄消失

## 文章元信息

- **建议阅读层级**：2–3 · 稳定算法、误差分析与工程取舍
- **前置知识**：[浮点数表示](/numerical-computing/floating-point)、[条件数](/numerical-computing/condition-number)
- **预计学习时间**：65 分钟
- **配套实验**：[浮点数错误博物馆](/projects/floating-point-museum)

## 学习目标

- 解释普通累加为何依赖输入顺序；
- 实现 Kahan 补偿求和和 pairwise 求和；
- 选择排序、补偿或更高精度的合适边界。

## 从一个计算问题开始

数学上 $10^{16}+1+1-10^{16}=2$，但二进制浮点普通累加常得到 0：当 1 加入巨大累计和时，尾数没有足够位保存它。若程序在统计、积分或财务模拟中沉默地丢失上万次这种低位，结果仍可“看起来合理”。

## 直觉与推导

一次浮点加法可写为 $\mathrm{fl}(a+b)=(a+b)(1+\delta)$，其中 $|\delta|$ 受机器精度限制。普通从左到右求和在每一步舍入，且大数先出现时小数的有效位最脆弱。

Kahan 算法用 `compensation` 保存本轮未写入 `total` 的低位：下一轮先计算 $y=x-c$，再加到和中，最后由 $(t-s)-y$ 重建新的舍入损失。它不改变数学目标 $\sum x_i$，只将被舍去的信息延迟回收。

## 手算轨迹：那一个 1 到底去了哪里

对 binary64，$10^{16}$ 附近相邻可表示数的间距是 2。因此把 1 加到 $10^{16}$ 时，`total` 保持 $10^{16}$；Kahan 不会让它立刻出现在 `total`，而是把损失以负号写进补偿量。下表的 $s$ 是旧 `total`，$c$ 是旧补偿量，$y=x-c$ 是实际要加的修正项，$t$ 是新的 `total`：

| 轮次 | $x$ | $s$ | $c$ | $y=x-c$ | $t=\mathrm{fl}(s+y)$ | 新 $c=(t-s)-y$ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $10^{16}$ | $0$ | $0$ | $10^{16}$ | $10^{16}$ | $0$ |
| 2 | $1$ | $10^{16}$ | $0$ | $1$ | $10^{16}$ | $-1$ |
| 3 | $1$ | $10^{16}$ | $-1$ | $2$ | $10^{16}+2$ | $0$ |
| 4 | $-10^{16}$ | $10^{16}+2$ | $0$ | $-10^{16}$ | $2$ | $0$ |

这解释了一个容易误读的细节：第二轮的 `compensation=-1` 不是“累计和少了负一”，而是按代码的符号约定记录“下一轮应额外加回 1”。第三轮因此把当前输入 1 修正为 2，恰好跨过该尺度下的一个 ULP。普通左到右求和没有这份状态，两个 1 都会消失，最后得到 0。

`kahan_sum_trace` 将这六个状态字段逐轮公开，`kahan_sum_trace_certificate` 从原输入重放全部转换；它会拒绝只把最终和改成 2，或把第二轮补偿的符号偷偷改掉的记录。轨迹暴露每个输入值和舍入路径，只适合公开教学数据。

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

项目中的可检查版本还可直接把手算表与实现对齐：

```python
from projects.floating_point_museum.examples import (
    kahan_sum_trace,
    kahan_sum_trace_certificate,
)

values = [1e16, 1.0, 1.0, -1e16]
result, trace = kahan_sum_trace(values)
assert result == 2.0
assert [event.corrected for event in trace] == [1e16, 1.0, 2.0, -1e16]
assert [event.compensation_after for event in trace] == [0.0, -1.0, 0.0, 0.0]
assert kahan_sum_trace_certificate(values, result, trace)
```

两者时间均为 $O(n)$。Kahan 使用 $O(1)$ 额外空间；上面的递归 pairwise 实现因切片额外占空间，生产实现应以索引或迭代树避免它。pairwise 将误差增长从线性层数改善为对数层数，且易并行。

## 正确性与工程边界

表中的一步能精确解释补偿更新：若 $t=\mathrm{fl}(s+y)$，表达式 $(t-s)-y$ 是这次加法相对精确增量的残余（以本实现的符号保存）。下一轮构造 $y=x-c$，便把该残余优先带入下一次加法。该局部关系解释算法的设计动机，并不推出“每一步或每个序列都精确”。Kahan 通常显著降低累计误差，但不能精确恢复所有病态序列。对于正负大数抵消，问题本身可能病态；排序求和、更高精度或代数重构更可靠。金额应使用整数/十进制定点，不应以 Kahan 替代正确的数据类型。

## 常见误区

- Kahan 不是“总能得到精确结果”的算法。
- `sum` 的顺序不是无关紧要的实现细节。
- pairwise 的并行性不等于任意并行归约都可复现；树形顺序仍需固定。

## 练习

1. **基础**：不用运行程序，补全 $[10^{16},1,1,-10^{16}]$ 的 Kahan 表中第 2、3 轮的 $y,t,c$，再与普通累加比较。
2. **推导**：从 $t=\mathrm{fl}(s+y)$ 说明 `(t - s) - y` 在精确算术下为何为 0，以及浮点下它为何能记录舍入残余；说明这不是全局精度保证。
3. **调试**：若第二轮代码误写为 `compensation = corrected - (next_total - total)`，预测第三轮 `corrected` 的符号与最终结果；用轨迹证书解释该错误为何可定位。
4. **编码**：实现无切片的 pairwise，并在空列表和奇数长度上测试；构造两种固定树顺序，比较它们对同一病态序列的结果。
5. **开放**：设计可复现的并行求和协议，说明固定归约树、数据分块和浮点格式的价值。

## 练习答案提示

1. 第 2 轮 $y=1,t=10^{16},c=-1$；第 3 轮 $y=2,t=10^{16}+2,c=0$。普通累加没有 $c$，故两个 1 都在加入时丢失。
2. 精确算术时 $t=s+y$，所以 $(t-s)-y=0$；浮点的非零值正是该次圆整后的残余。这只描述单步状态，不排除后续抵消或溢出。
3. 错误符号会使第二轮得到 $c=1$，第三轮变成 $y=0$，因而不能补回低位；重放器逐字段比对预期状态，先在第二个事件拒绝。
4. 传递索引区间而非切片；空区间返回加法单位元 0，单元素直接返回，奇数长度需明确哪一半多一个元素。比较时还应记录每个内部节点的左右子树顺序。
5. 固定分块规则、块内顺序和二叉归约树，并记录数据版本与浮点格式；否则调度变化会改变舍入路径，难以复现差异。

## 延伸与下一步

补偿求和减少算法引入的误差；[数值积分](/numerical-computing/numerical-integration)和蒙特卡洛模拟中仍需同时分析离散化与随机误差。
