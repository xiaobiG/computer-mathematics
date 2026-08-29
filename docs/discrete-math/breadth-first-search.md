---
title: BFS：图中的最短步数
description: 为什么按层访问图能找到无权图最短路径。
---

# BFS：图中的最短步数

## 核心想法

广度优先搜索（BFS）从起点开始，先访问距离为 1 的所有节点，再访问距离为 2 的节点。队列保证节点按“距离层”进入和离开，因此一个节点第一次被访问时，已经通过最少边数到达它。

```python
from collections import deque

def shortest_steps(graph, start, target):
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, distance = queue.popleft()
        if node == target:
            return distance
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    return None
```

## 正确性的关键不变量

队列中的节点距离非递减；当距离为 $d$ 的节点被取出时，所有距离小于 $d$ 的可达节点均已处理。因此，第一次到达节点的路径不可能比已知路径更短。

## 复杂度与边界

邻接表表示下，BFS 的时间复杂度为 $O(V+E)$，空间复杂度为 $O(V)$。它只适用于每条边代价相同的情形；带权图应使用 Dijkstra 等算法。

## 练习

为代码记录 `parent`，在找到目标后回溯并输出一条实际最短路径。
