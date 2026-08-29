---
courseLevel: "1–2（核心概念与推导）"
prerequisites: "代数、向量与 Python 基础"
estimatedMinutes: 45
experiment: "实现投影与余弦相似度边界测试"
title: 向量与点积：程序如何判断两个对象是否相似
description: 从投影推导余弦相似度，并实现能处理边界输入的向量比较。
---

# 向量与点积：程序如何判断两个对象是否相似

## 学习目标

- 用点积计算一个向量在另一个方向上的分量；
- 从投影推导余弦相似度，而不只记住公式；
- 在代码中处理维度不一致和零向量，并判断何时不该使用余弦相似度。

**前置知识**：实数、平方根和求和。本文会为后续的[矩阵乘法与线性变换](/linear-algebra/matrix-multiplication)提供“向量是矩阵输入”的语言。

## 从一个计算问题开始

搜索系统把查询和文档都编码成数字向量。设查询为 $q=(3,1)$，两篇文档分别为 $a=(6,2)$、$b=(2,5)$。若只看点积，$q\cdot a=20$、$q\cdot b=11$，似乎 $a$ 更相关。

但 $a=2q$：它只是更长，方向与查询完全相同。我们想知道的是“内容方向是否一致”，而非“向量数值总量是否更大”。这正是投影和余弦相似度要解决的计算问题。

## 直觉：点积测量同向的分量

把二维向量想成从原点出发的箭头。将 $\mathbf y$ 沿 $\mathbf x$ 的方向投影，投影长度越大，$\mathbf y$ 与 $\mathbf x$ 越同向；垂直时投影长度为零；反向时它为负。

点积把这种方向关系和两个箭头的长度一起编码。它不是“逐元素相乘”本身：逐元素相乘得到向量，点积会继续求和并得到一个标量。

## 定义与符号表

| 符号 | 含义 | 类型或约束 |
| --- | --- | --- |
| $\mathbf x,\mathbf y$ | 被比较的向量 | 同属 $\mathbb R^n$ |
| $\mathbf x\cdot\mathbf y$ | 点积 | 标量 |
| $\lVert\mathbf x\rVert$ | $\mathbf x$ 的欧氏范数（长度） | 非负标量 |
| $\theta$ | 两个非零向量的夹角 | $0\le\theta\le\pi$ |

对同维向量 $\mathbf{x}=(x_1,\ldots,x_n)$ 与 $\mathbf{y}=(y_1,\ldots,y_n)$，定义

$$
\mathbf{x}\cdot\mathbf{y}=\sum_{i=1}^{n}x_i y_i,
\qquad
\lVert\mathbf{x}\rVert=\sqrt{\sum_{i=1}^{n}x_i^2}.
$$

维度必须相同；否则不存在逐项配对，也就没有这里定义的点积。

## 从投影推导余弦相似度

令 $\hat{\mathbf x}=\mathbf x/\lVert\mathbf x\rVert$ 是 $\mathbf x$ 的单位方向。$\mathbf y$ 在这个方向上的有符号投影长度是 $\hat{\mathbf x}\cdot\mathbf y$。几何上，它也等于 $\lVert\mathbf y\rVert\cos\theta$，因此

$$
\frac{\mathbf x}{\lVert\mathbf x\rVert}\cdot\mathbf y
=\lVert\mathbf y\rVert\cos\theta.
$$

两边同乘 $\lVert\mathbf x\rVert$，得到点积的几何形式：

$$
\mathbf x\cdot\mathbf y
=\lVert\mathbf x\rVert\lVert\mathbf y\rVert\cos\theta.
$$

当两个向量都非零时，除去长度便得到余弦相似度：

$$
\operatorname{cosine}(\mathbf x,\mathbf y)
=\frac{\mathbf x\cdot\mathbf y}
       {\lVert\mathbf x\rVert\lVert\mathbf y\rVert}.
$$

所以值为 $1$ 表示同向，$0$ 表示正交，$-1$ 表示反向。根据柯西—施瓦茨不等式，分子的绝对值不超过分母，结果必在 $[-1,1]$ 内；代码中的轻微越界通常来自浮点舍入。

## 手算一个完整例子

对前面的 $q=(3,1)$ 与 $a=(6,2)$：

