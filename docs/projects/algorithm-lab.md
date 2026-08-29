---
title: 项目：算法可视化实验室
description: 用 BFS 与拓扑排序的状态轨迹连接队列、不变量、最短路径和依赖环检测。
---

# 项目：算法可视化实验室

## 目标

这个最小实验室不是绘制动画，而是输出算法每次推进后的状态。读者可以把每一行轨迹与 BFS 的层级不变量、或 Kahn 算法的入度不变量对应起来，观察最短路和依赖排序为何成立。

## 数学连接

- [循环不变量](/discrete-math/loop-invariants)：每轮循环前后保持的结论；
- [BFS](/discrete-math/breadth-first-search)：无权图中最短步数；
- [图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)：依赖解除、拓扑序与有向环；
- [渐进复杂度](/discrete-math/asymptotic-complexity)：为何邻接表下为 $O(V+E)$。

## 运行

```bash
python projects/algorithm_lab/bfs_trace.py
python -m unittest projects.algorithm_lab.test_bfs_trace
```

输出中的 `distance` 表示当前节点与起点相差的边数，`queue` 表示本轮扩展后待处理的边界。

## 可观察的实验

1. 改变邻居顺序，观察路径可能变化但最短距离不变；
2. 给图加入一条边，检查轨迹在哪一层提前到达目标；
3. 将边加上不同权重，解释为什么此算法不再适用，并转向 [Dijkstra](/discrete-math/dijkstra)。

## 工程边界

本项目使用内存中的小型邻接表，旨在说明算法状态；真实大规模图需要考虑内存布局、输入格式和性能分析。
