---
title: 项目：算法可视化实验室
description: 用图搜索、拓扑排序、最大流轨迹和 3-SAT 验证器连接不变量、最优证书与复杂度。
---

# 项目：算法可视化实验室

## 目标

这个最小实验室不是绘制动画，而是输出算法每次推进后的状态和候选解验证结果。读者可以把每一行轨迹与 BFS 的层级不变量、Kahn 算法的入度不变量或最大流的残量网络对应起来，也可对比 3-SAT 的线性验证与指数搜索。BFS 现在同时保存首次发现父指针，并用父路径、逐边层级不等式与队列重放验证无权最短路；Dijkstra 还提供独立的最短路证书检查：父指针证明可达路径，逐边松弛不等式证明不存在更短路径；加权活动选择会重放每个前缀 DAG 状态的“选/不选”转移；Kahn 轨迹则可重放验证每次入度更新、合法拓扑序或剩余正入度的环证据。

## 数学连接

- [循环不变量](/discrete-math/loop-invariants)：每轮循环前后保持的结论；
- [BFS](/discrete-math/breadth-first-search)：无权图中最短步数；
- [图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)：依赖解除、拓扑序与有向环；
- [渐进复杂度](/discrete-math/asymptotic-complexity)：为何邻接表下为 $O(V+E)$。
- [P、NP 与多项式归约](/discrete-math/p-np-reductions)：候选解验证为何不等于快速搜索。
- [Floyd–Warshall](/discrete-math/floyd-warshall)：重放允许中间点集合逐步扩展的全源最短路动态规划。
- [递推关系与分治复杂度](/discrete-math/recurrences)：用递归树层级和实际比较次数审计 $n\log n$ 工作量。
- [渐进复杂度](/discrete-math/asymptotic-complexity)：用操作计数和双指针轨迹区分线性、二次与指数增长。
- [集合、关系、等价类与偏序](/discrete-math/sets-relations-orders)：用性质报告和等价类划分验证有限关系。
- [Dijkstra 交互轨迹实验](/discrete-math/dijkstra)：在浏览器中逐步查看最小堆、确定集合、松弛与过期条目，再用堆的确定顺序与松弛轨迹验证非负最短路。
- [Bellman–Ford](/discrete-math/bellman-ford)：用冻结轮次的松弛轨迹验证负边正确性，并报告可达负环。
- [最大流最小割](/discrete-math/max-flow-min-cut)：增广路和残量可达集如何构成最优证书。
- [动态规划](/discrete-math/dynamic-programming-dag)：前缀 DAG 的最长路、回溯方案与小规模穷举对拍。

## 运行

```bash
python projects/algorithm_lab/bfs_trace.py
python -m unittest projects.algorithm_lab.test_binary_search_trace
python -m unittest projects.algorithm_lab.test_weighted_activity
python -m unittest projects.algorithm_lab.test_dfs_trace
python -m unittest projects.algorithm_lab.test_strongly_connected
python projects/algorithm_lab/sat_verifier.py
python -m unittest projects.algorithm_lab.test_floyd_warshall
python -m unittest projects.algorithm_lab.test_dijkstra_trace
python -m unittest projects.algorithm_lab.test_bellman_ford_trace
python -m unittest projects.algorithm_lab.test_recurrence_trace
python -m unittest projects.algorithm_lab.test_complexity_counts
python -m unittest projects.algorithm_lab.test_relations
python -m unittest projects.algorithm_lab.test_max_flow
python -m unittest discover -s projects/algorithm_lab -p "test_*.py"
```

输出中的 `distance` 表示当前节点与起点相差的边数，`queue` 表示本轮扩展后待处理的边界。

拓扑排序模块可在 Python 中直接观察：

```python
from projects.algorithm_lab.topological_trace import topological_trace

# 边表示“前置任务 -> 依赖它的后续任务”。
order, events = topological_trace({"compile": ["build"], "build": []})
print(order)          # ['compile', 'build']
print(events[-1])     # 最后一次移除后的顺序与就绪队列
assert topological_trace({"a": ["b"], "b": ["a"]})[0] is None
```

`None` 不是“没有找到一个恰好顺序”，而是 Kahn 算法已证明剩余顶点构成有向环：没有入度为零的下一步可执行任务。

## 浏览器内 BFS 轨迹

下面的面板把队列、首次发现、距离与前驱放在同一时间轴上。点击“下一步”后，先观察图上的队列前沿，再核对表中首次记录的距离；切换示例图可验证：即使一个节点能从多条路径到达，BFS 只在首次发现时赋值，因此距离按层单调出现。

<BfsTraceExplorer />

这个交互面板用于重放固定的小图，而非替代仓库中的 `projects/algorithm_lab/bfs_trace.py`。真实图输入应继续由 Python 模块的轨迹证书和单元测试检查；浏览器面板的价值是让不变量在每一轮可见。

## 浏览器内最短路算法对照

<ShortestPathComparisonExplorer />

面板在无权、非负权、负边和负环图之间切换，并将“拒绝前提”与“不可达”分开显示。配套的 `shortest_path_comparison.py` 会从同一边表重建四种算法的适用卡，证书也会检查被篡改的拒绝理由。

3-SAT 模块将变量写为非零整数，负号表示否定：

```python
from projects.algorithm_lab.sat_verifier import find_satisfying_assignment, verify_assignment

formula = ((1, -2, 3), (-1, 2), (3,))
witness = find_satisfying_assignment(formula)
assert witness is not None and verify_assignment(formula, witness)
```

`verify_assignment` 只扫描公式的文字，而 `find_satisfying_assignment` 故意枚举全部赋值；前者说明证书可验证，后者仅是指数搜索的教学基线。

## 可观察的实验

1. 改变邻居顺序，观察路径可能变化但最短距离不变；
2. 给图加入一条边，检查轨迹在哪一层提前到达目标；
3. 将边加上不同权重，解释为什么此算法不再适用，并转向 [Dijkstra](/discrete-math/dijkstra)。
4. 为一张依赖图加入环，观察拓扑序变为 `None`；删除一条环边后，解释哪一个入度变为零；
5. 写出一个不可满足公式，观察穷举搜索返回 `None`；再说明这不是 3-SAT 没有更好算法的证明。
6. 为一张含负边但无负环的图计算全源距离；加入负环后，解释为什么结果应被拒绝。
7. 对含环图检查 DFS 每个顶点只发现、完成一次；比较其路径与 BFS 最短路为何不同。
8. 将有向依赖图压缩为强连通分量，先报告循环组件，再对凝聚图做拓扑排序。
9. 对一个容量网络列出每条增广路，并计算最终残量可达集合的割容量，核对其等于总流量。
10. 对一张带非负边权的图检查 Dijkstra 轨迹中的确定距离单调和 `shortest_path_certificate`；篡改一个距离，确认松弛不等式或父路径证书会失败；再加入一条负边，确认实现拒绝该前提。
11. 对含重复值的小数组穷举运行二分查找，检查每步候选区间保留目标且未命中时严格缩小；再传入未排序数组，确认前提被显式拒绝。
12. 对不超过 18 个加权活动比较 DP 与穷举最优值；构造“最早结束但价值极低”的反例，并核对回溯活动彼此兼容。
13. 对加权活动的 `weighted_activity_trace` 篡改一个 `take_value` 或兼容前缀，确认状态轨迹证书拒绝它；再说明该证书为何不能取代最优子结构证明。

## 工程边界

本项目使用内存中的小型邻接表，旨在说明算法状态；真实大规模图需要考虑内存布局、输入格式和性能分析。
