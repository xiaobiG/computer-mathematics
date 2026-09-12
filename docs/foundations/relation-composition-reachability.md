---
title: 关系复合与可达闭包：两步路径如何成为矩阵中的 1
description: 用关系复合与逐中间点闭包，将有序对、布尔矩阵和图的可达性连成可重放不变量。
courseLevel: "1（关系、矩阵与图遍历前置）"
prerequisites: "有限关系与邻接矩阵、集合与数组形状"
estimatedMinutes: 60
experiment: "relation-reachability/v1：记录逐中间点的传递闭包新增对"
---

# 关系复合与可达闭包：两步路径如何成为矩阵中的 1

## 学习目标

你将能写出关系复合的定义；解释长度两步路径为何产生新关系对；用逐中间点不变量计算传递闭包；并将其对应到图可达性和布尔邻接矩阵。

## 从一个计算问题开始

给定边 $(a,b)$ 与 $(b,c)$，图搜索说“a 能经 b 到 c”；关系语言说 $(a,c)$ 属于 $R\circ R$。若只存直接边，`a -> c` 的矩阵格为 0；若问题问可达性，它应在闭包中成为 1。如何加入这条边，又如何证明没有越过尚未允许的中间点？

## 定义与不变量

$$R\circ R=\{(x,z):\exists y,(x,y)\in R\land(y,z)\in R\}.$$ 

固定域顺序 $d_1,\ldots,d_n$。第 $k$ 轮后维护：当前集合恰好包含所有内部中间点属于 $\{d_1,\ldots,d_k\}$ 的路径端点对。第 $k+1$ 轮仅用 $d_{k+1}$ 拼接已有对；这就是 Floyd–Warshall 可达性版本的核心不变量。

## 可运行实验

```python
from projects.foundations_lab.relations import relation_reachability_certificate, relation_reachability_report

domain = ["a", "b", "c"]
pairs = [["a", "b"], ["b", "c"]]
report = relation_reachability_report(domain, pairs)
assert ["a", "c"] in report["closure_pairs"]
assert relation_reachability_certificate(domain, pairs, report)
```

运行 `python -m unittest projects.foundations_lab.test_relations`。报告保留每个允许中间点和当轮新增对；证书重放全部层次，篡改闭包格或某层新增对都会失败。

## 正确性与复杂度

归纳基是没有中间点时仅有原始关系。归纳步将每条允许经过新点的路径拆成两段已被前一层允许的路径，故加入且只加入需要的新对。每层枚举端点对，直接实现为 $O(n^3)$ 时间、$O(n^2)$ 存储。

## 失败案例与工程边界

- 关系对有方向；不能把 $(a,b)$ 自动当作 $(b,a)$。
- 闭包不自动加入自环；只有存在非空回路时相应自环才可达。
- 小矩阵适于推导；稀疏大图通常用 BFS/DFS，而非存储全部闭包。
- 加权最短路需要 `min-plus` 等不同代数，不能把 0/1 闭包直接当距离。

## 常见误区

- “两步路径就是一条原边”：闭包关系回答可达，不改写原始图。
- “传递性等于对称性”：一个约束路径拼接，一个约束反向边。
- “矩阵乘法的普通加法适用”：此处是存在性逻辑的布尔组合。
- “所有可达性都要预计算”：查询数量、稠密度和更新频率决定选择。

## 练习

1. 对链 $a\to b\to c\to d$ 写出闭包新增的所有对。
2. 为什么第 k 层不能使用尚未允许的中间点？
3. 给出一个传递但不对称的关系。
4. 比较全闭包与从单一源点 BFS 的空间成本。

## 练习答案提示

1. 包括 $(a,c),(b,d),(a,d)$，按中间点顺序出现。
2. 否则报告无法维持“只允许前 k 个点”的归纳含义。
3. 小于等于关系是典型例子。
4. 闭包需 $O(n^2)$ 结果，单源 BFS 通常只需 $O(n)$ 状态加图表示。

## 延伸

[有限关系与邻接矩阵](/foundations/finite-relations-matrices)给出直接关系编码；[Floyd–Warshall](/discrete-math/floyd-warshall)将同一层次不变量推广到带权最短路；[图的两种存储](/discrete-math/graph-representations)比较矩阵和邻接表的代价。
