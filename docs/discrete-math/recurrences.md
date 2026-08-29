---
courseLevel: "2（递推与分析）"
prerequisites: "递归、求和与对数"
estimatedMinutes: 50
experiment: "比较递归树预测与实际运行计数"
title: 递推关系与分治复杂度：递归树如何计算总代价
description: 从递归代码建立递推式，用递归树和主定理分析分治算法的时间与边界。
---

# 递推关系与分治复杂度：递归树如何计算总代价

## 学习目标

- 从递归函数写出含基例的递推式；
- 用递归树推导二分查找与归并排序复杂度，并审计每层工作量；
- 判断主定理适用范围及递归栈边界。

## 从一个计算问题开始

递归代码里只有一两行自调用，却可能运行百万次。归并排序每次分成两个子问题，为什么不是 $O(\log n)$？答案要同时计算每层子问题数、每个子问题工作量和树高。

## 定义与递归树

递推式由基例、子问题和非递归工作组成。归并排序满足

$$T(1)=\Theta(1),\qquad T(n)=2T(n/2)+\Theta(n).$$

第 $i$ 层有 $2^i$ 个规模 $n/2^i$ 的问题，合并总工作为 $2^i\Theta(n/2^i)=\Theta(n)$。树高为 $\log_2n$，故总时间为 $\Theta(n\log n)$。二分查找为 $T(n)=T(n/2)+\Theta(1)=\Theta(\log n)$：每层只有一个子问题。

## 算法实验：把递归树变成可检查数据

```python
from projects.algorithm_lab.recurrence_trace import (
    binary_search_worst_case_steps,
    merge_sort_levels,
    merge_sort_with_comparisons,
)

assert binary_search_worst_case_steps(16) == 4
levels = merge_sort_levels(8)
assert [level.total_merge_items for level in levels] == [8, 8, 8]

ordered, comparisons = merge_sort_with_comparisons([5, 1, 4, 2, 3, 0, 7, 6])
assert ordered == list(range(8))
assert comparisons <= 8 * 3
```

运行 `python -m unittest projects.algorithm_lab.test_recurrence_trace`。`merge_sort_levels` 限定 $n$ 为二的幂，使第 $i$ 层恰有 $2^i$ 个大小 $n/2^i$ 的子问题；测试因此能验证每一内层的 `total_merge_items` 都为 $n$，总计为 $n\log_2n$。`merge_sort_with_comparisons` 则实际排序并确认比较次数不超过这一数量级上界，而不是把递归树只当作插图。

主定理处理 $T(n)=aT(n/b)+f(n)$，比较 $f(n)$ 与 $n^{\log_ba}$：递归叶子工作、每层附加工作或两者共同主导。递归栈深度通常为树高，二分搜索为 $O(\log n)$，但不等于所有节点的总工作。

## 正确性与复杂度证据

归并的正确性可对输入长度归纳：长度 $0$ 或 $1$ 已有序；若左右递归结果有序，每次输出两者当前较小首元素，就不可能漏掉元素，也不会把更大的元素放在尚未输出的更小元素之前，故合并结果有序且是原多重集合的重排。实验还检查输入列表没有被原地修改。

对二的幂 $n$，归并树有 $\log_2n$ 个内层，每层总合并量为 $n$，故总工作为 $\Theta(n\log n)$；比较次数至多同阶。实际 Python 切片也会复制列表，这正是代码中不能把“分割”盲目视为零成本的原因。对于非二的幂，树会不均匀，但渐近结论不变；本实验拒绝它们只是为了让课程不变量保持精确可读。

## 失败案例与工程边界

主定理不能直接处理 $T(n)=T(n-1)+\Theta(1)$、不等分递归、依赖输入的分支或不规则合并。切片、复制和排序等语言操作可能将“常数工作”变成线性工作；递归还受语言栈深度限制。此时用递归树、代入法或更一般的 Akra–Bazzi 工具。

## 常见误区

- 只数递归深度，忽略同层多个子问题；
- 漏掉基例，无法论证终止；
- 机械套主定理而不检查 $a,b,f(n)$ 的形状。

## 练习

1. **基础**：推导 $T(n)=T(n/2)+\Theta(1)$。
2. **推导**：用递归树分析 $T(n)=3T(n/2)+\Theta(n)$。
3. **编码**：为归并排序计数比较和切片代价。
4. **开放**：解释快速排序最坏递推为何不能直接用主定理，并设计避免最坏输入的策略。

## 延伸与下一步

[循环不变量](/discrete-math/loop-invariants)证明单轮更新正确；递推关系说明多轮递归的总代价。继续比较 [BFS](/discrete-math/breadth-first-search) 的图规模 $O(V+E)$ 分析。
