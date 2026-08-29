---
title: Kahan 求和：减少累计误差
description: 用一个补偿变量找回逐步相加时丢失的低位信息。
---

# Kahan 求和：减少累计误差

## 普通求和的问题

浮点数精度有限。把极小数加入极大累计和时，极小数的低位可能被舍去；大量重复后，误差会累积。

Kahan 求和保存上一步丢失的部分，并在下一次相加时补回：

```python
def kahan_sum(values):
    total = 0.0
    compensation = 0.0
    for value in values:
        corrected = value - compensation
        next_total = total + corrected
        compensation = (next_total - total) - corrected
        total = next_total
    return total
```

## 何时使用

它适用于大量浮点累计，如统计量、积分和财务模拟。代价是额外少量算术操作；对于极端病态数据，仍应结合排序求和、更高精度或问题重构。

## 练习

比较 `sum([1e16, 1, 1, -1e16])` 与 `kahan_sum` 的输出。为什么数学上结果为 2，而普通累加可能丢失它？
