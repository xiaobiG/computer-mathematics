---
courseLevel: "0–2（图论预备与算法）"
prerequisites: "集合、递归、队列与渐进复杂度"
estimatedMinutes: 65
experiment: "实现 DFS 连通分量、二分图染色与 Kahn 拓扑排序，并构造环的反例"
title: 图、树、二分图与拓扑排序
description: 建立图算法的共同语言：表示、连通性、树、DFS、二分图与有向无环图的拓扑序。
---

# 图、树、二分图与拓扑排序

> 包管理的依赖、课程先修关系、社交网络和迷宫看似不同，抽象后都是顶点与边。真正困难的不是画图，而是先确认边是否有方向、路径要满足什么约束、输入结构能否支持所选算法。

## 学习目标

完成本课后，你能够：

- 区分无向图、有向图、路径、环、连通分量与强连通分量的基本含义；
- 根据稀疏/稠密程度选择邻接表或邻接矩阵；
- 证明无向连通图“树 \(\Leftrightarrow\) 边数为 \(|V|-1\) 且无环”；
- 用 DFS 计算连通分量、检测二分图，并分析 \(O(V+E)\) 复杂度；
- 用 Kahn 算法得到拓扑序或发现有向环，并理解其正确性。

## 从依赖安装失败开始

项目有依赖 `app → ui → core`，箭头表示“前者依赖后者”。若依赖图中出现

\[
 A\to B\to C\to A,
\]

就不存在一种“先装依赖、后装调用者”的线性顺序。这个失败不是构建工具的偶然问题，而是有向图含环的数学事实。

相反，若依赖图无环，就可以把所有顶点排成一个序列，让每条边 \(u\to v\) 都从较早的位置指向较晚的位置（或按项目约定反向排列）。这就是拓扑排序。理解它之前，先建立图的语言。

## 定义：图究竟记录了什么

图写作 \(G=(V,E)\)：

- \(V\) 是顶点集合；
- 无向图的边是无序对 \(\{u,v\}\)；有向图的边是有序对 \((u,v)\)，写作 \(u\to v\)；
- 路径是相邻顶点序列；不重复顶点的闭合路径形成环；
- 无向图中，能由路径相达的顶点构成一个连通分量。

有向图必须区分“从 \(u\) 能到 \(v\)”与“互相可达”。后者形成**强连通分量**；本课的拓扑排序只适用于没有任何有向环的 DAG（directed acyclic graph）。

### 邻接表还是邻接矩阵

邻接表为每个顶点保存邻居列表，存储为 \(O(V+E)\)，遍历全部边为 \(O(V+E)\)，适合绝大多数稀疏工程图。邻接矩阵 `matrix[u][v]` 使查边为 \(O(1)\)，但占 \(O(V^2)\) 空间，遍历一个顶点的邻居也要扫 \(O(V)\) 个格子，适合图很稠密或需要大量常数时间查边的场景。

不要把“边少”与“顶点度小”混淆：邻接表的总遍历成本是所有列表长度的和，恰为 \(2E\)（无向）或 \(E\)（有向）。

## 树：连通与无环的最小骨架

无向图中的树是连通且无环的图。对有 \(n\) 个顶点的无向图，下列条件中任取两项（配合必要的连通/无环条件）都能刻画树：

\[
\text{树}\quad\Longleftrightarrow\quad\text{连通且有 }n-1\text{ 条边}
\quad\Longleftrightarrow\quad\text{无环且有 }n-1\text{ 条边}.
\]

一个简洁证明从“每个连通图含有生成树”开始：从任意顶点扩张，每次连接一个尚未访问顶点，得到 \(n-1\) 条边的无环连通子图。原图若也是无环，就不能再多一条边，否则这条边两端在树中已有路径，会闭合成环；所以原图恰是这棵树。

这条性质给 Kruskal、并查集和网络连接问题提供了可验证的不变量：若一个连通组件有 \(k\) 个顶点且保持无环，它必须有恰好 \(k-1\) 条树边。

## DFS：沿一条分支走到底，再回溯

深度优先搜索维护三种状态：未访问、正在访问、已完成。每次遇到未访问的邻居就递归（或压栈）深入；一个顶点所有邻居处理完后回溯。

对无向图，从一个起点 DFS 标记的顶点恰好是它所在连通分量：

- DFS 只沿边前进，因此所有被标记点都与起点连通；
- 对任一与起点连通的顶点，取一条起点到它的路径。DFS 会依次检查路径上的边，故最终不会漏掉该顶点。

对每个未访问顶点再启动一次 DFS，就得到全部连通分量。每个顶点至多进入一次，每条邻接边至多检查一次，邻接表实现为 \(O(V+E)\) 时间、\(O(V)\) 额外状态空间（递归栈最坏也可达 \(O(V)\)）。

## 二分图：能否把冲突两侧分开

无向图是二分图，当且仅当顶点能染成两色，使每条边两端颜色不同。这等价于图中没有奇数长度环。

