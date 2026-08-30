---
title: 强连通分量：把有向环压缩成 DAG
description: 从互相可达的等价关系推导 Kosaraju 两次 DFS，构造强连通分量并解释凝聚图为何无环。
courseLevel: "2（图算法、证明与工程建模）"
prerequisites: "有向图、DFS、完成时间与集合等价关系"
estimatedMinutes: 60
experiment: "实现 Kosaraju 算法，将有向图划分为强连通分量并验证 DAG 顶点均为单例"
---

# 强连通分量：把有向环压缩成 DAG

## 学习目标

读完后，你能定义强连通分量；证明互相可达构成等价关系；推导 Kosaraju 的两次 DFS；实现可测试的分量划分；并解释为何将每个分量压缩后必得到 DAG。

## 从循环依赖开始

在依赖图中 `a → b → a` 的两个模块无法单独排序；若又有 `b → c → d → c`，问题不是“有一个环”这么简单，而是存在两个互相可达的组件。强连通分量（SCC）将每个最大互相可达集合压成一个点，循环依赖变为可定位单元，其余组件可继续按 DAG 处理。

## 定义与推导

在有向图中定义 $u\sim v$ 当且仅当 $u$ 可达 $v$ 且 $v$ 可达 $u$。自反、对称、传递性分别来自空路径、定义对称和路径拼接，故 $\sim$ 是等价关系；等价类就是 SCC。

Kosaraju 算法先在原图 DFS，按完成时间排序；再在反图中按完成时间降序 DFS。第一次搜索的最后完成顶点所在的 SCC 在凝聚 DAG 中是源或汇（取决于边方向约定）；反图搜索从它出发不会越过到尚未处理的分量，于是恰好收集一个 SCC。删除该分量后归纳重复。

## 为什么两遍 DFS 不会混合组件

先把每个 SCC 看成一个点，得到凝聚图 $G_\mathrm{SCC}$。它若含有环，例如 $C_1\to C_2\to\cdots\to C_1$，就能沿环让任意两个组件互达；它们本应是同一个最大 SCC，矛盾。因此凝聚图是 DAG。

第一遍在原图记录完成时间。对尚未处理的组件，最高完成时间对应凝聚 DAG 的一个源组件；否则若有别的未处理组件能进入它，沿该边的 DFS 完成次序会迫使前驱组件拥有更晚的完成时间。将所有边反向后，这个源组件变为汇组件，第二遍从它出发没有通向其他未处理组件的反向边；但 SCC 内任意点仍可相互到达，所以本轮 DFS 恰好收集一个完整等价类。

每轮把已收集组件排除后，同一论证作用于剩余凝聚 DAG。这给出归纳不变量：第二遍已经输出的集合是若干完整、两两不交的 SCC，未访问顶点仍是其余 SCC 的并集。最终所有顶点恰好属于一个组件。

## 可运行实现

```python
from projects.algorithm_lab.strongly_connected import condensation_report, strongly_connected_components

graph = {"a": ["b"], "b": ["a", "c"], "c": ["d"], "d": ["c"], "e": []}
parts = strongly_connected_components(graph)
assert {frozenset(part) for part in parts} == {frozenset({"a", "b"}), frozenset({"c", "d"}), frozenset({"e"})}

report = condensation_report(graph)
assert report["valid"]
assert len(report["topological_order"]) == len(parts)
```

```bash
python -m unittest projects.algorithm_lab.test_strongly_connected
```

实现使用显式栈。先遍历原图记录完成顺序，再建立反图并按逆完成顺序收集分量；`condensation_report` 随后把跨组件边映射到组件编号，并用 Kahn 算法给出“每条跨组件边都从拓扑序前面指向后面”的证书。每条边在建反图、两遍 DFS 和凝聚图中只处理常数次，故时间 $O(V+E)$、空间 $O(V+E)$。

## 正确性与工程边界

第二次 DFS 只沿反图边走；完成时间顺序保证从一个尚未处理的起点开始时，能到达的未处理顶点正是其互相可达类。测试验证含两个环和孤立点的划分、DAG 中的单例分量、跨组件边的拓扑证书及缺失顶点的拒绝。

凝聚图不可能有环：若分量间有环，各分量顶点便可沿环互达，应属于同一最大分量，矛盾。算法依赖完整邻接表；漏掉边终点会破坏反图和分量定义。

## 常见误区

1. “有向连通就是 SCC。”错误：单向可达不代表能回来。
2. “任何 DFS 顺序都能做第二遍。”错误：必须按第一遍完成时间逆序。
3. “SCC 内只包含简单环。”错误：它是所有互相可达顶点的最大集合。
4. “压缩后仍可能有环。”错误：若有环就没有压缩到最大 SCC。

## 练习

1. **基础题**：为三个 SCC 画一张凝聚图，并列出其拓扑序。
2. **推导题**：证明互相可达关系的传递性，并说明为何因此能划分等价类。
3. **编码题**：返回每个顶点所属组件编号，并验证跨组件边构成 DAG。
4. **开放题**：为包依赖扫描设计 SCC 报告：如何显示最小循环、组件规模和修复优先级？

## 练习答案提示

1. 将每个 SCC 收缩成一个点，原图跨组件边成为凝聚图边；对该 DAG 做拓扑排序，注意孤立组件也要出现。
2. 自反、对称、传递性分别来自零长度路径、反向可达和路径拼接；因此互达关系确实是等价关系，组件是等价类。
3. 组件编号需覆盖所有顶点；遍历每条原边，若端点编号不同则加入凝聚边，再用拓扑排序或 DFS 验证没有环。
4. 报告可按组件大小和影响范围排序，但最小循环需要在 SCC 内另找回边/最短环；输出应区分“结构事实”和“业务修复优先级”。

## 延伸

[DFS](/discrete-math/depth-first-search)给出完成时间的基础；[拓扑排序](/discrete-math/graph-foundations-topological-sort)处理凝聚后的 DAG；[算法实验室](/projects/algorithm-lab)收录实现。继续学习可检索 Tarjan algorithm、2-SAT、condensation graph。
