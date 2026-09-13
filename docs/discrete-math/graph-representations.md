---
title: 图的两种存储：邻接表、邻接矩阵与表示成本
description: 将同一张有限图同时重放为邻接表与邻接矩阵，比较查边、枚举邻居、方向和存储成本。
courseLevel: "1–2（离散结构与图算法前置）"
prerequisites: "集合与数组形状、图的基本定义与渐进复杂度"
estimatedMinutes: 60
experiment: "重放无权有限图的邻接表、邻接矩阵、查询和存储报告"
---

# 图的两种存储：邻接表、邻接矩阵与表示成本

## 学习目标

你将能从同一份边表构造邻接表和邻接矩阵；在有向/无向语义下判断它们是否表示同一张图；推导查边与枚举邻居的不同成本；并用可重放报告审计表示、密度和查询结论。

## 同一张图，不同的程序对象

令无向图有 4 个顶点和边

$$E=\{\{0,1\},\{0,3\},\{1,2\},\{2,3\}\}.$$

邻接表只保存真实存在的连接：`[[1,3], [0,2], [1,3], [0,2]]`。邻接矩阵则保存所有可能的顶点对：

$$A=\begin{bmatrix}0&1&0&1\\1&0&1&0\\0&1&0&1\\1&0&1&0\end{bmatrix},\qquad A_{uv}=1\Longleftrightarrow\{u,v\}\in E.$$

两者都能回答“0 和 3 相邻吗”，但它们不是可随意互换的内存布局：列表查看顶点 0 的邻居只扫描 `[1,3]`，矩阵则需为枚举邻居检查这一行的 4 个格。反过来，矩阵查单个 `A[0][3]` 是一次访问；未排序列表的查边需要在该顶点的邻居中寻找目标。

## 表示约定：顶点、方向与槽位

本页将顶点固定为 `0` 到 `V-1` 的整数，边写作 `[u,v]`。有向图保留顺序，`[0,1]` 不推出 `[1,0]`；无向图会将一条边写入双方邻居列表，并让矩阵对称。自环和重复边在教学合同中被拒绝：它们不是绝对不能出现的图模型，而是需要额外说明多重边或环如何影响计数的另一种合同。

对有向图，邻接表的邻居槽位总数为 $E$；无向图为 $2E$。再加 $V$ 个顶点槽位，得到 $O(V+E)$ 级别的表示。邻接矩阵始终有 $V^2$ 个格，即使绝大多数都是 0。定义有向密度为

$$\rho=\frac{E}{V(V-1)}$$

（无向图分母为 $V(V-1)/2$）。密度只是结构信号：真正选择还要看是频繁查单条边、还是频繁遍历邻居，以及是否需要稀疏权重、动态更新或位压缩。

## 可运行实验：双表示报告

```python
from projects.algorithm_lab.graph_representations import (
    graph_representations_certificate,
    graph_representations_report,
)

edges = [[0, 1], [0, 3], [1, 2], [2, 3]]
report = graph_representations_report(4, edges, False, [[0, 3], [1, 3]])

assert report["adjacency_list"][0] == [1, 3]
assert report["adjacency_matrix"][0] == [0, 1, 0, 1]
assert report["storage"]["adjacency_list_neighbor_slots"] == 8
assert report["storage"]["adjacency_matrix_cells"] == 16
assert report["edge_queries"][0]["answers_agree"]
assert graph_representations_certificate(4, edges, False, [[0, 3], [1, 3]], report)
```

运行：

```bash
python -m unittest projects.algorithm_lab.test_graph_representations
```

报告分别记录每个顶点的列表检查次数和矩阵行扫描次数；对每个指定查边问题，同时计算两个表示的布尔答案。证书从原始边表重新构造两种表示，因此把矩阵格数改成 7、篡改查询答案或调换有向边方向都会失败。

## 运行实验：同一 BFS 的实际扫描数

静态的槽位计数并不自动等于一次算法实际花费：BFS 只会扫描从起点可达的顶点。下面用一条 5 顶点路径加一个不可达顶点，分别重放两个表示：

```python
from projects.algorithm_lab.graph_representations import (
    graph_representation_bfs_certificate,
    graph_representation_bfs_report,
)

edges = [[0, 1], [1, 2], [2, 3]]
report = graph_representation_bfs_report(5, edges, False, source=0)

assert report["adjacency_list_bfs"]["distances"] == [0, 1, 2, 3, None]
assert report["adjacency_matrix_bfs"]["distances"] == [0, 1, 2, 3, None]
assert report["adjacency_list_bfs"]["neighbor_slot_checks"] == 6
assert report["adjacency_matrix_bfs"]["matrix_cell_checks"] == 20
assert report["distances_agree"]
assert graph_representation_bfs_certificate(5, edges, False, 0, report)
```

两个实现得到同一组无权最短距离，因为它们逐顶点判断的边关系相同；但列表只扫描已访问顶点的真实邻居槽位，矩阵为每个已访问顶点扫描完整一行。此例访问 4 个顶点：无向列表扫描 $2E_{\mathrm{reachable}}=6$ 个槽位，矩阵扫描 $4\times5=20$ 个格。不可达的顶点 4 不被出队，所以它的邻居（若有）不应被算入这次 BFS 的工作量。

这份证书绑定距离、出队顺序、扫描计数和表示本身。它仍然是小规模、固定邻居排序的教学审计，不是不同语言或硬件之间的墙钟基准。

## 加权图反例：0 不能同时代表“无边”和“零权边”

无权邻接矩阵把 `0` 解释为无边没有问题，因为存在边统一写作 `1`。一旦矩阵单元存的是权重，零却是合法的边成本。例如有向边 $0\to1$ 的权重为 $0$、$1\to2$ 的权重为 $4$ 时，若仍用 `0` 填充“无边”，矩阵中的 `matrix[0][1]` 与 `matrix[0][2]` 都是 0，却分别表示“零权边”和“根本无边”。原图已无法从矩阵恢复。