$$
q\cdot a=3\times6+1\times2=20,
\quad \lVert q\rVert=\sqrt{10},
\quad \lVert a\rVert=\sqrt{40}=2\sqrt{10}.
$$

因此 $\operatorname{cosine}(q,a)=20/(\sqrt{10}\cdot2\sqrt{10})=1$。再计算 $b=(2,5)$：

$$
q\cdot b=11,
\quad \lVert b\rVert=\sqrt{29},
\quad \operatorname{cosine}(q,b)=\frac{11}{\sqrt{290}}\approx0.646.
$$

点积和余弦在这个例子中都让 $a$ 排在前面；区别在于，将 $a$ 再放大一百倍，余弦仍为 $1$，点积却会放大一百倍。

## 把公式实现为代码

```python
from math import sqrt


def cosine_similarity(x, y):
    """返回同维非零向量的余弦相似度。"""
    if len(x) != len(y):
        raise ValueError("vectors must have the same dimension")

    dot = sum(a * b for a, b in zip(x, y))
    norm_x = sqrt(sum(a * a for a in x))
    norm_y = sqrt(sum(b * b for b in y))
    if norm_x == 0 or norm_y == 0:
        raise ValueError("cosine similarity is undefined for a zero vector")

    # 防止浮点舍入把 1.0 变成 1.0000000000000002。
    return max(-1.0, min(1.0, dot / (norm_x * norm_y)))


assert cosine_similarity([3, 1], [6, 2]) == 1.0
assert cosine_similarity([1, 0], [0, 1]) == 0.0
```

三次求和各扫描一次向量，时间复杂度为 $O(n)$，额外空间为 $O(1)$。真实的检索系统会把文档向量预先归一化，此时查询一次只需点积；大批量计算应交给 NumPy、PyTorch 或 BLAS，而非 Python 循环。

## 正确性说明

`dot` 正是定义中的 $\sum_i x_i y_i$；两个 `norm` 分别实现 $\sqrt{\sum_i x_i^2}$ 与 $\sqrt{\sum_i y_i^2}$。在非零且同维的前提下，函数返回二者之比，因而与上节推导的余弦相似度相等。维度检查和零向量检查分别排除了定义不成立与分母为零的情况。

## 失败案例与工程边界

余弦相似度故意忽略长度，因此不适合“大小本身就是信号”的任务。例如预算向量 $(100,0)$ 和 $(1,0)$ 的余弦相似度为 $1$，但两者金额相差极大；这时欧氏距离、相对误差或业务阈值更合适。

零向量没有方向，不能被赋予余弦相似度。产品代码必须事先规定策略：拒绝该输入、跳过该样本，或将它当作“无信息”单独处理；不能悄悄返回 $0$ 并把“未定义”误当作“正交”。

## 常见误区

- **点积等于逐元素乘法**：`[1, 2] * [3, 4]` 的概念结果应先是 $(3,8)$，继续求和后才是点积 $11$。
- **相似度高就代表距离近**：余弦只比较方向；放大向量不改变它，欧氏距离却会改变。
- **余弦相似度总在 $[0,1]$**：允许负值，反向向量的结果是 $-1$。

## 练习

1. **复现**：手算 $(-1,2)\cdot(2,1)$ 和它们的余弦相似度。验收条件：点积为 $0$，余弦相似度为 $0$。
2. **变式**：为 `cosine_similarity` 编写三个测试：维度不一致、零向量和反向向量。最后一个测试应得到 `-1.0`。
3. **迁移**：将一组二维“用户行为”向量按与查询向量的余弦相似度排序，并解释为何先归一化所有候选向量可减少在线计算。
4. **开放**：构造两个方向相同但长度相差一千倍的向量，分别比较余弦相似度与欧氏距离；说明检索、异常检测和预算监控中应如何根据业务语义选择度量。

## 延伸与下一步

点积把一个向量投影到另一个方向；[矩阵乘法与线性变换](/linear-algebra/matrix-multiplication)将把这种“加权组合”扩展为同时产生多个输出方向。随后在[最小二乘](/linear-algebra/least-squares)中，投影会成为“没有精确解时怎样选择最好近似”的核心工具。
