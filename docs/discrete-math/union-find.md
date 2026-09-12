---
title: 并查集与动态连通性：森林如何压缩成近常数查询
description: 用代表元不变量证明并查集的连通性判断，推导路径压缩与按大小合并的均摊复杂度及其边界。
courseLevel: "2–3（算法证明与工程）"
prerequisites: "树、图连通性、递归与渐进复杂度"
estimatedMinutes: 50
experiment: "比较朴素链式合并与路径压缩的 find 路径长度"
---

# 并查集与动态连通性：森林如何压缩成近常数查询

## 学习目标

读完后，你能说明并查集维护的数学对象和森林不变量；证明 `find`、`union` 对“只增边”的连通性查询正确；实现带输入检查的路径压缩与按大小合并；并知道删除边、最短路和在线动态连通性为何超出它的能力。

## 从重复 DFS 的瓶颈开始

边一条条加入社交图，每次都问“用户 $u,v$ 已连通吗？”重新 DFS 的成本是 $O(V+E)$。若查询很多而边只增加，真正需要维护的不是完整路径，而是顶点集合的一个**划分**：每个连通分量恰对应一个不相交集合。

并查集（disjoint-set union, DSU）把每个集合表示为一棵以根为代表元的树。它不记录路径长度或边的顺序，只记录“是否在同一块”。

## 不变量与定义

`parent[x]` 指向一个顶点；根满足 `parent[r] == r`。对任意顶点反复沿 `parent` 最终到达唯一根，记为 `find(x)`。核心不变量是：

> 两个顶点连通，当且仅当它们的根相同。

初始时每个顶点自成集合，命题成立。添加边 $(a,b)$ 时：若根相同，划分不变；若根不同，把一个根接到另一个根，正好合并两个原连通分量。因此归纳可知不变量在所有 `union` 后保持。

## 算法实现

```python
class UnionFind:
    def __init__(self, n: int):
        if n < 0:
            raise ValueError("n 必须非负")
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

    def _check(self, x: int) -> None:
        if not 0 <= x < len(self.parent):
            raise IndexError("顶点编号越界")

    def find(self, x: int) -> int:
        self._check(x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # 路径压缩：不改变根，因而不改变集合划分。
        while x != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x
        return root

    def union(self, a: int, b: int) -> bool:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        self.components -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)
```

`union(a,b)` 返回 `False` 当且仅当 $a,b$ 原本同集合。在无向图中，这正是“新边会形成环”的判据，也是 Kruskal 算法的关键。

## 为什么优化不破坏正确性

路径压缩只是让查询路径上的节点直接指向原来的根；这些节点的根不变，集合划分也不变。按大小合并总是让小树根指向大树根；同样只合并两棵树，不会把第三个集合误接进来。

只按大小合并时，一个节点深度每增加一层，所在树大小至少翻倍，深度至多 $O(\log n)$。结合路径压缩，任意 $m$ 次操作总成本为 $O(m\alpha(n))$；$\alpha$ 是增长极慢的反阿克曼函数，在实际规模下近似常数。这是**均摊**结论：单次操作不必保证常数时间。

## 可验证实验

测试不应只断言某个根编号，因为代表元可随合并顺序改变。应断言等价关系：

```python
uf = UnionFind(5)
assert uf.union(0, 1)
assert uf.union(1, 2)
assert uf.connected(0, 2)
assert not uf.union(0, 2)  # 同一分量内加边会成环
assert not uf.connected(0, 3)
assert uf.components == 3
```

可构造连续 `union(i, i+1)` 的输入，再重复查询最后一个节点。观察第一次 `find` 后父指针被压平；这验证的是优化效果，而正确性仍来自集合不变量。

## 失败案例与工程边界

- **删除边**：删除一条树边可能把一个集合拆开；普通 DSU 无法知道怎样拆分，需离线回滚 DSU 或专门的动态树算法。
- **有向可达性**：`connected` 是无向等价关系，不能回答“从 $u$ 能否到 $v$”。
- **最短路径**：同一分量不代表距离短，BFS/Dijkstra 仍需保留图结构。
- **递归实现栈深度**：未压缩的坏链在 Python 中可能触发递归深度限制；迭代 `find` 更稳健。

## 常见误区

1. “根编号本身有语义。”错误：它只是代表元，合并顺序会改变它。
2. “路径压缩让每次操作都是 $O(1)$。”错误：严格说是序列上的均摊 $O(\alpha(n))$。
3. “DSU 可以求连通路径。”错误：它保存分组，不保存前驱边。
4. “`union` 失败是异常。”错误：在 Kruskal 中它正是检测环的正常信号。

## 练习

1. **基础题**：依次合并 $(0,1),(2,3),(1,2)$，写出此时的连通分量，而不依赖具体根编号。
2. **推导题**：证明只按大小合并时，任一节点深度至多 $\lfloor\log_2 n\rfloor$。
3. **编码题**：实现 Kruskal 最小生成树，断言选中的边数为 $V-c$，其中 $c$ 是原图连通分量数。
4. **开放题**：设计一个支持“加边、删边、询问连通性”的服务接口；比较离线回滚、批处理重建和全动态算法的取舍。

## 练习答案提示

1. 合并后只有一个集合包含 $\{0,1,2,3\}$；根代表元可能随按秩规则不同而变，不能作为答案依据。
2. 节点深度每增加 1，它所在树的大小至少翻倍；因此深度为 $h$ 的节点所在树至少有 $2^h$ 个节点。
3. 边按非降权重扫描，仅在两端代表元不同才加入；每个原分量最终形成一棵树，所以边数是 $V-c$，同时应测试不连通图。
4. 先界定删边是否立即生效、查询是否在线；回滚适合离线时间段，批处理适合允许延迟，全动态结构换来更高实现复杂度。

## 延伸

将 `union` 的环判定接到[递推关系与分治复杂度](/discrete-math/recurrences)之后，练习分析 Kruskal。若问题需要分层路径而非集合归并，继续阅读[BFS](/discrete-math/breadth-first-search)；若需要带权最短路，则回到[Dijkstra](/discrete-math/dijkstra)。
