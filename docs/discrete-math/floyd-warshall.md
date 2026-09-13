---
title: Floyd–Warshall：全源最短路与动态规划
description: 用“允许的中间点集合”推导 Floyd–Warshall，处理负边、检测负环，并实现可验证的全源最短路。
courseLevel: "2–3（动态规划、图算法与复杂度边界）"
prerequisites: "图、最短路、动态规划与 Bellman–Ford"
estimatedMinutes: 60
experiment: "实现 Floyd–Warshall，验证负边、多重边、不可达点与负环"
---

# Floyd–Warshall：全源最短路与动态规划

## 学习目标

读完后，你能推导 Floyd–Warshall 的状态转移；说明为何它允许负边但不允许负环；实现并验证全源距离矩阵；并在多源、稠密和大规模图之间判断其工程边界。

## 从多次查询开始

路由系统若只问“从一个源到所有点”，Dijkstra 或 Bellman–Ford 合适；若不断问任意两点间距离，重复运行单源算法会变得笨重。Floyd–Warshall 一次计算所有 $V^2$ 个答案，代价是 $O(V^3)$，特别适合顶点数不大、图较稠密或全源查询很多的场景。

## 状态定义与分步推导

按编号逐步允许中间点。令 $D^{(k)}[i,j]$ 为从 $i$ 到 $j$、中间点只可取自 $\{0,\ldots,k\}$ 的最短长度。允许点 $k$ 后，最优路径要么不经过它，要么首次分为两段：

$$D^{(k)}[i,j]=\min\left(D^{(k-1)}[i,j],D^{(k-1)}[i,k]+D^{(k-1)}[k,j]\right).$$

初值 $D^{(-1)}[i,i]=0$，边权填入对应格，其他为 $\infty$。三重循环以 `middle → source → target` 的顺序原地更新，正是这个递推的空间压缩版本。

## 可运行实现

```python
from projects.algorithm_lab.floyd_warshall import (
    floyd_warshall_path_certificate,
    floyd_warshall_trace,
    floyd_warshall_trace_certificate,
    floyd_warshall_with_paths,
    recover_floyd_warshall_path,
)

edges = [(0, 1, 4), (0, 2, 11), (1, 2, -2)]
distance, trace = floyd_warshall_trace(3, edges)
assert distance[0][2] == 2.0
assert floyd_warshall_trace_certificate(3, edges, distance, trace)
```

```bash
python -m unittest projects.algorithm_lab.test_floyd_warshall
```

初始化取平行边的最小权重，故不会因输入顺序改变答案。`floyd_warshall_trace` 记录每个 `middle` 完成后的完整距离矩阵；证书从初始边表独立重放三重循环，并拒绝任何被篡改的层。若最后存在 $D[i,i]<0$，则有从 $i$ 回到自己的负长度闭路，任意绕行次数都能使路径更小，最短距离无定义，项目会显式拒绝。NaN 和无穷边权也会在输入处被拒绝，而非进入比较后静默污染状态。

## 距离从哪里来：用 `next` 矩阵恢复路径

只报告 `distance[0][2] == 2` 还不能说明这条最短路经过哪些顶点。初始化时对一条边 $i\to j$ 令 `next[i][j] = j`；当通过 `middle` 改善 $i\to j$ 时，第一跳应更新为 `next[i][middle]`，而不是 `middle` 本身。这样从源点不断读取 `next[current][target]`，便能沿最短路走到目标：

```python
distance, next_hop = floyd_warshall_with_paths(3, edges)
path = recover_floyd_warshall_path(next_hop, 0, 2)

assert path == [0, 1, 2]
assert floyd_warshall_path_certificate(3, edges, distance, next_hop, 0, 2, path)
assert recover_floyd_warshall_path(next_hop, 2, 0) is None
```

`floyd_warshall_path_certificate` 从边表重算距离和下一跳矩阵，再绑定指定源、目标与恢复路径；将第一跳篡改为直达 `2` 或报告一条不存在的边都会失败。若存在负环，路径和距离都没有定义，函数与原算法一样拒绝输入。

## 负环不只影响环上顶点：哪些点对的答案会失效

“某处有负环，所以整个距离矩阵都不能用”与“只把环上的距离删掉”都不精确。令最终 DP 矩阵中某个顶点 $k$ 满足

$$
D[k,k] < 0.
$$

若存在从 $i$ 到 $k$ 的路、也存在从 $k$ 到 $j$ 的路，即

$$
D[i,k] < \infty,\qquad D[k,j] < \infty,
$$

