---
title: 循环不变量：二分查找为什么不会漏掉答案
description: 用一个始终为真的命题证明循环算法的正确性。
---

# 循环不变量：二分查找为什么不会漏掉答案

## 先问一个问题

二分查找每次丢弃一半区间。它凭什么确认被丢弃的部分不包含目标？答案不是“看起来合理”，而是一个可验证的循环不变量。

## 定义

循环不变量是在每次循环开始前都成立的命题。证明循环正确性通常检查三件事：

1. 初始化前它成立；
2. 一次循环后它仍成立；
3. 循环停止时，它能推出所需结论。

## 二分查找的证明

在有序数组 `a` 中寻找 `target`，维护半开区间 `[left, right)`。不变量为：

> 如果 `target` 出现在数组中，那么它一定在 `[left, right)` 内。

初始区间覆盖整个数组。令 `mid = left + (right - left) // 2`：

- 若 `a[mid] < target`，有序性说明 `mid` 及左侧不可能是答案，令 `left = mid + 1`；
- 否则答案不在 `mid` 的右侧，令 `right = mid`。

区间长度严格缩短。结束时 `left == right`，区间为空；若未提前返回，按不变量可知目标不存在。

```python
def binary_search(a, target):
    left, right = 0, len(a)
    while left < right:
        mid = left + (right - left) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            left = mid + 1
        else:
            right = mid
    return -1
```

## 常见误区

`right` 设为闭区间端点还是开区间端点都可以，但不变量、循环条件和更新规则必须属于同一套约定。混用 `[left, right]` 与 `[left, right)` 是典型的边界错误来源。

## 练习

给出“寻找第一个不小于 `target` 的元素”的不变量，并据此改写代码。
