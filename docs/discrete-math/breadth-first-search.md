---
title: BFS：无权图最短路为什么按层出现
description: 用队列分层不变量证明 BFS 的最短步数，并实现路径还原与边界测试。
---

# BFS：无权图最短路为什么按层出现

## 文章元信息

- **建议阅读层级**：2 · 算法、正确性与复杂度
- **前置知识**：[循环不变量](/discrete-math/loop-invariants)、队列与图的邻接表
- **预计学习时间**：55 分钟
- **配套实验**：[算法可视化实验室](/projects/algorithm-lab)

## 学习目标

- 用队列实现无权图的最短步数与路径还原；
- 证明首次发现节点就是最短路径；
- 判断何时必须从 BFS 切换到 Dijkstra 或其他算法。

## 从一个计算问题开始

社交图中“最少经过几条关系能到达目标？”和迷宫中“最少走几步到出口？”都只关心边数。深度优先搜索也能找到路径，却可能先沿很长的分支走到底；BFS 为什么能保证第一次找到的目标路径最短？

## 直觉与定义

令 $d(s,v)$ 为从起点 $s$ 到 $v$ 的最少边数。BFS 的队列像波纹：先放入距离 0 的起点，再放入所有未访问邻居（距离 1），随后才会处理距离 2。`visited` 在**入队时**标记，确保每个节点只首次入队一次。

## 正确性推导

不变量：队列中节点的距离非递减；任一已入队节点都带有一条长度等于其记录距离的路径；当节点 $u$ 出队时，记录距离等于 $d(s,u)$。

初始化时队列只有 $(s,0)$，成立。假设出队 $u$ 时成立。每个未访问邻居 $v$ 被赋值 `distance[u]+1` 并入队，显然存在对应路径。若存在更短路径到 $v$，其倒数第二个节点距离至多 `distance[u]-?`；该层应先于 $u$ 或与 $u$ 同层被处理，并会更早发现 $v$，与 `v` 尚未访问矛盾。因此首次入队距离最短。目标首次出队时即可返回。

## 算法实现与复杂度

```python
from collections import deque


def shortest_path(graph, start, target):
    queue, parent = deque([start]), {start: None}
    while queue:
        node = queue.popleft()
        if node == target:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path))
        for neighbor in graph.get(node, []):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    return None


assert shortest_path({"s": ["a", "b"], "a": ["t"], "b": [], "t": []}, "s", "t") == ["s", "a", "t"]
```

每个顶点至多入队一次、每条边至多检查一次，邻接表下时间为 $O(V+E)$，`parent` 与队列的空间为 $O(V)$。

## 失败案例与工程边界

BFS 最小化的是**边数**，不是时间、距离或金额。若边 $s\to t$ 权重 100、$s\to a\to t$ 权重各 1，BFS 会选一条边的昂贵路径；非负权图应使用 [Dijkstra](/discrete-math/dijkstra)。超大图还需考虑双向 BFS、外存队列和节点 ID 去重。

## 常见误区

- 在出队时才标记访问会让同一节点反复入队，破坏空间界与父节点语义。
- BFS 不是任何图上的“最短距离”算法；它依赖单位边权。
- 找到目标的首次发现与首次出队在标准入队标记实现中等价；本文选择出队返回以保持不变量表述清晰。

## 练习

1. **基础**：给示例图加一条边，手写每轮队列与 `parent`。
2. **推导**：补全上面“更短路径会更早发现”的反证。
3. **编码**：返回所有距离而非单一目标路径，并测试不可达节点与环。
4. **开放**：实现双向 BFS，说明它为何常减少搜索节点却仍需正确终止条件。

## 延伸与下一步

BFS 的队列分层是图算法不变量的基础；[Dijkstra](/discrete-math/dijkstra)在非负权下用最小堆维持更一般的距离顺序。
