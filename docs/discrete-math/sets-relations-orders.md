---
courseLevel: "0–2（离散结构预备）"
prerequisites: "命题逻辑、集合符号与 Python 基础"
estimatedMinutes: 55
experiment: "实现并验证等价关系划分与偏序上的拓扑排序"
title: 集合、关系、等价类与偏序
description: 用集合与二元关系描述程序状态，推导等价类划分、偏序和拓扑排序的共同结构。
---

# 集合、关系、等价类与偏序

> 并查集维护的不是“很多数组”，而是一个集合的划分；包依赖也不是“很多箭头”，而是一个偏序。先看清关系的性质，才能选择正确的数据结构和算法。

## 学习目标

- 使用集合、笛卡尔积与二元关系精确描述程序对象；
- 判断关系的自反、对称、反对称与传递性质；
- 从等价关系推导不相交的等价类划分；
- 区分等价关系与偏序，并理解拓扑序为何是偏序的线性扩展；
- 用小程序验证关系性质与依赖约束。

## 从“用户是否同一群组”开始

社交网络的“互相可达”关系满足：每个用户与自己可达；若 \(u\) 到 \(v\)，则 \(v\) 到 \(u\)；若 \(u\) 到 \(v\)、\(v\) 到 \(w\)，则 \(u\) 到 \(w\)。这三项使它成为等价关系。它把所有用户分成互不重叠的连通分量，正是并查集所维护的对象。

而“课程 A 是课程 B 的先修”不应对称：A 先于 B 不代表 B 先于 A。它更接近偏序；若出现两门不同课程互为先修，就有环，偏序条件被破坏。

## 定义：关系是笛卡尔积的子集

对集合 \(S\)，二元关系 \(R\) 是 \(S\times S\) 的一个子集。记 \(aRb\) 表示 \((a,b)\in R\)。

- 自反：\(\forall a\in S,aRa\)；
- 对称：\(aRb\Rightarrow bRa\)；
- 反对称：\(aRb\land bRa\Rightarrow a=b\)；
- 传递：\(aRb\land bRc\Rightarrow aRc\)。

**等价关系**满足自反、对称、传递。\(a\) 的等价类是 \([a]=\{b\in S\mid aRb\}\)。任意两个等价类要么相同，要么不相交：若 \(c\in[a]\cap[b]\)，传递性可推出 \([a]=[c]=[b]\)。因此等价关系与集合划分一一对应。

**偏序**满足自反、反对称、传递。偏序元素不必都可比较：两个独立任务既非 \(a\preceq b\)，也非 \(b\preceq a\)，这正是可以并行的空间。

## 从定义推导：为什么等价类一定是划分

这不是一个应当记住的结论，而是三个性质共同强迫出的结构。设 \(R\) 是 \(S\) 上的等价关系。

1. **覆盖全集。** 对任意 \(a\in S\)，自反性给出 \(aRa\)，所以 \(a\in[a]\)。每个元素至少属于一个等价类。
2. **相交则相等。** 假设 \(c\in[a]\cap[b]\)。则 \(aRc\) 与 \(bRc\)；由对称性得到 \(cRb\)。任取 \(x\in[a]\)，有 \(aRx\)，再由对称性得到 \(xRa\)，结合 \(aRc\) 和 \(cRb\) 可推出 \(xRb\)，故 \(x\in[b]\)。反向同理，于是 \([a]=[b]\)。
3. **因此没有部分重叠。** 两个类若有共同元素就相等，否则不相交；再结合第一步，所有等价类正好把 \(S\) 切成一个划分。

这也解释并查集的 API：`find(x)` 返回的是一个类的代表元，`union(x, y)` 只有在把两个类合并时才改变划分。它不需要保存“所有元素两两等价”的 \(O(n^2)\) 个关系对。

## 从偏序到拓扑排序

有限偏序可看成 DAG 的可达关系。拓扑排序给出一个线性序，使 \(a\prec b\) 时 \(a\) 一定出现在 \(b\) 之前；它称为偏序的线性扩展。独立元素的相对位置可以不同，所以拓扑序通常不唯一。

若依赖图有环，则存在 \(a\prec b\prec\cdots\prec a\)，违反反对称性；这解释了为什么 [拓扑排序](/discrete-math/graph-foundations-topological-sort) 能把“无输出顺序”作为环的证据。

## 从定义实现验证器

有限集合上可以把量词直接翻译成 `all`。下面的代码故意不追求大规模性能：它让每个循环都对应一条数学定义，因此既可做单元测试，也可用于发现输入关系没有满足的性质。

