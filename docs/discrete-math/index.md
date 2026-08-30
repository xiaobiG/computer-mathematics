# 算法背后的离散数学

离散数学研究可数、可枚举、可证明的结构，也是算法正确性与复杂度分析的语言。深度版以“前提—不变量—终止—复杂度—反例”为共同骨架。

## 按层进入

| 层级 | 先学什么 | 达成的能力 | 建议入口 |
| --- | --- | --- | --- |
| 0 · 预备 | 函数、有限求和与程序索引 | 读懂规格、循环区间与计数 | [符号、函数、求和与 Python](/foundations/functions-summation-python) |
| 1 · 核心 | 逻辑、集合、关系与图表示 | 用量词和结构准确描述问题 | [命题逻辑、量词与归纳法](/discrete-math/logic-induction-proofs) → [集合、关系、等价类与偏序](/discrete-math/sets-relations-orders) |
| 2 · 推导与算法 | 循环不变量、BFS/DFS、最短路 | 证明算法正确并分析复杂度 | [循环不变量](/discrete-math/loop-invariants) → [BFS](/discrete-math/breadth-first-search) → [Dijkstra 交互轨迹实验](/discrete-math/dijkstra) |
| 3 · 工程与前沿 | 负边、网络流、归约与测试 | 在前提变化时选择或审计算法 | [Bellman–Ford](/discrete-math/bellman-ford) → [最大流最小割](/discrete-math/max-flow-min-cut) → [算法实验室](/projects/algorithm-lab) |

可以从熟悉的层级开始，但图算法前请先补齐循环不变量与图表示；专题首页的每篇元信息会给出更细的前置条件。

## 课程地图

1. 命题逻辑与程序条件
2. 集合、关系与映射
3. 证明方法与循环不变量
4. 组合计数与递推
5. 渐进复杂度
6. 图论、最短路与网络流

## 当前深度版

- [命题逻辑、量词与归纳法](/discrete-math/logic-induction-proofs)：规格、反例、终止性与循环不变量的证明语言；
- [集合、关系、等价类与偏序](/discrete-math/sets-relations-orders)：分组、依赖与状态空间的共同离散结构；
- [图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)：图表示、DFS、树不变量、二分染色与依赖环；
- [循环不变量](/discrete-math/loop-invariants)：二分查找为何不会漏掉答案；
- [Dijkstra](/discrete-math/dijkstra)：非负边权为何能贪心，以及负权边为何失败；页面内可逐步操作最小堆与松弛轨迹实验；
- [BFS](/discrete-math/breadth-first-search)：队列分层不变量与无权图最短路；
- [DFS](/discrete-math/depth-first-search)：发现/完成时间、显式栈与环检测边界；
- [强连通分量](/discrete-math/strongly-connected-components)：互相可达等价类、Kosaraju 与凝聚 DAG；
- [并查集](/discrete-math/union-find)：森林不变量、路径压缩与动态连通性边界；
- [贪心算法](/discrete-math/greedy-exchange-arguments)：交换论证、活动选择与反例构造；
- [动态规划](/discrete-math/dynamic-programming-dag)：状态设计、加权活动选择与 DAG 视角；
- [Bellman–Ford](/discrete-math/bellman-ford)：负边、路径边数不变量与负环检测；
- [Floyd–Warshall](/discrete-math/floyd-warshall)：全源动态规划、负边与负环边界；
- [最短路算法选择：同图对照](/discrete-math/shortest-path-algorithm-selection)：在同一规模图上检查四种算法的前提、路径与拒绝边界；
- [最大流最小割](/discrete-math/max-flow-min-cut)：残量边、增广路与可审计的最优证书；
- [P、NP 与多项式归约](/discrete-math/p-np-reductions)：候选解验证、指数搜索与归约方向；
- [离散数学深度版路线](/discrete-math/rewrite-plan)：后续文章、项目和验收标准。

从“二分查找为什么不会漏掉答案”开始，建立证明算法的习惯。
