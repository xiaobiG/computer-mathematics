---
title: 最短路边删除：旧路径失效后为何不能只做下降松弛
description: 在单条非负边删除的受限合同下，审计旧父路径、完整重算与替代路径，理解距离只能变差而不能靠插入修复复用。
courseLevel: "3（动态图、Dijkstra 前提与重放审计）"
prerequisites: "Dijkstra、增量最短路、最短路算法选择"
estimatedMinutes: 55
experiment: "删除一条边后重放 Dijkstra，比较旧路径、替代路径与目标距离"
---

# 最短路边删除：旧路径失效后为何不能只做下降松弛

## 学习目标

- 区分插入边的“标签下降”与删除边的“父路径可能失效”；
- 推导非负边删除后距离只能保持或变大；
- 用完整重算审计一条删除边是否破坏旧的目标路径；
- 明确替换路径算法与本页的小图重放合同之间的界限。

## 从一个更新问题开始

旧图中 $0\to1\to3$ 的权重为 $1+1=2$，另有绕行 $0\to2\to3$ 的权重为 $4+4=8$。删除 $(1,3,1)$ 后，旧父指针指向的边已经不存在。把旧距离 $d(3)=2$ 留在堆中不会产生“待下降的种子”：正确的新距离是 8，方向恰好与单边插入相反。

删除一条与当前目标路径无关的边也可能不改变该目标距离，但这不是许可重用整份旧报告：它只是一份需要由新图重算确认的结论。

## 定义与推导：为什么距离只会上升

令 $G'=(V,E\setminus\{e\})$ 是从非负权图 $G=(V,E)$ 删除一条边得到的图。$G'$ 的每一条 $s\to x$ 路径原本也在 $G$ 中，因此可选路径集合变小：

$$
\mathrm{dist}_{G'}(s,x)\ge \mathrm{dist}_{G}(s,x),
$$

其中不可达可视为 $+\infty$。这与插入边时的“距离只能下降”形成对偶，却不能直接得到新标签：若旧最短路径经过 $e$，必须寻找绕开 $e$ 的替换路径。

对源点最短路树而言，删除的边若是记录父链的一部分，受影响的节点可能形成整棵子树；每个节点的最佳替换边又可能来自树外。仅从某个端点向外做 Dijkstra 松弛只能发现更小距离，无法发现某个原标签已经失去支撑。因此本课选择完整重算作为小图正确性 oracle；真正的动态替换路径算法需要额外的数据结构、不变量与复杂度证明。

## 可运行实验：路径失效与替代路径

```python
from projects.algorithm_lab.deletion_shortest_path import (
    deletion_shortest_path_certificate,
    deletion_shortest_path_report,
)
from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION

before = {
    "contract_version": CONTRACT_VERSION,
    "vertex_count": 5,
    "edges": [[0, 1, 1], [1, 3, 1], [0, 2, 4], [2, 3, 4], [0, 4, 2]],
    "source": 0,
    "target": 3,
}
after = {**before, "edges": [edge for edge in before["edges"] if edge != [1, 3, 1]]}
report = deletion_shortest_path_report(before, after)

assert report["before"]["distances"] == 2.0
assert report["after"]["distances"] == 8.0
assert report["audit"]["deleted_endpoint_pair_is_in_recorded_old_target_path"]
assert report["audit"]["target_distance_worsened_or_became_unreachable"]
assert report["audit"]["full_recomputation_required_by_this_contract"]
assert deletion_shortest_path_certificate(before, after, report)
```

运行 `python -m unittest projects.algorithm_lab.test_deletion_shortest_path`。报告绑定删除的边、删除前后的 Dijkstra 重放、旧目标路径、新目标路径和目标距离变化。证书会重建整份报告，篡改“需要完整重算”或距离结论都会失败。

注意 `deleted_endpoint_pair_is_in_recorded_old_target_path` 只检查记录路径中的端点对；有平行边时端点相同不自动证明删除的是那条具体边。这个保守标记提醒我们：父路径、边身份和多重边语义必须一起记录，不能仅凭两个顶点下结论。

## 正确性、复杂度与工程边界

本合同先拒绝顶点、源点、目标改变，拒绝插入/改权混入，并只接受非负有限权的**恰好一条删除边**。它随后分别对旧图和新图运行 Dijkstra，因此新报告的距离与路径由新边集直接得到；前面的路径集合包含关系解释为何目标距离不会变小。

每次完整重算的时间为 $O((V+E)\log V)$，空间为 $O(V+E)$。这不是动态删除的最优复杂度，也没有把“删除边不在记录路径上”当作跳过重算的判据。大图系统可考虑替换路径、动态树、批量更新策略和查询分布，但必须分别声明边身份、并发快照、更新序列、最坏/摊还复杂度与失效语义。

## 失败案例与工程边界

- **沿用插入修复。** 它只传播下降标签，不能发现距离应从 2 增加到 8。
- **只看目标路径。** 一条不在当前记录路径上的边仍可能改变并列最短路、其他查询或后续更新的证据。
- **混合删除、插入和改权。** 它们的单调性不同；本合同拒绝混合更新而非猜测顺序。
- **负边。** Dijkstra 的定型论证不成立，应改用适合的静态重算或另建合同。
- **把完整重算包装成增量算法。** 本页把完整重算明确当 oracle；没有声称局部速度优势。

## 常见误区

- “旧路径没有使用被删边，所以旧报告一定有效。”不对，整份报告绑定的是旧图快照。
- “距离变大说明原 Dijkstra 算错了。”不对，输入边集变了，问题本身变了。
- “残留一个旧父指针即可证明替代路径。”不对，父边可能已经不存在，必须在新图验证每条边。

## 练习

1. **基础**：证明删边后任意点的最短距离不会下降。
2. **推导**：给出一个删去最短路树根边、使多个后继节点都必须改走替代路径的例子。
3. **编码**：删除示例中的 `[0, 4, 2]`，比较报告为何显示目标距离未变却仍要求完整重算。
4. **开放**：为平行边设计一个“端点对相同而边身份不同”的输入；说明报告还需记录什么才能识别具体被删边。

## 练习答案提示

1. 新图路径集是旧图路径集的子集；最小值只能保持或升为无穷。
2. 让根经一条轻边进入一棵子树，再设置一条更贵的旁路；删除轻边后每个子树节点的父链都失效。
3. 该边不在记录的目标路径上，但报告仍从新图计算全部 Dijkstra 标签；输入指纹已改变。
4. 除端点外记录权重、平行边实例 ID 或稳定边 ID；仅用 $(u,v)$ 会混淆不同边。

## 延伸

[增量最短路](/discrete-math/incremental-shortest-path)处理单边插入的下降传播；[Dijkstra](/discrete-math/dijkstra)给出非负权定型不变量；[最短路算法选择](/discrete-math/shortest-path-algorithm-selection)将前提变化与算法选择放在同一输入上比较。
