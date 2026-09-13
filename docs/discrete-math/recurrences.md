---
courseLevel: "2（递推与分析）"
prerequisites: "递归、求和与对数"
estimatedMinutes: 65
experiment: "重放递归树报告、任意规模的精确最坏比较递推，并比较模型工作量与实际比较次数"
title: 递推关系与分治复杂度：递归树如何计算总代价
description: 从递归代码建立递推式，用递归树和主定理分析分治算法，并区分合并工作模型与精确最坏比较次数。
---

# 递推关系与分治复杂度：递归树如何计算总代价

## 学习目标

- 从递归函数写出含基例的递推式；
- 用递归树推导二分查找与归并排序复杂度，并重放每层工作与总工作；
- 对任意输入规模推导归并排序的精确最坏比较递推与闭式；
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
    merge_sort_comparison_bound_certificate,
    merge_sort_comparison_bound_report,
    merge_sort_tree_certificate,
    merge_sort_tree_report,
    merge_sort_with_comparisons,
)

assert binary_search_worst_case_steps(16) == 4
report = merge_sort_tree_report(8)
assert report["total_merge_items"] == 24
assert all(report["certificate"].values())
assert merge_sort_tree_certificate(8, report)

comparison_bound = merge_sort_comparison_bound_report(6)
assert comparison_bound["recurrence_worst_case_comparisons"] == 11
assert comparison_bound["closed_form_worst_case_comparisons"] == 11
assert merge_sort_comparison_bound_certificate(6, comparison_bound)

ordered, comparisons = merge_sort_with_comparisons([5, 1, 4, 2, 3, 0, 7, 6])
assert ordered == list(range(8))
assert comparisons <= 8 * 3
```

运行 `python -m unittest projects.algorithm_lab.test_recurrence_trace`。`merge_sort_tree_report` 限定 $n$ 为二的幂，使第 $i$ 层恰有 $2^i$ 个大小 $n/2^i$ 的子问题。它明确记录层数、每层的子问题分割与合并量；证书同时重放“深度等于 $\log_2 n$”“每层刚好分割 $n$ 个元素”和“总量为 $n\log_2 n$”。因此，改写某一层的规模、深度或总量都会让 `merge_sort_tree_certificate` 失败。`merge_sort_with_comparisons` 则实际排序并确认比较次数不超过这一数量级上界，而不是把递归树只当作插图。

主定理处理 $T(n)=aT(n/b)+f(n)$，比较 $f(n)$ 与 $n^{\log_ba}$：递归叶子工作、每层附加工作或两者共同主导。递归栈深度通常为树高，二分搜索为 $O(\log n)$，但不等于所有节点的总工作。

## 任意规模的精确比较递推

“合并 $n$ 个元素的工作是 $n$”是一个方便的成本模型，但元素比较的精确最大值是 $n-1$：当一侧先耗尽时，另一侧的剩余元素不必再比较。对任意正整数 $n$，两半大小为 $\lfloor n/2\rfloor$ 和 $\lceil n/2\rceil$，故最坏比较次数满足

$$C(1)=0,\qquad C(n)=C(\lfloor n/2\rfloor)+C(\lceil n/2\rceil)+n-1.$$

令 $h=\lceil\log_2n\rceil$，这个递推的闭式为

$$C(n)=nh-2^h+1.$$

例如 $n=6$ 时，$C(6)=2C(3)+5=11$，而 $6\lceil\log_2 6\rceil=18$ 只是宽松的同阶上界。`merge_sort_comparison_bound_report` 同时重放递推值、闭式、分割大小与 $h$；这使非二的幂不再被迫伪装成完整的对称递归树。

这条公式不表示每个长度为 6 的输入都会做 11 次比较。实际比较次数取决于元素交错方式；它只是在存在能让各次合并尽量晚耗尽一侧的输入时达到的最大值。与之相对，`merge_sort_with_comparisons` 记录某个具体输入的实际计数，因此该计数必须不超过 $C(n)$，却通常小于它。

## 正确性与复杂度证据

归并的正确性可对输入长度归纳：长度 $0$ 或 $1$ 已有序；若左右递归结果有序，每次输出两者当前较小首元素，就不可能漏掉元素，也不会把更大的元素放在尚未输出的更小元素之前，故合并结果有序且是原多重集合的重排。实验还检查输入列表没有被原地修改。

对二的幂 $n$，归并树有 $\log_2 n$ 个内层，每层总合并量为 $n$，故总工作为 $\Theta(n\log n)$；比较次数至多同阶。报告不是只检查最终的 $24$：它逐层保存 $2^i \times (n/2^i)=n$，再将所有内层相加。实际 Python 切片也会复制列表，这正是代码中不能把“分割”盲目视为零成本的原因。对于非二的幂，树会不均匀，但渐近结论不变；对称工作模型仍拒绝它们以保持该不变量精确可读，精确比较报告则用地板/天花板递推处理它们。

## 失败案例与工程边界

主定理不能直接处理 $T(n)=T(n-1)+\Theta(1)$、不等分递归、依赖输入的分支或不规则合并。切片、复制和排序等语言操作可能将“常数工作”变成线性工作；递归还受语言栈深度限制。此时用递归树、代入法或更一般的 Akra–Bazzi 工具。

本报告也不测量墙钟时间，更不声称元素比较恰好等于合并元素数：数据顺序会改变比较次数，运行环境会改变耗时。精确比较报告只证明给定分割规则下的最坏**元素比较**数；它不计切片、分配、缓存、比较器成本或 Python 解释器开销。用 `merge_sort_with_comparisons` 的实际计数来观察另一个量，不能把它与递归树按元素工作模型混为一谈。

## 常见误区

- 只数递归深度，忽略同层多个子问题；
- 漏掉基例，无法论证终止；
- 机械套主定理而不检查 $a,b,f(n)$ 的形状。

## 练习

1. **基础**：推导 $T(n)=T(n/2)+\Theta(1)$。
2. **推导**：用递归树分析 $T(n)=3T(n/2)+\Theta(n)$。
3. **编码**：为归并排序计数比较和切片代价；再验证非二的幂 $n=6$ 的实际比较数不超过 $C(6)=11$。
4. **开放**：解释快速排序最坏递推为何不能直接用主定理，并设计避免最坏输入的策略。

## 练习答案提示

1. 展开后每层只有一个子问题，深度约为 $\log_2 n$，每层增加常数工作；写出基例再求和。
2. 第 $i$ 层有 $3^i$ 个问题、每个附加工作约为 $n/2^i$，层工作为 $n(3/2)^i$，因此叶层主导。
3. 将“元素比较次数”和“切片复制元素数”分开计数。$C(6)=11$ 来自 $2C(3)+5$，是最坏比较数，不是每份输入的必然计数；用多种规模比较增长，避免只看单次运行时间。
4. 最坏快速排序是 $T(n)=T(n-1)+\Theta(n)$，子问题不按固定比例缩小；随机主元或三路划分缓解风险，但需区分期望与最坏保证。

## 延伸与下一步

[循环不变量](/discrete-math/loop-invariants)证明单轮更新正确；递推关系说明多轮递归的总代价。继续比较 [BFS](/discrete-math/breadth-first-search) 的图规模 $O(V+E)$ 分析。
