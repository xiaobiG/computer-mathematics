---
title: Bellman–Ford：负边最短路与负环检测
description: 用路径边数不变量推导 Bellman–Ford，证明其负边正确性，并实现可验证的负环检测与路径恢复。
courseLevel: "2–3（算法证明与工程边界）"
prerequisites: "图、最短路、松弛操作与循环不变量"
estimatedMinutes: 60
experiment: "实现带路径恢复的 Bellman–Ford，并构造 Dijkstra 失败与负环例子"
---

# Bellman–Ford：负边最短路与负环检测

## 学习目标

读完后，你能说明为何 Dijkstra 不能接受负边；从“至多 $k$ 条边的最短路径”状态推导 Bellman–Ford；证明 $|V|-1$ 轮松弛的正确性；并实现负环检测和不可达点处理。

## 从 Dijkstra 的失败开始

图有边 $s\to a=2,s\to b=5,b\to a=-10$。Dijkstra 可能先永久确定 $a$ 的距离为 2，后来才发现经过 $b$ 的距离为 -5。它的“已确定点不会再变好”不变量依赖非负边，负边直接毁掉该前提。

Bellman–Ford 不永久锁定顶点，而是反复尝试所有边的松弛；代价是 $O(VE)$，收益是处理负边并报告可达负环。

## 状态与松弛不变量

令 $d_k(v)$ 是从源点到 $v$、使用至多 $k$ 条边的最短路径长度；没有路径则为 $\infty$。初始 $d_0(s)=0$，其余为 $\infty$。对边 $(u,v,w)$：

$$d_k(v)=\min\bigl(d_{k-1}(v),\;d_{k-1}(u)+w\bigr).$$

这正是松弛：若经过 $u$ 再走一条边更短，则更新 $v$。任何简单路径最多有 $|V|-1$ 条边；若从源点可达的最短路径存在且没有可达负环，最优路径可取简单路径。因此 $|V|-1$ 轮后得到真实最短距离。

## 可运行实现

```python
from math import inf

def bellman_ford(vertex_count, edges, source):
    if not 0 <= source < vertex_count:
        raise ValueError("source 越界")
    if any(not (0 <= u < vertex_count and 0 <= v < vertex_count) for u, v, _ in edges):
        raise ValueError("边端点越界")
    distance, parent = [inf] * vertex_count, [None] * vertex_count
    distance[source] = 0
    for _ in range(vertex_count - 1):
        changed = False
        for u, v, weight in edges:
            if distance[u] != inf and distance[u] + weight < distance[v]:
                distance[v], parent[v], changed = distance[u] + weight, u, True
        if not changed:
            break
    negative_cycle = any(distance[u] != inf and distance[u] + w < distance[v]
                         for u, v, w in edges)
    if negative_cycle:
        raise ValueError("源点可达负环，最短距离无定义")
    return distance, parent
```

提前停止不改变正确性：若一整轮没有更新，所有可用“再加一条边”的路径也不能改善，之后不会再改变。`parent` 仅在更新时写入，回溯可恢复一条最短路；路径恢复必须限制长度以防输入或代码错误产生环。

## 正确性与复杂度

对轮数归纳：第 $k$ 轮后，`distance[v]` 等于至多 $k$ 条边路径的最短长度。基例对应只有空路径；归纳步枚举“不加第 $k$ 条边”与“从某个 $u$ 加一条边”两类路径。无负环时，简单最优路径边数不超过 $V-1$，结论成立。

再做第 $V$ 轮若仍能松弛，改善路径含至少 $V$ 条边，必重复某顶点；去掉非负环不会改善，故能改善只能意味着包含负环。复杂度最坏 $O(VE)$，空间 $O(V)$；稠密图或多源最短路时，应评估 Floyd–Warshall、Johnson 或问题结构。

## 失败案例与工程边界

- **不可达负环**：不从源点可达的负环不影响该源的距离；实现不应把它误报为错误。
- **负环可达但不通向查询目标**：若只关心单目标，可进一步分析影响范围；本实现保守地报告源可达负环。
- **整数溢出**：固定宽度语言的 `distance + weight` 可溢出并伪造松弛；须检查或用足够大的数值类型。
- **浮点权重**：比较需容差且误差会累积；图最短路通常优先用精确整数成本。

## 常见误区

1. “Bellman–Ford 只是在 Dijkstra 上多循环几次。”错误：它的正确性不依赖贪心确定点，而依赖路径边数归纳。
2. “任何负环都会报错。”错误：只检测从源可达的负环。
3. “没有负边就应总用 Bellman–Ford。”错误：Dijkstra 通常更快，前提满足时应使用它。
4. “负环只是距离很小。”错误：可任意绕行使路径长度趋于负无穷，最短值不存在。

## 练习

1. **基础题**：对 $s\to a=2,s\to b=5,b\to a=-10$ 手算两轮松弛。
2. **推导题**：完成“可改善的至少 $V$ 边路径蕴含可达负环”的证明。
3. **编码题**：为实现添加 `reconstruct_path`，并测试不可达点、负边正确路径和可达负环。
4. **开放题**：比较 Dijkstra、Bellman–Ford、Floyd–Warshall 在稀疏/稠密、多源/单源、含负边三种维度的选择条件。

## 延伸

将本课与[Dijkstra](/discrete-math/dijkstra)并读，重点比较各自不变量。进一步学习 Johnson 重加权与差分约束系统；它们展示负边并不必然阻止更快算法，但必须先恢复可用的正确性前提。
