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
from heapq import heappop, heappush


def dijkstra(graph, start):
    distances, parent = {start: 0}, {start: None}
    heap = [(0, start)]
    while heap:
        cost, node = heappop(heap)
        if cost != distances[node]:  # 跳过过期堆项
            continue
        for neighbor, weight in graph.get(node, []):
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative weights")
            candidate = cost + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor], parent[neighbor] = candidate, node
                heappush(heap, (candidate, neighbor))
    return distances, parent


distances, _ = dijkstra({"s": [("a", 2), ("b", 5)], "a": [("b", 1)]}, "s")
assert distances["b"] == 3
```

采用二叉堆时，每次松弛可能入堆，时间复杂度为 $O((V+E)\log V)$，空间为 $O(V+E)$。代码允许过期条目留在堆中，以简化“降低键”操作。

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