```python
from projects.algorithm_lab.graph_representations import (
    weighted_matrix_sentinel_certificate,
    weighted_matrix_sentinel_report,
)

edges = [[0, 1, 0.0], [1, 2, 4.0]]
report = weighted_matrix_sentinel_report(3, edges, directed=True)

assert report["weighted_adjacency_matrix"][0][1] == 0.0
assert report["weighted_adjacency_matrix"][0][2] is None  # 明确的“无边”哨兵
assert report["zero_sentinel_matrix"][0][1] == report["zero_sentinel_matrix"][0][2] == 0.0
assert report["zero_as_no_edge_is_lossy"]
assert weighted_matrix_sentinel_certificate(3, edges, True, report)
```

这里用 `None` 表示无边；也可采用 $+\infty$（尤其在最短路初始化中），但必须把“边存在性”与“权重数值”分开。报告将歧义边对、两种矩阵和原边表绑定，篡改“0 方案无损”的结论会被证书拒绝。它不选择真实系统的稀疏格式，也不规定负权或多重边该如何建模。

## 推导：操作决定成本，而非表示名称

设顶点 $u$ 的度为 $\deg(u)$。未排序邻接表的单次查边 `u -> v` 最坏检查 $\deg(u)$ 个邻居，邻接矩阵只读取 $A_{uv}$，即 $O(1)$。但枚举 `u` 的全部邻居时，列表只读这 $\deg(u)$ 个真实邻居，而矩阵必须测试 $V$ 个列位置：

$$\text{查边：列表 }O(\deg(u))\ \text{vs. 矩阵 }O(1),\qquad
\text{枚举邻居：列表 }O(\deg(u))\ \text{vs. 矩阵 }O(V).$$

因此 BFS/DFS 配邻接表通常为 $O(V+E)$：所有被扫描的列表长度相加为有向图 $E$、无向图 $2E$。若机械改为邻接矩阵，扫描每个已访问顶点的一整行；完整可达时复杂度为 $O(V^2)$。这在稀疏图上可能大幅浪费，但在本来就稠密的图上未必是主要劣势。上面的重放报告进一步把“大 O”落到某个起点实际访问的顶点数上，而不把一次小图计数误报为普遍性能结论。

## 正确性：两种表示为何回答同一个边问题

构造时对每一条有向边 $(u,v)$，同时执行“将 `v` 加入 `adjacency[u]`”与“置 `matrix[u][v]=1`”。故对任意查询 $(u,v)$，`v in adjacency[u]` 当且仅当 `matrix[u][v] == 1`。无向边再对称执行一次，所以同样结论在两个方向都成立。

合同禁止重复边，保证列表成员关系与矩阵的 0/1 状态一一对应；若允许多重边，矩阵必须改成计数或权重，而不能再把 `1` 解释为完整信息。报告按顶点排序邻居，使相同边集的重放输出稳定；排序只用于证书文本，不改变图的边语义。

## 失败案例与工程边界

- **无向边写成单向。** 若只把 `[0,1]` 放入 `adjacency[0]`，列表已不再是无向图；矩阵也必须同时填 `A[1][0]`。
- **把矩阵的 0 当作不存在顶点。** 顶点存在由 `V` 定义；0 只表示这对顶点之间没有边。
- **把“矩阵查边快”扩大为“矩阵总是快”。** 枚举邻居、存储和缓存局部性是不同问题，需按工作负载判断。
- **把稀疏判定当硬阈值。** 密度没有放之四海而皆准的分界线；本报告刻意只给结构计数，不自动替业务选表示。
- **把 0/1 矩阵用于加权或多重边。** 这些模型需要值域、无穷距离或计数的独立合同。

## 常见误区

- **“邻接表的行数等于边数。”** 不对；每个顶点都有一个邻居容器，行数是 $V$。
- **“无向图的邻居槽位是 $E$。”** 不对；每条无向边出现在两个列表，合计 $2E$。
- **“有了矩阵就不需要边表。”** 输入边表、矩阵和列表各服务不同阶段；从何种来源重建、如何处理重复，都属于接口。
- **“邻接矩阵必须是对称的。”** 只有无向图如此；有向图通常不对称。

## 练习

1. 对 `V=5`、无向边 `[[0,1],[0,2],[3,4]]` 写出邻接表，并计算邻居槽位与矩阵格数。
2. 对有向边 `0 -> 1`，写出矩阵中两个相关格的值；解释为什么交换行列会改变关系。
3. 图有 $V=1000,E=3000$，若对每个顶点枚举邻居一次，比较列表和矩阵总检查数量的量级。
4. 设计一个多重边场景，说明为什么本页 0/1 矩阵合同不能完整保存它。

## 练习答案提示

1. 列表为 `[[1,2],[0],[0],[4],[3]]`；邻居槽位为 6，矩阵格为 25。
2. `A[0][1]=1`、`A[1][0]=0`；行是源顶点、列是目标顶点，调换即反向查询。
3. 列表总扫描为 $2E=6000$（无向约定），矩阵为 $V^2=10^6$；这解释稀疏遍历的巨大差异。
4. 例如两条平行道路 `0--1`；0/1 只能说明“至少一条”，需要计数矩阵或边对象列表记录两条。

## 延伸

[图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)将邻接表用于遍历；[BFS](/discrete-math/breadth-first-search)从列表扫描推导 $O(V+E)$；[最短路算法选择](/discrete-math/shortest-path-algorithm-selection)会把查询量、密度与矩阵型全源算法放入同一决策框架。
