---
title: 批量最短路更新：边身份、顺序快照与重算审计
description: 用稳定边 ID 和顺序化更新快照，审计平行边删除、改权与插入后的最短路变化；完整重算是正确性 oracle，不是动态算法性能声明。
courseLevel: "3（动态图与可重放审计）"
prerequisites: "Dijkstra、增量最短路、最短路边删除"
estimatedMinutes: 65
experiment: "ordered-shortest-path-updates/v1：稳定边 ID 的顺序更新与逐步 Dijkstra 重放"
---

# 批量最短路更新：边身份、顺序快照与重算审计

## 学习目标

你将能说明端点对 $(u,v)$ 不足以标识一条边；将插入、删除和改权写成有序快照转换；重放每一步的最短路；并区分“每一步正确”与“存在高效动态维护算法”。

## 从一个平行边问题开始

图中同时有 `fast: 0→1,1` 与 `slow-parallel: 0→1,9`，再有 `to-target: 1→2,1`。删去 `fast` 后最短距离从 2 变为 10；删去 `slow-parallel` 则仍为 2。两条边的端点相同，只记录 $(0,1)$ 会让“删除哪一条”失去含义。

若接着插入 `shortcut: 0→2,2`，先删后插与先插后删虽然最终都可能到达 2，却经过不同中间快照。批量更新不是无序集合；它是一段状态转换序列。

## 定义与推导：稳定身份与有序状态

令图快照为 $G_k=(V,E_k)$，每条边为 $(id,u,v,w)$，其中 `id` 在快照内唯一。一次更新 $U_k$ 产生

$$G_{k+1}=U_k(G_k).$$

删除只在目标 `id` 属于 $E_k$ 时有定义；插入要求新 `id` 尚未出现；改权也以 `id` 精确定位。于是报告不是只比较 $G_0,G_m$，而是绑定完整链

$$G_0\xrightarrow{U_0}G_1\xrightarrow{U_1}\cdots\xrightarrow{U_{m-1}}G_m.$$

对每个 $G_k$，本课运行非负边 Dijkstra 并保存目标距离与路径。完整重算给出教学 oracle：若报告中的某步距离与该快照直接计算不一致，序列结论就不可信。它不推出增量更新的复杂度优势。

## 算法：顺序应用、每步完整验证

合同限定小图、非负有限权和至多六项更新。每项只能是 `insert(edge)`、`delete(edge_id)` 或 `set_weight(edge_id, weight)`；运行时先检查 ID 合同，再产生新快照并重放 Dijkstra。这样“改权”不被偷偷解释成删除加插入，“平行边删除”也不会误删所有端点相同的边。

```python
from projects.algorithm_lab.batch_shortest_path_updates import (
    ordered_shortest_path_updates_certificate,
    ordered_shortest_path_updates_report,
)

state = {"vertex_count": 3, "source": 0, "target": 2,
         "edges": [["fast", 0, 1, 1], ["slow-parallel", 0, 1, 9], ["to-target", 1, 2, 1]]}
updates = [{"kind": "delete", "edge_id": "fast"},
           {"kind": "insert", "edge": ["shortcut", 0, 2, 2]}]
report = ordered_shortest_path_updates_report(state, updates)
assert report["steps"][1]["dijkstra"]["target_distance"] == 10.0
assert report["steps"][2]["dijkstra"]["target_distance"] == 2.0
assert ordered_shortest_path_updates_certificate(state, updates, report)
```

运行 `python -m unittest projects.algorithm_lab.test_batch_shortest_path_updates`。证书会重建每个快照、操作与 Dijkstra 报告；篡改距离、重排更新或引用不存在的 ID 都会失败。

## 正确性与复杂度边界

唯一 ID 使每个更新的目标边无歧义；按列表顺序应用使 $G_k$ 唯一；每个快照由 Dijkstra 从其实际边集重算，故报告的每一步都满足非负权最短路定义。若一批有 $m$ 次更新，当前教学 oracle 的成本约为

$$O\left(m(V+E)\log V\right).$$

这不是在线动态图的最优界。生产系统还要考虑并发版本、事务原子性、边 ID 的持久化、查询缓存、替换路径索引与摊还复杂度；本课故意不把“有完整审计”误称为“更新更快”。

## 失败案例与工程边界

- **端点对当 ID。** 平行边被混淆，删除语义不再确定。
- **把批量当集合。** 重排插入/删除会改变中间快照和可审计事件。
- **只验证最终图。** 中间决策可能已基于错误路径；需保留每步快照。
- **负权更新。** Dijkstra 的定型不变量不成立，合同明确拒绝。
- **把完整重算用于高频生产更新。** 它是可读 oracle；真正的动态算法需单独的数据结构与性能证据。

## 常见误区

- “最终距离一样，所以顺序无关。”最终值相同不证明中间报告和行动语义相同。
- “边权和端点足以定位边。”平行边或重复权重会反驳它。
- “证书通过就说明并发安全。”本合同只处理单一、顺序化快照流。
- “完整重算无用。”它是教学中检验局部/动态算法的可靠 oracle。

## 练习

1. 为什么删除 `fast` 与删除 `slow-parallel` 必须有不同结果？
2. 推导为何 $G_{k+1}=U_k(G_k)$ 需要保留更新顺序。
3. **编码**：将示例操作改成对不存在 ID 的删除或重复 ID 插入，确认合同拒绝；再篡改第二步距离，确认重放证书失败。
4. **开放**：给高频路由服务设计边 ID、版本号、事务边界和替换路径缓存的职责分工。

## 练习答案提示

1. 两边端点相同但权重不同；稳定 ID 是操作对象，端点只是属性。
2. 每步的输出是下一步输入；一般 $U_1(U_0(G))$ 不等于 $U_0(U_1(G))$。
3. 区分引用不存在、重复身份和报告篡改三种失败；它们不应被默默忽略。
4. 分别说明谁分配 ID、谁保护版本顺序、谁提交原子快照、谁在缓存失效后重算；不要把这些治理问题塞进 Dijkstra。

## 下一步

[增量最短路](/discrete-math/incremental-shortest-path)说明单边插入为何可局部下降传播；[最短路边删除](/discrete-math/deletion-shortest-path)说明删除为何需要替换路径思维。更复杂的批量动态算法必须从这些明确的身份与快照语义出发。
