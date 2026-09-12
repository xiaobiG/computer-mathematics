---
title: 动态规划：状态设计、最优子结构与 DAG 视角
description: 以加权活动选择为例推导动态规划递推、回溯重建与 DAG 最长路视角，解释它为何取代错误贪心。
courseLevel: "2（算法设计与证明）"
prerequisites: "递推、排序、贪心反例与渐进复杂度"
estimatedMinutes: 75
experiment: "从任务合同选择贪心或加权活动选择 DP，并与穷举、最早结束贪心对拍"
---

# 动态规划：状态设计、最优子结构与 DAG 视角

## 学习目标

读完后，你能从问题目标设计状态和转移；推导加权活动选择的递推；实现价值最优解与具体选择的回溯；用归纳证明正确性；并区分“重叠子问题”与仅仅写递归的区别。更重要的是，你会先把“最优”翻译为可检查的目标与不变量，而不是看到区间就默认使用某个算法。

## 从贪心反例到状态

在活动选择中，每个活动价值相同，最早结束贪心可选最多个。若活动附带收益，规则失效：一个结束很早但收益 1 的活动，可能挡住收益 100 的长活动。此时“先做哪一个”不能只看局部；需要保留多个可能过去的最优结果。

将活动按结束时间排序为 $1,\ldots,n$。令 $p(j)$ 是活动 $j$ 之前最后一个与它兼容的活动下标（无则 0）；令 $w_j$ 是价值。状态 $OPT(j)$ 表示前 $j$ 个活动可取得的最大总价值。

## 直觉与定义：选或不选，没有第三种

最优解对活动 $j$ 只有两种情况：

- 不选 $j$，价值至多 $OPT(j-1)$；
- 选 $j$，此前只能从前 $p(j)$ 个活动选，价值为 $w_j+OPT(p(j))$。

因此

$$OPT(j)=\max\{OPT(j-1),\;w_j+OPT(p(j))\},\qquad OPT(0)=0.$$

这不是猜公式：任何可行解都落在两种情况之一；各情况中的前缀若不是最优，可替换成更优前缀而不破坏兼容性，便与“原解最优”矛盾。这同时给出最优子结构的证明。

## 可运行实现与回溯

```python
from projects.algorithm_lab.weighted_activity import (
    brute_force_best_value,
    compatible_schedule,
    weighted_activity_trace,
    weighted_activity_trace_certificate,
    weighted_activity_selection,
)

activities = [(0.0, 2.0, 1.0, "short"), (0.0, 4.0, 100.0, "valuable")]
value, chosen = weighted_activity_selection(activities)

assert value == 100.0                     # 最早结束贪心会选错 short
assert compatible_schedule(chosen)
assert value == brute_force_best_value(activities)

value, chosen, trace = weighted_activity_trace(activities)
assert weighted_activity_trace_certificate(activities, value, chosen, trace)
```

实验室的 `brute_force_best_value` 明确限制在 18 个活动以内，作为 DP 的测试 oracle 而非算法替代；它验证回溯出的活动两两兼容，且价值确实达到小规模全局最优。`weighted_activity_trace` 还记录每个前缀的兼容前缀、跳过值、选取值与最终决策；独立证书会重放两条 DAG 边，拒绝被篡改的状态。二分搜索每个 $p(j)$ 需 $O(\log n)$，总时间 $O(n\log n)$（排序也相同），状态数组和回溯空间 $O(n)$。若只需最优值且能流式计算兼容关系，可讨论空间压缩；若要重建方案，必须保留足够决策信息。

## 构造实验：先写任务合同，再让目标决定状态

“安排会议”不是完整的算法输入。读者要明确：端点相碰能否共存、目标是最多完成多少项还是最大收益、以及什么结果算通过。`diagnose_activity_task` 不从自然语言猜这些选择；它要求你提交合同，然后把目标映射到方法、状态含义和验收不变量。

```python
from projects.algorithm_lab.weighted_activity import diagnose_activity_task

task = {
    "interval_semantics": "half_open",  # [finish, start] 相等时可以衔接
    "objective": "maximize_value",
    "acceptance_invariant": "compatible_schedule_and_maximum_total_value",
    "activities": [
        {"start": 0, "finish": 2, "value": 1, "name": "short"},
        {"start": 0, "finish": 4, "value": 100, "name": "valuable"},
        {"start": 4, "finish": 5, "value": 5, "name": "after"},
    ],
}
diagnosis = diagnose_activity_task(task)
assert diagnosis["recommended_method"] == "prefix_dag_dynamic_programming"
assert diagnosis["chosen_names"] == ["valuable", "after"]
assert diagnosis["objective_value"] == diagnosis["oracle_value"] == 105.0
assert diagnosis["earliest_finish_value"] == 6.0
```