必要性很直接：沿环颜色交替，回到起点时奇数条边会要求起点同时拥有两种颜色。充分性可由 BFS/DFS 染色证明：从任一分量根设为 0，沿边翻转颜色；若出现一条边两端同色，沿两条根路径可构造奇环；若无冲突，颜色划分就是合法二分。

二分图出现在“人与任务”“学生与课程”这类只允许跨组关系的建模中，也是最大匹配算法的前置结构。

## 拓扑排序：反复取入度为零的顶点

对于有向图，顶点的入度是指向它的边数。Kahn 算法反复取出入度为零的顶点，把它放到答案，并删除它的出边；被删除边的终点入度降为零后加入队列。

```text
将所有入度为 0 的顶点入队
while 队列非空:
    u = 出队
    将 u 写入顺序
    for 每条 u -> v:
        indegree[v] -= 1
        若 indegree[v] == 0: v 入队
若顺序长度 < |V|: 图含环；否则顺序合法
```

为什么它正确？DAG 至少有一个入度为零的顶点：若每个顶点入度都正，从任意顶点不断沿入边倒走，有限图中必会重复顶点，从而得到环，矛盾。移除一个入度零顶点不会破坏其余 DAG 的无环性，因此可归纳地继续。顶点被输出时，所有前驱边已被删除，故每条边的起点都在终点之前。

若队列耗尽但仍有顶点，剩余子图每个顶点入度至少为一；同样沿入边倒走必发现环。这就是“未输出全部顶点”不仅是失败信号，也是有向环的证据。

## 可运行实现：分量、二分检测与拓扑序

```python
from collections import deque


def connected_components(graph):
    """无向邻接表；孤立顶点也须作为键出现。"""
    unseen = set(graph)
    components = []
    while unseen:
        start = unseen.pop()
        component, stack = {start}, [start]
        while stack:
            u = stack.pop()
            for v in graph[u]:
                if v not in component:
                    component.add(v)
                    unseen.discard(v)
                    stack.append(v)
        components.append(component)
    return components


def is_bipartite(graph):
    color = {}
    for start in graph:
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                expected = 1 - color[u]
                if v in color and color[v] != expected:
                    return False, color
                if v not in color:
                    color[v] = expected
                    queue.append(v)
    return True, color


def topological_sort(graph):
    """有向邻接表；环存在时返回 None。"""
    indegree = {u: 0 for u in graph}
    for neighbors in graph.values():
        for v in neighbors:
            if v not in indegree:
                raise ValueError("每个终点都必须出现在 graph 中")
            indegree[v] += 1
    queue = deque(u for u, degree in indegree.items() if degree == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return order if len(order) == len(graph) else None


dependencies = {"core": [], "ui": ["core"], "app": ["ui", "core"]}
print(topological_sort(dependencies))  # ['app', 'ui', 'core']，方向按“依赖者 -> 依赖”
print(topological_sort({"a": ["b"], "b": ["a"]}))  # None
```

注意最后的顺序方向：示例边是“依赖者 → 被依赖者”，因此先出现 `app`。若构建系统想先编译依赖，需要反转边，或反转得到的序列。算法没有替你决定业务语义。

## 工程边界与常见误区

- **递归 DFS 栈溢出。** 深链图在 Python 中会触及递归深度限制；生产实现常使用显式栈。
- **无向边只加一侧。** 无向边 \(u-v\) 应同时写入 `u` 的邻居和 `v` 的邻居，否则连通性结论失真。
- **漏掉孤立顶点。** 仅从边表生成键会丢失无边顶点，导致组件数和拓扑结果错误。
- **把“无环”说成“可随意排序”。** 拓扑序通常不唯一；队列/优先队列的选择决定输出次序。需要可复现构建时应指定稳定的平局规则。
- **对一般图套 DAG 最长路 DP。** 有向环会产生循环依赖；一般有向图最长简单路是困难问题，不能沿用拓扑转移。

## 练习

1. 证明：无向连通图若有 \(n-1\) 条边则无环。提示：若有环，删环上一条边仍连通。
2. 为 `is_bipartite` 构造一个长度 5 的环并验证失败；再构造长度 6 的环并解释两种着色。
3. 将 `connected_components` 改为返回每个分量的边数，并验证每个树分量满足 \(E=V-1\)。
4. 给出一个有向环，手工列出 Kahn 算法停止时每个剩余顶点的入度，并从中找出环。
5. 为包依赖系统选择边方向与稳定平局规则，写出三个应由测试保证的性质（包括环与孤立包）。

## 下一步

现在可以学习 [BFS：图中的最短步数](/discrete-math/breadth-first-search)、[Dijkstra：带权图最短路](/discrete-math/dijkstra) 和 [动态规划：状态与 DAG](/discrete-math/dynamic-programming-dag)。它们的正确性都建立在本课的图表示、分层/无环结构与不变量之上。
