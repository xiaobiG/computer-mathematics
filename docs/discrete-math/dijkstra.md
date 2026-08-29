---
title: Dijkstra：带权图最短路
description: 用贪心与松弛操作求非负边权图中的最短路径。
---

# Dijkstra：带权图最短路

## 从 BFS 到带权图

BFS 按边数分层，因此只适合每条边代价相同的图。若道路时间或网络延迟不同，需要维护当前已知的最小总成本，并始终优先扩展成本最小的节点。

## 松弛操作

若经由 $u$ 到达 $v$ 更短，则更新：

$$dist[v]\leftarrow\min(dist[v],dist[u]+w(u,v))$$

使用最小堆后，每次取出当前距离最小的未确定节点。边权非负保证以后绕路不可能再把它变得更短，这是贪心正确性的关键。

```python
from heapq import heappop, heappush

def dijkstra(graph, start):
    dist, heap = {start: 0}, [(0, start)]
    while heap:
        cost, node = heappop(heap)
        if cost != dist[node]:
            continue
        for neighbor, weight in graph[node]:
            candidate = cost + weight
            if candidate < dist.get(neighbor, float('inf')):
                dist[neighbor] = candidate
                heappush(heap, (candidate, neighbor))
    return dist
```

## 边界

存在负权边时，Dijkstra 的确定性结论不再成立；应改用 Bellman–Ford 等算法。时间复杂度常写为 $O((V+E)\log V)$。

## 练习

为算法保存前驱节点并还原路径；再构造一个负权边反例，说明为何它会失败。
