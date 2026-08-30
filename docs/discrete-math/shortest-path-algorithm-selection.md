---
title: 最短路算法选择：在同一张图上比较 BFS、Dijkstra、Bellman–Ford 与 Floyd–Warshall
description: 从边权、负环、源点数量和图密度推导最短路算法选择，并用同图交互面板审计前提、路径和不变量。
courseLevel: "2–3（图算法、证明与工程边界）"
prerequisites: "BFS、Dijkstra、Bellman–Ford、Floyd–Warshall 与渐进复杂度"
estimatedMinutes: 65
experiment: "在同一规模的无权、非负权、负边和负环图上对照四种最短路算法的前提与结果"
---

# 最短路算法选择：在同一张图上比较 BFS、Dijkstra、Bellman–Ford 与 Floyd–Warshall

## 学习目标

读完后，你能按边权、负环、源点数量和图规模选择最短路算法；解释 BFS 分层、Dijkstra 定型、Bellman–Ford 边数轮次和 Floyd–Warshall 中间点集合这四种不变量；区分“算法拒绝前提”和“图中不存在路径”；并用统一报告与重放证书审计结论。

## 从一个计算问题开始

边代表“下一跳”时可用 BFS；边代表运输成本时却不能再把每条边视为等价。若有负权补贴，未来路径可改善眼前最优；若有负环，所谓最短成本根本不存在。问题不是“哪个算法最强”，而是这张图的数学结构允许算法承诺什么。

## 直觉与定义：四种状态语言

设有向图 $G=(V,E)$、边权 $w(u,v)$、源点 $s$。

| 算法 | 前提 | 状态不变量 | 解决范围 |
| --- | --- | --- | --- |
| BFS | 每条边等价（权 1） | 队列按非递减边数层级处理 | 单源最少边数 |
| Dijkstra | 所有边权非负 | 最小暂定距离被弹出时可最终确定 | 单源非负权最短路 |
| Bellman–Ford | 源点可达区域无负环 | 第 $k$ 轮是至多 $k$ 条边的最短路径 | 单源、允许负边 |
| Floyd–Warshall | 图中无负环 | 第 $k$ 层只允许前 $k$ 个顶点作中间点 | 所有源点对 |

只有每条边权都为 1 时，路径总权重才等于边数：

$$w(P)=\lvert E(P)\rvert.$$

所以 BFS 的层数才可解释为最小总权重。Dijkstra 的贪心步骤则严格依赖非负性：通向未确定节点的任何延伸都不能让当前最小标签变小。Bellman–Ford 按边数冻结上一轮标签，Floyd–Warshall 按允许的中间点集合做动态规划；它们各自覆盖不同前提。

## 交互实验：同图先看前提

<ShortestPathComparisonExplorer />

切换四类图，先看“适用”或“拒绝”，再看路径：无权图中四种算法都可运行；非负加权图中 BFS 被拒绝；有负边、无负环时 Dijkstra 被拒绝；出现负环时 Bellman–Ford 与 Floyd–Warshall 都拒绝有限最短路结论。拒绝不是算法失败，而是避免把不受保证的数字伪装成最优解。

## 自定义小图：输入契约与可重放报告

上面的“自定义小图”选项允许修改顶点数、起点、终点和边表。它刻意不是通用图编辑器：顶点必须从 $0$ 连续编号，数量限制为 $2\ldots8$；边数至多 20；每条边写成 `起点 终点 权重`，权重必须有限且绝对值不超过 10,000。点击“应用并审计”前，错误输入不会覆盖当前可用图。

展开“查看可重放输入与浏览器报告”后可以复制输入 JSON。复制的输入而不是浏览器显示的结论才是重放锚点：将它交给 Python 会重新计算所有算法卡片，并用证书拒绝被篡改的结果。

## 查询数量：从“能用”到“该不该预处理”

同一张图上的一次单源查询和 $Q$ 次独立单源查询不是同一个成本问题。交互面板的“查询数量与成本”区将 $Q$ 从 1 调到当前顶点数：BFS、Dijkstra、Bellman–Ford 的工作量会随 $Q$ 线性增加；Floyd–Warshall 的 $V^3$ 预处理则只付一次。这些数字是用于比较增长趋势的理论单位，不是不同电脑上不可复现的毫秒排名。

