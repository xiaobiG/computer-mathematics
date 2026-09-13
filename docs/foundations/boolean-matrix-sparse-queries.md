---
title: 布尔矩阵乘法与稀疏图查询：两步可达为何不是普通乘法
description: 从关系复合推导布尔矩阵乘法，在同一输入上比较密集候选检查与稀疏邻接表扫描。
courseLevel: "1（关系、矩阵与图算法桥接）"
prerequisites: "有限关系与邻接矩阵、关系复合与可达闭包"
estimatedMinutes: 60
experiment: "布尔复合、稀疏扫描与位集合批次查询的可重放计数"
---

# 布尔矩阵乘法与稀疏图查询：两步可达为何不是普通乘法

## 学习目标

你将推导布尔乘积，并比较密集、稀疏和位集合查询。

## 从两跳查询开始

两跳查询问中间点是否存在，不是边权相乘；矩阵与邻接表语义相同、工作不同。

## 定义与推导

令 $A,B$ 是关系 $R,S$ 的 0/1 矩阵。复合关系满足

$$
(R\circ S)(x,z)\Longleftrightarrow\exists y:\ (x,y)\in R\land(y,z)\in S.
$$

因此对应的布尔乘积使用 OR 代替加法、AND 代替乘法：

$$
(A\odot B)_{ij}=\bigvee_{k=1}^{n}(A_{ik}\land B_{kj}).
$$

值 1 表示中间点存在，不表示路径数或距离。

## 算法与可运行实验

密集实现对每个 $(i,j)$ 逐一试探中间点 $k$；稀疏邻接表则只从实际存在的 $(i,k)$ 出发，扫描 $k$ 的实际后继：

```python
from projects.foundations_lab.relations import (
    boolean_relation_composition_certificate,
    boolean_relation_composition_report,
)

report = boolean_relation_composition_report(
    ["a", "b", "c"], [["a", "b"], ["b", "c"]], [["b", "a"], ["c", "a"]],
)
assert report["composition_pairs"] == [["a", "a"], ["b", "a"]]
assert report["verification"]["dense_and_sparse_pairs_match"]
assert boolean_relation_composition_certificate(
    ["a", "b", "c"], [["a", "b"], ["b", "c"]], [["b", "a"], ["c", "a"]], report,
)
```

报告绑定关系、布尔乘积、两条路径和扫描计数；篡改结果或计数会被证书拒绝。

## 正确性与复杂度

对每个输出对 $(x,z)$，密集循环只在找到某个同时满足两条关系的 $y$ 时写 1，恰好实现存在量词；邻接表循环枚举每个实际 $(x,y)$ 后的实际 $(y,z)$，生成同一批复合对。证书比较两集合，而不是假设两个实现“应该一样”。

密集检查最坏 $O(n^3)$、存储 $O(n^2)$；稀疏扫描为 $\sum_{(x,y)\in R}\mathrm{outdeg}_S(y)$，热点或稠密图仍可很大。大量任意对查询可预计算，少量源点通常用 BFS/DFS。

## 查询批次：位集合并集与重复源缓存

位集合把右关系行按位 OR。`a,a,b` 中第二个 `a` 命中缓存，但总成本 10 高于 7 次稀疏扫描：

```python
from projects.foundations_lab.relations import (
    bitset_batch_relation_query_certificate,
    bitset_batch_relation_query_report,
)

report = bitset_batch_relation_query_report(
    ["a", "b", "c", "d"], [["a", "b"], ["a", "c"], ["b", "d"]],
    [["b", "a"], ["b", "d"], ["c", "d"], ["d", "c"]], ["a", "a", "b"], word_bits=2,
)
assert report["batch_outputs"][1]["cache_hit"]
assert report["work"]["sparse_two_hop_scans"] == 7
assert bitset_batch_relation_query_certificate(
    ["a", "b", "c", "d"], [["a", "b"], ["a", "c"], ["b", "d"]],
    [["b", "a"], ["b", "d"], ["c", "d"], ["d", "c"]], ["a", "a", "b"], 2, report,
)
```

## 更新后：缓存必须绑定关系版本

`relation_cache_invalidation_report` 在同一批源上比较版本 0/1 的右关系。给 `b` 增加一条右边后，`a,a,c` 的两跳答案均改变，旧缓存不能当作版本 1 的结果；报告列出受影响查询并由证书重放。

这是有限快照合同，不是并发缓存一致性或实际运行时性能保证。

这是固定字宽模型；真实速度还取决于布局、运行时和更新。

## 失败案例与工程边界

- **普通乘法当可达性。** 它计路径数，不是存在性。
- **稀疏或位集合永远更快。** 构造、缓存和更新会改变计数。
- **忽略矩阵顺序或闭包层次。** 域顺序决定语义；两步不等于闭包。
- **操作计数当吞吐量。** CPU、布局和运行时仍会改变速度。

## 常见误区

- “矩阵里的 1 是权重。”此处只表示真假。
- “表示会给不同答案。”正确实现只应改变代价。
- “预计算总更好。”更新和查询批次决定取舍。

## 练习

1. 手算 $a\to b\to c$ 的布尔平方。
2. 为什么稀疏扫描只枚举已存在的两段边？
3. **编码**：篡改扫描/缓存计数或复合对，确认证书拒绝。
4. **开放**：为共同关注查询比较三种表示，写明批次和更新率。

## 练习答案提示

1. 选中间点 b；存在即可写 1。
2. 外层枚举已有 $(x,y)$，内层枚举 y 的真实后继。
3. 从输入重建结果、扫描和缓存，不能只查字段。
4. 对比存储、重复批次与更新成本。

## 下一步

[关系复合与可达闭包](/foundations/relation-composition-reachability)将两步关系推广到任意长度；[图的两种存储](/discrete-math/graph-representations)继续比较表示成本；[Floyd–Warshall](/discrete-math/floyd-warshall)展示另一种代数下的全源动态规划。
