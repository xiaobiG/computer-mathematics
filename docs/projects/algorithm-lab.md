---
title: 项目：算法可视化实验室
description: 用 BFS、拓扑排序状态轨迹和 3-SAT 验证器连接不变量、依赖环与复杂度。
---

# 项目：算法可视化实验室

## 目标

这个最小实验室不是绘制动画，而是输出算法每次推进后的状态和候选解验证结果。读者可以把每一行轨迹与 BFS 的层级不变量、或 Kahn 算法的入度不变量对应起来，也可对比 3-SAT 的线性验证与指数搜索。

## 数学连接

- [循环不变量](/discrete-math/loop-invariants)：每轮循环前后保持的结论；
- [BFS](/discrete-math/breadth-first-search)：无权图中最短步数；
- [图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)：依赖解除、拓扑序与有向环；
- [渐进复杂度](/discrete-math/asymptotic-complexity)：为何邻接表下为 $O(V+E)$。
- [P、NP 与多项式归约](/discrete-math/p-np-reductions)：候选解验证为何不等于快速搜索。
- [Floyd–Warshall](/discrete-math/floyd-warshall)：用中间点集合做全源最短路动态规划。

## 运行

```bash
python projects/algorithm_lab/bfs_trace.py
python -m unittest projects.algorithm_lab.test_dfs_trace
python projects/algorithm_lab/sat_verifier.py
python -m unittest projects.algorithm_lab.test_floyd_warshall
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

## 工程边界

本项目使用内存中的小型邻接表，旨在说明算法状态；真实大规模图需要考虑内存布局、输入格式和性能分析。