把同一组时间窗改成 `maximize_count` 时，去掉每项 `value`，并把验收量改为 `compatible_schedule_and_maximum_cardinality`；诊断器会选择最早结束贪心，状态是 `current_end`，而不是 $OPT(j)$。反过来，价值目标下即便这一个输入恰好让最早结束得到同样价值，诊断仍会指出**首先失效的前提**：交换一个结束更早的活动并不保证保持总价值。因此不能把一次幸运测试当成加权贪心的证明。

小于等于 `oracle_limit`（默认 18）项时，结果还会与指数穷举比较；更大输入会保留“兼容且达到声明目标”的验收语义，但明确不运行穷举。合同拒绝闭区间语义、与目标不匹配的字段或验收量、重复名称及非法端点，避免把另一个问题偷偷送进原有证明。

## DAG 视角与正确性

将每个前缀状态 $0,1,\ldots,n$ 看成 DAG 顶点：有边 $j-1\to j$ 权重 0（不选），有边 $p(j)\to j$ 权重 $w_j$（选）。递推正是在拓扑序上求最长路。DAG 无环保证已依赖状态都先被计算。

归纳证明也直接：假设 $OPT(0),\ldots,OPT(j-1)$ 正确。任一前 $j$ 活动的最优解要么不含 $j$，上界为 $OPT(j-1)$；要么含 $j$，剩余部分上界为 $OPT(p(j))$。算法取两上界较大者，并各自可由对应构造达到，所以 $OPT(j)$ 正确。

## 可验证实验

对不超过 12 个活动的随机小输入，枚举 $2^n$ 子集，过滤兼容集后比较价值与函数返回值。还应构造贪心失败例：`(0,2,1,'short'), (0,4,100,'valuable')`，最早结束规则会选价值 1，而 DP 应选价值 100。

测试回溯时不要只比较活动名顺序：断言返回活动两两兼容、价值和等于 `best_value`、并与穷举最优值相同。再篡改一条 `trace` 的选取值或兼容前缀，确认 `weighted_activity_trace_certificate` 拒绝它；这分别审计“每步按递推更新”和“小输入达到全局最优”，而不是把其中任一项误当作完整证明。

## 失败案例与工程边界

- **状态遗漏关键约束**：若活动有资源类别、冷却时间或多个会议室，只用“最后结束时间”状态可能不够。
- **循环依赖**：一般图的最长路不是 DAG DP，可能有正环；先确认状态依赖图可拓扑排序。
- **价值为负**：本实现拒绝它以保持“可选空集”语义清晰；允许负价值时应明确是否必须选择活动。
- **规模爆炸**：多维背包的状态空间可能是参数乘积；递推正确不代表可承受。

## 常见误区

1. “动态规划就是递归加缓存。”不完整：关键是状态、转移、初值和无环依赖；递归只是实现方式。
2. “有重叠子问题就一定值得 DP。”错误：状态空间过大时缓存可能更糟。
3. “只求最大值，不必关心选择。”错误：业务常需要方案本身，回溯设计应从开始考虑。
4. “DP 总比贪心慢。”错误：本题两者都可为 $O(n\log n)$；区别是适用目标与证明，不只是速度。

## 练习

1. **基础题**：为“最多完成预约”与“最大化已确认收入”各写一个任务合同；说明两者为何需要不同的 `objective`、字段和验收不变量。
2. **推导题**：写出上面归纳证明的基例、归纳假设和归纳步。
3. **编码题**：先用 `diagnose_activity_task` 构造一个会让最早结束亏损的收益任务，再实现穷举对拍器随机验证 `weighted_activity_selection`；加入相同结束时间的测试。
4. **开放题**：将问题扩展为两间会议室，讨论状态是否仍是一维前缀，并提出可行算法方向。

## 练习答案提示

1. 数量任务声明 `maximize_count`，活动没有价值字段，验收最大基数；收益任务声明 `maximize_value`，每项必须有非负价值，验收最大总价值。两者都先声明半开区间，但前者状态是结束边界，后者才需要前缀 $OPT(j)$。
2. 基例是空前缀；归纳步按最优解是否含第 $j$ 个活动分为两类，并说明两种上界都能由已计算状态达到。
3. 对拍器既要比较最优价值，也要检查回溯活动两两兼容；相同结束时间需固定平局规则，避免把不确定顺序误判成错误。
4. 两间会议室时“最后结束时间”可能需要记录两个资源的状态或改用流/匹配模型；先评估状态数量是否仍可承受。

## 延伸

本题把[贪心交换论证](/discrete-math/greedy-exchange-arguments)的失败目标转为 DP。继续学习编辑距离、背包和最长递增子序列；它们分别展示网格 DAG、容量维度和状态优化的不同设计模式。