```python
def relation_report(items, relation):
    """检查有限集合上的 R 是否满足定义；集合外端点是输入错误。"""
    if any(left not in items or right not in items for left, right in relation):
        raise ValueError("relation contains an item outside the domain")

    reflexive = all((item, item) in relation for item in items)
    symmetric = all((right, left) in relation for left, right in relation)
    antisymmetric = all(
        left == right or (right, left) not in relation
        for left, right in relation
    )
    transitive = all(
        (left, last) in relation
        for left in items for middle in items for last in items
        if (left, middle) in relation and (middle, last) in relation
    )
    return {
        "reflexive": reflexive,
        "symmetric": symmetric,
        "antisymmetric": antisymmetric,
        "transitive": transitive,
        "equivalence": reflexive and symmetric and transitive,
        "partial_order": reflexive and antisymmetric and transitive,
    }


def equivalence_classes(items, relation):
    if not relation_report(items, relation)["equivalence"]:
        raise ValueError("equivalence_classes requires an equivalence relation")
    unseen, result = set(items), []
    while unseen:
        representative = next(iter(unseen))
        current = {item for item in items if (representative, item) in relation}
        result.append(current)
        unseen -= current
    return result


items = {1, 2, 3, 4, 5, 6}
same_parity = {(a, b) for a in items for b in items if a % 2 == b % 2}
assert relation_report(items, same_parity)["equivalence"]
assert {frozenset(group) for group in equivalence_classes(items, same_parity)} == {
    frozenset({1, 3, 5}), frozenset({2, 4, 6}),
}

# “相差不超过 1”有自反性和对称性，却缺少传递性。
near = {(a, b) for a in {0, 1, 2} for b in {0, 1, 2} if abs(a - b) <= 1}
assert not relation_report({0, 1, 2}, near)["transitive"]
```

`relation_report` 分别返回自反、对称、反对称、传递、等价和偏序六项证据；其中三重循环就是传递性量词的逐项检查，时间为 \(O(|S|^3)\)，空间除输入外为 \(O(1)\)。`equivalence_classes` 依次选择一个尚未分类的代表元；等价关系保证所得类彼此不重叠，所以每个元素只会被移出 `unseen` 一次。运行 `python -m unittest projects.algorithm_lab.test_relations` 可再验证奇偶关系、\(\le\) 和非法域元素。真实的“同组”关系常由图连通性或 DSU 增量维护，而不显式存储所有有序对。

## 正确性：代码为何得到真正的等价类

`relation_report` 的每个布尔值都是定义的有限域全称量词：例如 `reflexive` 遍历每个 `item`，只有全部 \((item,item)\) 都在 `relation` 中才为真；传递性同理遍历全部三元组。因此它返回 `equivalence=True` 当且仅当输入关系满足三项定义。

对 `equivalence_classes`，循环不变量是：`result` 中的集合两两不交，且它们的并集恰为原始 `items - unseen`。初始时显然成立。每次选择代表元得到完整的 \([a]\)，由上节“相交则相等”的结论，它不会与已有类部分重叠；移除后不变量仍成立。`unseen` 严格变小，循环终止时为空，于是 `result` 是全集的划分。

## 常见误区与边界

- **反对称不是“不对称”。** \(\le\) 既允许 \(a\le a\)，也允许不同元素单向比较；它只禁止不同元素双向比较。
- **传递闭包不等于原始边。** 依赖图可只保存直接依赖，关系语义通常包含所有可达路径。
- **相等关系不是唯一等价关系。** “同余”“同一连通分量”“相同哈希桶”（在定义合适时）都可能形成等价类。
- **偏序不是总序。** 强行给独立任务排序会引入实现细节，不是数学依赖。
- **关系由数据推断时要注意误差。** “相似度超过阈值”常不传递，不能直接当等价关系用于分组。

## 练习

1. 判断“整数相差不超过 1”是否为等价关系，给出违反性质的最小反例。
2. 证明等价类形成集合划分。
3. 写函数检查有限关系是否为偏序，并对课程先修关系测试一个环。
4. 用并查集维护动态加边图的等价类，说明删除边为何困难。
5. 对一个带独立任务的 DAG 找出两个不同拓扑序，解释两者为何都合法。

## 练习答案提示

1. 它自反、对称，却不传递：$0\sim1$ 且 $1\sim2$，但 $0\not\sim2$；这已构成最小的传递性反例。
2. 用自反性说明每个元素属于某个等价类；若两个等价类相交，取交点并用对称性、传递性证明它们相等，故各类不相交且并集为全集。
3. 对有限集合枚举所有元素对：检查自反、反对称、传递；若先修图出现环，传递性虽可成立但它不再能代表无环依赖，拓扑排序也会失败。
4. 并查集的 `union` 只合并集合，无法知道哪一条历史边是连接的唯一原因；删除一条边可能要求重新计算整块连通分量，需用动态连通性结构或重建。
5. 任选两个互不依赖的顶点交换次序；验证每条边的起点都仍出现在终点之前。不同线性扩展对应同一偏序，并不改变依赖语义。

## 下一步

将等价类连接到[并查集](/discrete-math/union-find)，将偏序连接到[图、树、二分图与拓扑排序](/discrete-math/graph-foundations-topological-sort)。这两条线分别处理“哪些对象可合并”和“哪些任务必须先后”。