Python 报告会重放同一份输入，记录真正被扫描的边、实际发生的成功松弛和 Floyd–Warshall 的候选矩阵格。这里的“查询”定义为一次完整的单源运行，而非目标出现后提前停止；这样四张卡才在相同的比较口径下成立。

## 目标查询、密度与内存：停止也需要证明

若只问从 $s$ 到固定目标 $t$ 的距离，BFS 在 $t$ **首次出队**后可停止；Dijkstra 在 $t$ **被定型**后可停止。这并不等于“第一次看到 $t$ 就停止”：对 Dijkstra，只有最小暂定距离被弹出时才有证明；对含负边的 Bellman–Ford，后续轮次仍可能改进 $t$；Floyd–Warshall 的状态本来就是所有点对，不能把它改写为目标导向搜索。

同一图还需要选择表示法。若忽略自环，定向密度为

$$\rho=\frac{\lvert\{(u,v)\in E:u\ne v\}\rvert}{V(V-1)}.$$

邻接表约保存 $V+E$ 个槽位；Floyd–Warshall 的核心距离矩阵是 $V^2$ 个格。页面会同时显示这两种空间口径和实际“完整单源扫描 / 目标停止扫描”计数。它们解释了为什么稀疏图、目标查询和大量点对查询会改变问题结构，而不是给出脱离输入的万能赢家。

## 图更新：输出没变，不等于旧证据仍有效

将当前图固定为基线后再修改边表，面板会显示新增/移除边和发生变化的算法卡。一个容易漏掉的情况是：新增一条永远不会出现在 $s\to t$ 路径上的边，最短距离、路径和前提可能都不变；但旧报告绑定的是**旧输入**，它不能证明新图。必须从新的规范化 JSON 重放比较、工作量和目标查询报告。

`shortest_path_update_report` 用规范化输入的 SHA-256 指纹识别图快照，并把平行边当作多重集。因此增加或删除一条重复边也不会被静默吞掉。顶点数、源点和目标若变化，则问题本身不同，报告会拒绝把它包装成“同一次更新”。

## 可运行统一报告

`shortest_path_comparison` 将前提、距离、路径和不变量放入同一报告，并从原始边表重放包括“拒绝卡”在内的全部结论。

```python
from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    shortest_path_comparison,
    shortest_path_comparison_certificate,
    shortest_path_replay_certificate,
    shortest_path_replay_report,
)
from projects.algorithm_lab.shortest_path_workload import (
    shortest_path_workload_certificate,
    shortest_path_workload_report,
)
from projects.algorithm_lab.shortest_path_query_boundary import (
    shortest_path_query_boundary_certificate,
    shortest_path_query_boundary_report,
)
from projects.algorithm_lab.shortest_path_update import (
    shortest_path_update_certificate,
    shortest_path_update_report,
)

edges = [(0, 1, 2.0), (0, 2, 5.0), (2, 1, -10.0), (1, 3, 4.0)]
report = shortest_path_comparison(4, edges, source=0, target=3)
assert report["algorithms"]["dijkstra"]["status"] == "rejected"
assert report["algorithms"]["bellman_ford"]["distance"] == -1.0
assert shortest_path_comparison_certificate(4, edges, 0, 3, report)

payload = {
    "contract_version": CONTRACT_VERSION,
    "vertex_count": 4,
    "edges": [[0, 1, 2], [0, 2, 5], [2, 1, -10], [1, 3, 4]],
    "source": 0,
    "target": 3,
}
replay = shortest_path_replay_report(payload)
assert replay["comparison"]["algorithms"]["bellman_ford"]["distance"] == -1.0
assert shortest_path_replay_certificate(payload, replay)

workload = shortest_path_workload_report(payload, query_count=2)
assert workload["algorithms"]["dijkstra"]["status"] == "rejected"
assert workload["algorithms"]["floyd_warshall"]["work"]["candidate_cells"] == 64
assert shortest_path_workload_certificate(payload, 2, workload)

unit_target_query = {
    "contract_version": CONTRACT_VERSION,
    "vertex_count": 5,
    "edges": [[0, 1, 1], [1, 2, 1], [2, 4, 1], [4, 3, 1]],
    "source": 0,
    "target": 4,
}
boundary = shortest_path_query_boundary_report(unit_target_query)
assert boundary["algorithms"]["dijkstra"]["target_only"]["edge_scans"] < boundary["algorithms"]["dijkstra"]["full_source"]["edge_scans"]
assert boundary["storage"]["floyd_matrix_cells"] == 25
assert shortest_path_query_boundary_certificate(unit_target_query, boundary)

updated = {**unit_target_query, "edges": [*unit_target_query["edges"], [0, 4, 1]]}
update = shortest_path_update_report(unit_target_query, updated)
assert not update["invalidation"]["old_comparison_report_valid_for_after"]
assert "dijkstra" in update["algorithm_outcome_changes"]
assert shortest_path_update_certificate(unit_target_query, updated, update)
```

