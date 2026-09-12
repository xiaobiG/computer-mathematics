---
title: 有限关系与邻接矩阵：从集合对到图表示
description: 将有限二元关系写成笛卡尔积的子集和 0/1 邻接矩阵，审计自反、对称与传递性。
courseLevel: "0–1（集合、关系与数组表示）"
prerequisites: "集合与数组形状、零基索引、有限求和"
estimatedMinutes: 60
experiment: "finite-relation-matrix/v1：重放关系对、邻接矩阵与性质报告"
---

# 有限关系与邻接矩阵：从集合对到图表示

## 学习目标

你将能把有限关系表示为有序对集合与 0/1 矩阵；区分成员与坐标；检查自反、对称、传递性；并理解同一矩阵为何既可表示关系，也可表示有向图的边。

## 从一个计算问题开始

集合 $D=\{a,b,c\}$ 上，“可达”或“同组”不是单个元素，而是有序对。例如 $(a,b)$ 表示 $aRb$。若程序需要快速查看某对是否存在，可以在固定顺序 $[a,b,c]$ 下把它存为矩阵 $M$：第 $i$ 行、第 $j$ 列为 1 当且仅当第 $i$ 个成员与第 $j$ 个成员有关系。

## 定义与矩阵表示

二元关系是 $R\subseteq D\times D$。在有限域的固定顺序下，

$$M_{ij}=\begin{cases}1,&(d_i,d_j)\in R\\0,&\text{otherwise.}\end{cases}$$

自反要求所有 $(d,d)$ 在 $R$；对称要求 $(x,y)\in R\Rightarrow(y,x)\in R$；传递要求 $(x,y),(y,z)\in R\Rightarrow(x,z)\in R$。矩阵的对角线对应自反性；对称关系的矩阵关于主对角线对称。

## 可运行实验

```python
from projects.foundations_lab.relations import finite_relation_certificate, finite_relation_report

domain = ["a", "b"]
pairs = [["a", "a"], ["b", "b"], ["a", "b"], ["b", "a"]]
report = finite_relation_report(domain, pairs)
assert report["adjacency_matrix"] == [[1, 1], [1, 1]]
assert report["properties"]["equivalence_relation"]
assert finite_relation_certificate(domain, pairs, report)
```

运行 `python -m unittest projects.foundations_lab.test_relations`。合同拒绝重复成员、重复关系对和域外元素；证书重建矩阵与性质，篡改矩阵单元或传递性结论都会失败。

## 正确性与复杂度

矩阵构造逐一检查 $|D|^2$ 个可能有序对，因此时间和空间均为 $O(|D|^2)$。自反性检查对角线；对称性反转每条已给关系对；传递性枚举两跳组合，直接教学实现最多为 $O(|D|^3)$。这正解释了为什么稀疏图通常更偏好邻接表。

## 失败案例与工程边界

- **交换坐标。** $(a,b)$ 与 $(b,a)$ 在一般关系中不同；有向边也是如此。
- **忽略矩阵顺序。** 同一 0/1 数组若成员顺序变了，关系语义也变了。
- **把缺少传递边当错误。** 这只说明该关系不是传递的；不是所有关系都应是等价关系。
- **大而稀疏的域。** 本课程矩阵适合小规模可视化，不替代生产图存储。

## 常见误区

- **“关系一定对称。”** 小于关系和有向可达关系通常不对称。
- **“对角线全 1 就是等价关系。”** 还需要对称和传递。
- **“矩阵里的 1 是数值权重。”** 本课的 1 只表示关系存在；加权图需另行定义。
- **“集合没有顺序，所以矩阵也不需顺序。”** 关系本身无需顺序，矩阵编码必须声明顺序。

## 练习

1. 为 $D=\{1,2,3\}$ 的“小于等于”关系写出矩阵，并判断三种性质。
2. 给出一个自反且对称、但不传递的关系。
3. 为什么同一关系对列表可用邻接表或邻接矩阵编码？
4. 将一个无向图转换为对称关系，说明循环边如何影响对角线。

## 练习答案提示

1. 它自反、传递，通常不对称；按元素顺序填上三角形。
2. 例如含所有自环、$(a,b),(b,a),(b,c),(c,b)$，但不含 $(a,c)$。
3. 两者都保留同一对集合，只是查询和枚举的时间/空间成本不同。
4. 每条无向边写成两个方向；自环恰好对应一个对角元素。

## 延伸

[集合与数组形状](/foundations/sets-array-shapes)复习成员与坐标；[图的两种存储](/discrete-math/graph-representations)比较邻接表与邻接矩阵；[集合、关系、等价类与偏序](/discrete-math/sets-relations-orders)继续研究关系的数学结构。
