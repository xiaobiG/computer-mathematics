---
courseLevel: "2–3（算法与证明）"
prerequisites: "图、堆与循环不变量"
estimatedMinutes: 60
experiment: "实现最短路并构造负权反例"
title: Dijkstra：带权图最短路为何能贪心
description: 以松弛、不变式和负权反例证明非负边权图的最短路径算法。
---

# Dijkstra：带权图最短路为何能贪心

## 文章元信息

- **建议阅读层级**：2–3 · 推导、算法与工程边界
- **前置知识**：[BFS](/discrete-math/breadth-first-search)、[循环不变量](/discrete-math/loop-invariants)、最小堆
- **预计学习时间**：60 分钟
- **配套实验**：[算法可视化实验室](/projects/algorithm-lab)

## 学习目标

读完后，你能从松弛规则说明 `dist` 的语义；写出 Dijkstra 已确定集合的不变量与反证步骤；实现并审计非负权最短路及路径重建；并能识别负边、负环和堆中过期条目各自破坏什么前提。

## 从一个计算问题开始

BFS 以边数分层，适合每条边成本相同的图。导航系统的道路时间不同：如果先走一条边数较少但极慢的道路，BFS 会错误地优先它。Dijkstra 如何在不枚举所有路径的情况下保证已弹出的节点距离最终正确？

## 定义与直觉

设 $\delta(s,v)$ 为起点 $s$ 到顶点 $v$ 的真实最短距离。算法维护上界 `dist[v]`，初始 `dist[s]=0`、其余为无穷。**松弛**边 $(u,v)$ 的规则为

$$dist[v]\leftarrow\min(dist[v],dist[u]+w(u,v)).$$

最小堆每次取当前上界最小的未确定节点。直觉上，若所有边权非负，从它出发绕一个圈只会更长，因此不存在一条“稍后才发现”的更短绕路。

## 正确性推导

不变量是：已确定集合 $S$ 中每个顶点 $u$ 都满足 $dist[u]=\delta(s,u)$；对其余顶点，`dist` 是经过 $S$ 中节点的某条路径长度上界。

初始化时只有 $s$ 被确定，命题成立。假设本轮从堆取出最小的 $u$，若存在一条更短路径到 $u$，考察该路径从 $S$ 第一次离开的边 $(x,y)$。$x\in S$，松弛时已经给出 `dist[y]` 不大于这条路径前缀；又因边权非负，`dist[y]\le dist[u]`，与 $u$ 是最小未确定上界矛盾。因此 $u$ 的距离最终正确。每个节点至多确定一次，有限图上算法终止。

## 算法实现与复杂度

```python
from projects.algorithm_lab.dijkstra_trace import (
    dijkstra_trace, reconstruct_path, shortest_path_certificate,
)

graph = {"s": [("a", 2.0), ("b", 5.0)], "a": [("b", 1.0)], "b": []}
distances, parents, events = dijkstra_trace(graph, "s")
assert distances["b"] == 3.0
assert reconstruct_path(parents, "b") == ["s", "a", "b"]
assert [event.distance for event in events] == [0.0, 2.0, 3.0]
assert shortest_path_certificate(graph, "s", distances, parents, events)["valid"]
```

运行 `python -m unittest projects.algorithm_lab.test_dijkstra_trace`。实现会在开始前验证整张图的节点和权重，而非只在可达分支中偶然发现负边；它使用序号避免同距离、不可比较节点导致堆比较失败。事件按最终确定顺序记录节点、距离和成功松弛。`shortest_path_certificate` 再独立核对：每个有限距离都有同权重的父指针路径，所有边满足松弛不等式，轨迹恰好覆盖可达点且确定距离单调。前者给出“能达到这个距离”，后者沿任意路径逐边推出“不能更短”，二者合在一起才是最短路证书。

采用二叉堆时，每次松弛可能入堆，时间复杂度为 $O((V+E)\log V)$，空间为 $O(V+E)$。代码允许过期条目留在堆中，以简化“降低键”操作。证书检查扫描父指针和所有边，为 $O(V+E)$ 时间与 $O(V)$ 额外空间；它适合测试和审计，不是替代算法本身的第二次求解。

## 失败案例与工程边界

负权边会破坏证明。图 $s\to a$ 权重 $2$、$s\to b$ 权重 $5$、$b\to a$ 权重 $-10$ 中，算法可能先确定 $a=2$，却遗漏真实距离 $-5$。有负权边应使用 Bellman–Ford；有负环时最短路甚至未定义。超大图还要考虑权重溢出、稀疏存储和多源查询的预处理。

## 常见误区

- BFS 不是 Dijkstra 的“慢版本”；它隐含所有边权相同。
- 堆中弹出不等于首次发现节点，过期条目必须跳过。
- “非负”包含零权边，但不包含 NaN 或未定义权重。

## 练习

1. **基础**：手算示例图每次堆弹出与松弛后的 `dist`。
2. **推导**：补全上面的反证，明确首次离开 $S$ 的边为何存在。
3. **编码**：利用 `parent` 还原路径，并测试不可达节点。
4. **开放**：实现 Bellman–Ford，比较它与 Dijkstra 在负边、负环和非负图上的行为。

## 延伸与下一步

最短路是图算法中“贪心正确性依赖前提”的经典例子；继续阅读[递推关系与分治复杂度](/discrete-math/recurrences)，再用[算法实验室](/projects/algorithm-lab)观察 BFS 的队列轨迹。