运行：

```bash
python -m unittest projects.algorithm_lab.test_shortest_path_comparison
```

篡改距离、路径或“Dijkstra 可以处理负边”的理由都会使证书失败。重放合同还会拒绝第 9 个顶点、超过 20 条边、无穷权重、额外字段或错误合同版本；工作量证书还会拒绝被改写的扫描边数、查询源集合或 $V^3$ 候选格计数；目标查询证书还会拒绝被伪装成“安全提前停止”的 Bellman–Ford/Floyd 卡片、密度和内存槽位；更新证书还会拒绝被改写的边增删、输入指纹或“旧报告仍有效”声明。拒绝信息也必须被审计，因为它绑定了算法结论的适用范围。

## 推导、复杂度与工程边界

| 需求 | 通常选择 | 复杂度与原因 |
| --- | --- | --- |
| 单源、无权 | BFS | 邻接表 $O(V+E)$，队列分层即可 |
| 单源、非负权 | Dijkstra | 二叉堆约 $O((V+E)\log V)$，可安全定型 |
| 单源、含负边 | Bellman–Ford | $O(VE)$，可检查可达负环 |
| 大量源点对、小型或稠密图 | Floyd–Warshall | $O(V^3)$，一次得到全源矩阵 |

当 $Q$ 很小，重复单源算法通常不必支付全源矩阵成本；当 $Q$ 接近 $V$ 且图足够小，Floyd–Warshall 的一次预处理开始更容易解释。它不是运行时魔法规则：稀疏性、查询数量、内存预算和是否需要路径证书都会改变选择。真实地图还需处理浮点权重、动态更新和输入契约。

## 正确性、边界与反例

在非负图上，Dijkstra 的确定顺序、父路径和逐边松弛不等式共同构成证据；在负边图上，Bellman–Ford 的冻结轮次保证“至多 $k$ 条边”的归纳含义；Floyd–Warshall 的每层矩阵记录允许中间点集合的扩张。

反例：图中有负环但源点不可达它。Bellman–Ford 的单源结论仍可定义；Floyd–Warshall 解的是全源问题，仍须拒绝。这不是实现不一致，而是问题范围不同。

## 常见误区

- **“BFS 找到的路径总是最短。”** 它只保证最少边数。
- **“Dijkstra 最后检查负边即可。”** 负边会破坏中途定型论证。
- **“Bellman–Ford 发现负环就说明所有点无最短路。”** 需检查负环是否从源点可达、是否影响目标。
- **“Floyd–Warshall 更通用，所以总该用它。”** $O(V^3)$ 对大稀疏图通常不合适。

## 练习

1. **基础题**：证明所有边权为 1 时 BFS 距离和路径总权重相等。
2. **推导题**：写出 Dijkstra 中“最小暂定距离可确定”的反证步骤，并指出非负性在哪里使用。
3. **编码题**：为统一报告添加源点数量建议，并为拒绝卡补充证书测试。
4. **开放题**：设计一个负环不能到达目标的图，讨论到该目标的最短路与全源最短路报告应如何分别表述。

## 练习答案提示

1. 每条边贡献 1，因此总权重就是边数。
2. 取一条更短替代路径上的第一个未定型点；非负最后一边使其候选距离不小于当前最小标签，产生矛盾。
3. 保留原图、源/目标、前提和拒绝理由；不要为了显示一致而给拒绝算法填入路径。
4. 单源全体距离、到特定目标的距离和全源矩阵是不同问题，需分别声明范围。

## 延伸

[BFS](/discrete-math/breadth-first-search)、[Dijkstra](/discrete-math/dijkstra)、[Bellman–Ford](/discrete-math/bellman-ford)和[Floyd–Warshall](/discrete-math/floyd-warshall)分别展开四条证明线；[算法可视化实验室](/projects/algorithm-lab)收录可重放实现。下一步将对 v1.2 的同图、输入、工作量、目标查询与更新证据做收束审计，再决定下一条高价值学习链。
