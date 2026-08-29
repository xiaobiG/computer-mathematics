---
title: 并查集与动态连通性
description: 用不相交集合快速回答两个节点是否属于同一连通分量。
---

# 并查集与动态连通性

并查集维护若干不相交集合，支持 `find(x)` 查询代表元和 `union(a, b)` 合并两个集合。它非常适合“边不断加入时，两个节点是否已连通”的问题。

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return True
```

路径压缩与按大小合并使均摊复杂度接近常数，严格记为 $O(\alpha(n))$，其中反阿克曼函数增长极慢。

## 工程连接

Kruskal 最小生成树、社交网络社群合并和离线连通性查询都常使用并查集。它不擅长删除边后的动态连通性。

## 练习

用 `union` 的返回值实现 Kruskal 算法的环检测，并解释为何加入同一集合内的边会形成环。
