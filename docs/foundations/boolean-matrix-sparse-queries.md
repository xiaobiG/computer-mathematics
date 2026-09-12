---
title: 布尔矩阵乘法与稀疏图查询：两步可达为何不是普通乘法
description: 从关系复合推导布尔矩阵乘法，在同一输入上比较密集候选检查与稀疏邻接表扫描。
courseLevel: "1（关系、矩阵与图算法桥接）"
prerequisites: "有限关系与邻接矩阵、关系复合与可达闭包"
estimatedMinutes: 60
experiment: "boolean-relation-composition/v1：重放布尔乘积、稀疏两跳扫描与操作计数"
---

# 布尔矩阵乘法与稀疏图查询：两步可达为何不是普通乘法

## 学习目标

你将能从关系复合推导布尔矩阵乘法；区分普通数值乘法和“存在一条中间路径”的逻辑；在同一关系上比较矩阵候选检查与邻接表扫描；并知道稀疏性和查询模式而非口号决定表示选择。

## 从两跳查询开始

若关系 $R$ 有 $(a,b),(b,c)$，查询“a 能否两步到 c”不是把边权相乘，而是问是否**存在**中间点 $b$。邻接矩阵适合直接检查任意格；邻接表适合沿实际边扩展。两者表示同一关系，却让程序做不同的工作。

## 定义与推导

令 $A,B$ 是关系 $R,S$ 的 0/1 矩阵。复合关系满足

$$
(R\circ S)(x,z)\Longleftrightarrow\exists y:\ (x,y)\in R\land(y,z)\in S.
$$

因此对应的布尔乘积使用 OR 代替加法、AND 代替乘法：

$$
(A\odot B)_{ij}=\bigvee_{k=1}^{n}(A_{ik}\land B_{kj}).
$$

值 1 表示至少一个中间点存在，不表示路径数或距离。把它换成普通 $\sum_kA_{ik}B_{kj}$ 会得到路径条数；换成 min-plus 才与带权最短路有关。代数不同，问题含义也不同。

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

运行 `python -m unittest projects.foundations_lab.test_relations`。报告绑定左右关系、布尔乘积、两条计算路径和实际扫描计数；篡改复合对或计数都会被证书拒绝。

## 正确性与复杂度

对每个输出对 $(x,z)$，密集循环只在找到某个同时满足两条关系的 $y$ 时写 1，恰好实现存在量词；邻接表循环枚举每个实际 $(x,y)$ 后的实际 $(y,z)$，生成同一批复合对。证书比较两集合，而不是假设两个实现“应该一样”。

密集候选检查最坏为 $O(n^3)$，矩阵存储为 $O(n^2)$。稀疏两跳扫描为 $\sum_{(x,y)\in R}\mathrm{outdeg}_S(y)$；它常在稀疏图上更小，却可能在高度节点或稠密图上接近立方工作量。若要大量任意对查询，预计算矩阵或闭包可能值得；若仅从少量源点查询，BFS/DFS 往往更合适。

## 失败案例与工程边界

- **普通乘法当可达性。** 它计算路径数，不是布尔存在性。
- **稀疏永远更快。** 星形、热点中间点或稠密图可让邻接表扫描很大。
- **矩阵顺序被忽略。** 行列对应的域顺序改变会改变关系语义。
- **两步可达当传递闭包。** 闭包需要重复组合或逐中间点不变量。
- **把操作计数当吞吐量。** 缓存、位运算、图存储和查询批次会改变真实性能。

## 常见误区

- “矩阵里的 1 就是数值权重。”此处只表示真假。
- “邻接表与矩阵给不同答案。”正确实现应给同一关系，只是代价不同。
- “预计算总是更好。”更新频率和查询数量会改变取舍。

## 练习

1. 手算链 $a\to b\to c$ 的布尔平方，说明为什么 $(a,c)$ 为 1。
2. 推导稀疏扫描为何只枚举已存在的两段边。
3. **编码**：篡改报告的 `sparse_two_hop_scans` 或复合对，确认证书拒绝。
4. **开放**：为社交图的“共同关注”查询比较矩阵、邻接表与预计算闭包，写明密度、查询量和更新率假设。

## 练习答案提示

1. 选择中间点 b；存在性成立即可写 1，不需计算路径数。
2. 外层枚举 $(x,y)\in R$，内层只枚举 y 的真实后继；不存在的边不参与。
3. 证书应从输入关系重建两种结果与计数，不能只检查字段存在。
4. 指出哪些假设使一次性 $O(n^2)$ 存储可接受，哪些使按查询 BFS 更合理。

## 下一步

[关系复合与可达闭包](/foundations/relation-composition-reachability)将两步关系推广到任意长度；[图的两种存储](/discrete-math/graph-representations)继续比较表示成本；[Floyd–Warshall](/discrete-math/floyd-warshall)展示另一种代数下的全源动态规划。
