---
courseLevel: "2（正确性证明）"
prerequisites: "命题逻辑、循环与有序数组"
estimatedMinutes: 50
experiment: "为二分查找编写属性测试"
title: 循环不变量：二分查找为什么不会漏掉答案
description: 用初始化、保持与终止三步证明循环算法的正确性。
---

# 循环不变量：二分查找为什么不会漏掉答案

## 文章元信息

- **建议阅读层级**：2 · 推导与算法
- **前置知识**：[渐进复杂度](/discrete-math/asymptotic-complexity)、有序数组与半开区间
- **预计学习时间**：50 分钟
- **配套实验**：[算法可视化实验室](/projects/algorithm-lab)

## 学习目标

读完后，你能把初始化、保持和终止组织为循环正确性证明；为半开区间二分查找写出不变量和终止度量；实现可重放的查找轨迹；并能指出未排序输入、区间约定混用和不严格缩小为何会使结论失效。

## 从一个计算问题开始

二分查找一次丢弃半个区间。若目标刚好被丢掉，程序可能依然结束却给出错误的“不存在”。代码的每个分支凭什么安全？答案不是“区间变小了”，而是一个始终保持为真的命题。

## 直觉模型

将待查找区间记为半开区间 $[left,right)$：包含 `left`，不包含 `right`。每轮都保留“答案仍可能在内”的候选箱子；丢弃一半时，要能说明其中每个元素都不可能是答案。

## 严格定义与推导

循环不变量是每次循环开始时成立的命题。证明循环正确性需要三步：

1. **初始化**：第一次循环前成立；
2. **保持**：若本轮开始时成立，执行一次后仍成立；
3. **终止**：循环条件为假时，不变量能推出后置条件。

对升序数组 `a` 的不变量为：若 `target` 出现在 `a` 中，则它的某个下标位于 $[left,right)$。初始为 $[0,n)$，显然覆盖全数组。令 $mid=left+\lfloor(right-left)/2\rfloor$：

- 若 $a[mid]<target$，排序性说明所有 $i\le mid$ 都不是目标，令 $left=mid+1$；
- 若 $a[mid]>target$，所有 $i\ge mid$ 都不是目标，令 $right=mid$；
- 相等则直接返回。

每次未返回时，区间长度至少减一，因此有限数组上必终止。终止时区间为空；不变量说明目标若存在仍应在空区间，矛盾，所以返回 `-1` 正确。

## 算法实现与复杂度

```python
from projects.algorithm_lab.binary_search_trace import (
    binary_search_trace,
    trace_respects_invariant,
)

values = [1, 3, 5, 7]
result, steps = binary_search_trace(values, 4)

assert result == -1
assert trace_respects_invariant(values, 4, result, steps)
assert steps[-1].next_left == steps[-1].next_right  # 终止时是空区间
```

每个轨迹事件都记录更新前后的半开区间与比较结果；`trace_respects_invariant` 独立检查“目标若存在仍在候选区间中”以及“未命中时区间严格缩小”。测试还穷举包含重复值的小型有序数组，避免只凭两个示例相信边界正确。

区间长度每轮至多约减半，时间复杂度为 $O(\log n)$，额外空间为 $O(1)$。这份证明同时解释了为何不能把更新写成 `left = mid`：当 `left == mid` 时区间可能不再缩小，终止性失效。

## 从“找到一个”到“找到边界”：`lower_bound`

真实程序更常问的是“应插到哪里”，或“重复值块从哪里开始”。定义

$$
p=\min\{i\in\{0,\ldots,n\}: i=n\ \text{或}\ a_i\ge target\}。
$$

这个定义允许 $p=0$ 和 $p=n$，所以空数组、全部元素较小和重复值都不需要额外分支。此时比“目标还在候选区间”更强、也更有用的不变量是：

$$
\forall i<left,\ a_i<target;\qquad
\forall i\ge right,\ a_i\ge target;\qquad
0\le left\le right\le n.
$$

取中点后，若 $a_{mid}<target$，则 `mid` 及其左侧都已证明不能是边界，更新 `left = mid + 1`；否则 `mid` 及右侧仍可能包含第一个不小于目标的元素，更新 `right = mid`。两种更新都保持上述三部分命题，且候选区间严格缩小。停止时 `left == right == p`，左右两个已排除区间恰好给出定义。

```python
from projects.algorithm_lab.binary_search_trace import (
    lower_bound_trace,
    lower_bound_trace_respects_invariant,
)

values = [1, 3, 3, 3, 7]
index, steps = lower_bound_trace(values, 3)

assert index == 1                 # 第一个 3，而不是任意一个 3
assert lower_bound_trace_respects_invariant(values, 3, index, steps)
```

验证器重放每次更新，并检查 `left` 左侧严格小于目标、`right` 右侧不小于目标。它把“返回值看起来正确”升级为可独立核查的边界证书。

## 失败案例与工程边界

二分查找的前提是数组按同一比较规则有序。实验实现会拒绝未排序输入；许多库为了性能不会做这一步，因此对未排序数组运行通常仍会终止，却没有正确性保证。浮点数、字符串本地化排序或比较器不满足传递性时，也必须先明确“有序”的语义。

## 常见误区

- 混用闭区间 `[left,right]` 与半开区间 `[left,right)` 的更新规则。
- 只证明“能找到”而未证明循环一定终止。
- 认为不变量只能用于搜索；累加、双指针、堆和图遍历也都需要它。

## 练习

1. **基础**：写出寻找第一个不小于 `target` 的半开区间不变量。
2. **推导**：证明上面程序最多执行 $\lceil\log_2(n+1)\rceil$ 次未命中的迭代。
3. **编码**：阅读 `lower_bound_trace` 的轨迹，篡改一次更新并让验证器拒绝它；再测试空数组、重复元素和所有元素小于目标。
4. **开放**：为滑动窗口中“窗口和不超过阈值”的算法设计一个不变量和终止度量。

## 练习答案提示

1. 用半开区间 `[left, right)` 表示仍可能成为答案的位置；分别说明左侧与右侧各排除了什么。
2. 每次未命中后区间长度至少减半；从长度 $n$ 缩到零或一时再取上整。
3. `lower_bound` 的返回值允许等于数组长度；验证器应同时检查左侧全小于、右侧全不小于和每步严格缩小；把空数组、全小于和重复块当作三个独立契约。
4. 将“窗口合法”与“左端点只前进”分开写；终止度量可取左右指针到末端的剩余距离。

## 延伸与下一步

循环不变量证明局部更新不会丢失答案；[Dijkstra](/discrete-math/dijkstra)会把这种思想扩展为“已确定节点的距离永远最短”。