则 $(i,j)$ 的最短距离没有有限最小值。把进入路径记为 $P$、离开路径记为 $Q$、负环记为 $C$，可构造一族走法

$$
P + \underbrace{C+\cdots+C}_{m\text{ 次}} + Q,
\qquad
w(P)+m\,w(C)+w(Q)\longrightarrow-\infty.
$$

这正是全源版本的“可进入且可离开”条件；`D` 在最后一轮留下的某个有限数值不能再被当成该点对的最短路。

```python
from projects.algorithm_lab.floyd_warshall import (
    floyd_warshall_negative_cycle_certificate,
    floyd_warshall_negative_cycle_report,
)

edges = [
    (0, 1, 2), (1, 2, 1), (2, 1, -3),  # 1 → 2 → 1 的权重为 -2
    (2, 3, 2), (3, 4, 5),
]
report = floyd_warshall_negative_cycle_report(5, edges)

assert report.negative_cycle_vertices == (1, 2)
assert report.pair_status[0][3] == "undefined_by_negative_cycle"
assert report.pair_status[0][4] == "undefined_by_negative_cycle"
assert report.pair_status[3][4] == "finite"
assert report.pair_status[4][0] == "unreachable"
assert floyd_warshall_negative_cycle_certificate(5, edges, report)
```

报告不会伪造受影响点对的数值距离，而是把它们标为 `undefined_by_negative_cycle`；证书从冻结边表重跑全部 DP 和可达条件。把 $(0,3)$ 改写为 `finite` 会被拒绝。这和主算法的 fail-closed 行为互补：主算法防止调用方误用整张矩阵，报告则解释拒绝究竟覆盖哪些查询。

## 正确性与复杂度

对 `middle` 归纳：初始矩阵恰是没有中间点的最短边；递推枚举经过或不经过新增中间点的全部合法路径，故保持定义。全部顶点允许后，任何简单路径的中间点均被覆盖，得到最短路。三重循环是 $O(V^3)$ 时间、$O(V^2)$ 空间；这不是稀疏大图的默认选择。

## 失败案例与工程边界

- **负环**：负边允许，负环不允许；可进入并离开负环的点对最短值为 $-\infty$，而与它隔离的点对仍可能有有限距离或不可达状态。
- **无穷值相加**：实现依赖 `inf` 传播；固定宽度整数语言须避免“无穷哨兵 + 权重”溢出。
- **浮点权重**：舍入可能制造极小负对角线；优先用整数成本，或定义容差语义。
- **规模**：$10^4$ 个顶点的矩阵本身就需约一亿项，时间和内存都不可接受。

## 常见误区

1. “负边就不能用 Floyd–Warshall。”错误：只要没有负环即可。
2. “它只比 Bellman–Ford 多一层循环。”错误：状态是允许中间点集合，而非路径边数。
3. “负环只影响环上的点。”错误：能进入并离开该环的点对都可能没有定义的最短值。
4. “全源预处理总是更快。”错误：取决于查询数量、稀疏度和内存预算。

## 练习

1. **基础题**：手算上例在允许中间点 1 前后的 `distance[0][2]`。
2. **推导题**：完成状态转移的归纳正确性证明。
3. **编码题**：运行 `floyd_warshall_negative_cycle_report`，解释为何 $(0,4)$ 是 `undefined_by_negative_cycle`、$(3,4)$ 仍为 `finite`；再篡改一个状态并确认负环证书拒绝。
4. **开放题**：为稀疏地图、多源查询服务和小型课程依赖图分别选择算法，并列出要测量的规模指标。

## 练习答案提示

1. 分别比较直达边与经允许中间点的两段距离；写出更新前后值，并保持不可达为无穷而不是任意大整数。
2. 归纳状态是“中间点只取自前 $k$ 个顶点的最短距离”；新路径要么不用 $k$，要么经过 $k$ 并分成两段。
3. 先找到负对角顶点 $1,2$；$0$ 可进入它们且它们可到达 $4$，故可重复负环让 $(0,4)$ 趋于 $-\infty$。$3$ 无法回到环，所以 $(3,4)$ 保留有限路径；证书应重放每个点对的可达条件。
4. 记录顶点数、边数、查询批量、权重符号与内存预算；稀疏地图通常不适合 $V^2$ 表，多源服务才可能摊销全源预处理。

## 延伸

[Bellman–Ford](/discrete-math/bellman-ford)以路径边数为不变量处理单源负边；[动态规划](/discrete-math/dynamic-programming-dag)提供状态设计语言；[算法实验室](/projects/algorithm-lab)收录本实现。继续学习可检索 Johnson 重加权、min-plus 矩阵乘法与动态最短路。
