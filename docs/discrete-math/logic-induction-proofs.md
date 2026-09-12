---
title: 命题逻辑、量词与归纳法：算法证明的最小语言
description: 从程序规格推导蕴含、量词、反证与数学归纳法，学习用反例和不变量验证算法结论。
courseLevel: "0–2（预备知识与证明）"
prerequisites: "集合、函数与基础编程"
estimatedMinutes: 55
experiment: "为循环规格编写断言，并用小规模穷举寻找反例"
---

# 命题逻辑、量词与归纳法：算法证明的最小语言

## 学习目标

读完后，你能将程序需求写成带量词的规格；区分必要、充分与等价；用反例推翻全称命题；用数学归纳法证明循环/递归性质；并避免把测试通过误当成普遍证明。

## 从“这个算法应该对”开始

排序函数的需求不是“示例输出有序”，而是：对**任意**输入数组，输出有序，且与输入含相同元素。`for some` 和 `for all` 的差异决定了一个例子能否支持结论。算法证明的第一步是把模糊直觉写成可判定的命题。

## 命题、蕴含与反例

命题 $P\Rightarrow Q$ 只在 $P$ 真而 $Q$ 假时为假；推翻它只需一个满足 $P$ 而不满足 $Q$ 的反例。

“$P$ 是 $Q$ 的充分条件”表示 $P\Rightarrow Q$；“$P$ 是 $Q$ 的必要条件”表示 $Q\Rightarrow P$。例如“数组已排序”是二分查找正确性的必要前提，不是它能返回某个索引的充分条件（目标仍可能不存在）。

逆否命题与原命题等价；逆命题通常不等价，必须另证或找反例。

## 量词的直觉与定义：规格的范围

$$\forall x\in D,\;P(x)$$

表示对域 $D$ 的每个 $x$ 都成立；一个反例即可推翻。$\exists x\in D,P(x)$ 表示存在一个见证；给出一个具体 $x$ 即可证明。

“数组有序”可写为 $\forall i<j, a_i\le a_j$；“存在重复元素”可写为 $\exists i\ne j,a_i=a_j$。量词否定会翻转：

$$\neg(\forall x\,P(x))\equiv\exists x\,\neg P(x),\qquad
\neg(\exists x\,P(x))\equiv\forall x\,\neg P(x).$$

随机测试寻找全称断言的反例，不能单独证明没有反例。

## 归纳法与循环不变量

要证明命题 $P(n)$ 对所有 $n\ge0$ 成立：

1. **基例**：证明 $P(0)$；
2. **归纳假设**：假设 $P(k)$ 成立；
3. **归纳步**：利用假设推出 $P(k+1)$。

循环不变量是程序版本的归纳命题：初始化对应基例；每轮保持对应归纳步；循环终止条件加不变量共同推出后置条件。例如求和循环在处理前 $k$ 个元素后保持 `total == sum(values[:k])`。它不是注释，而是证明中间状态的精确声明。

## 可运行验证：有限穷举能做什么，不能做什么

```python
from projects.algorithm_lab.counterexample_search import (
    bounded_binary_search_counterexample,
    bounded_binary_search_counterexample_certificate,
)

stalled = bounded_binary_search_counterexample("nonprogress_left", max_length=2, max_value=2)
assert stalled["values"] == [0] and stalled["target"] == 1
assert stalled["failure"] == "interval_did_not_strictly_shrink"
assert bounded_binary_search_counterexample_certificate(
    "nonprogress_left", max_length=2, max_value=2, report=stalled,
)

lost = bounded_binary_search_counterexample("drops_left_boundary", max_length=2, max_value=2)
assert lost["values"] == [0, 1] and lost["target"] == 0
assert lost["failure"] == "present_target_lost"
```

运行 `python -m unittest projects.algorithm_lab.test_counterexample_search`。`left=mid` 在 `[0]` 中寻找 `1` 时不缩小区间；`right=mid-1` 会从 `[0,1]` 丢失 `0`。证书重枚举有限域并绑定见证与轨迹。穷举可推翻全称主张，却不能外推到任意长度；一般正确性仍需初始化、保持与终止证明。

## 反证法与终止性

反证法假设结论不成立并推出矛盾。终止性常用严格下降且有下界的度量，例如二分查找区间长度 $r-l$；不变量保持不代表程序会停。

## 失败案例与工程边界

- **空域陷阱**：`forall x in empty_set, P(x)` 在逻辑上为真；代码中仍须明确空输入是否符合业务规格。
- **量词顺序**：$\forall x\exists y$ 与 $\exists y\forall x$ 完全不同。一个固定缓存大小能服务所有输入，与每个输入都有某个缓存大小不是同一承诺。
- **隐含前提**：除法证明忘记分母非零、数组访问忘记索引范围，会让推导形式正确但规格不完整。
- **浮点谓词**：实数上的等号推理未必适用于浮点比较；需要容差和数值误差模型。

## 常见误区

1. “测了很多例子就证明了算法。”错误：测试只能增加信心或发现反例。
2. “逆命题当然成立。”错误：蕴含只有逆否等价。
3. “不变量就是循环结束后的条件。”错误：不变量必须每轮开始/结束都成立；后置条件还需终止条件。
4. “归纳假设可以假设所有想要的结论。”错误：只能假设已明确的较小规模命题，并在归纳步真实使用它。

## 练习

1. **基础题**：写出“每个非空数组都有最大元素”的量词形式，并说明需要的域与顺序前提。
2. **推导题**：用归纳法证明 $1+2+\cdots+n=n(n+1)/2$。
3. **编码题**：为二分查找写出包含候选解的区间不变量，并用穷举小数组寻找一个故意错误更新规则的反例。
4. **开放题**：为一个带重试的网络客户端定义安全性、活性和终止性规格；说明哪些需要概率或时间模型。

## 练习答案提示

1. 用“对每个非空数组，存在一个数组中的元素，使得所有数组元素不大于它”的量词骨架；最大元素不必唯一，量词顺序不能交换。
2. 先验证 $n=1$，再把前 $n+1$ 项拆为前 $n$ 项加 $n+1$；代入归纳假设后提取 $(n+1)$。
3. 不变量应表述为“若目标存在，则它仍位于 `[left, right)`”；枚举短的已排序数组与所有目标值，记录第一次违反该命题的更新路径。
4. 安全性可写成“不重复提交/不越权”，活性可写成“网络恢复后最终得到响应”；有限重试需要终止度量，无限重试还要引入公平性、时钟或失败概率假设。

## 延伸

下一篇可进入[循环不变量与二分查找](/discrete-math/loop-invariants)，将归纳模板用于真实算法。再学习[递推关系](/discrete-math/recurrences)，把“规模减小”同时用于正确性和复杂度分析。
