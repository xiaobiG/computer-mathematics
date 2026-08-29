# 算法背后的离散数学

离散数学研究可数、可枚举、可证明的结构，也是算法正确性与复杂度分析的语言。深度版以“前提—不变量—终止—复杂度—反例”为共同骨架。

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
- [Dijkstra](/discrete-math/dijkstra)：非负边权为何能贪心，以及负权边为何失败；
- [BFS](/discrete-math/breadth-first-search)：队列分层不变量与无权图最短路；
- [DFS](/discrete-math/depth-first-search)：发现/完成时间、显式栈与环检测边界；
- [强连通分量](/discrete-math/strongly-connected-components)：互相可达等价类、Kosaraju 与凝聚 DAG；
- [并查集](/discrete-math/union-find)：森林不变量、路径压缩与动态连通性边界；
- [贪心算法](/discrete-math/greedy-exchange-arguments)：交换论证、活动选择与反例构造；
- [动态规划](/discrete-math/dynamic-programming-dag)：状态设计、加权活动选择与 DAG 视角；
- [Bellman–Ford](/discrete-math/bellman-ford)：负边、路径边数不变量与负环检测；
- [Floyd–Warshall](/discrete-math/floyd-warshall)：全源动态规划、负边与负环边界；
- [P、NP 与多项式归约](/discrete-math/p-np-reductions)：候选解验证、指数搜索与归约方向；
- [离散数学深度版路线](/discrete-math/rewrite-plan)：后续文章、项目和验收标准。

从“二分查找为什么不会漏掉答案”开始，建立证明算法的习惯。
