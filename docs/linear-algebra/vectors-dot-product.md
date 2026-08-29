---
title: 向量与点积：程序如何判断两个对象是否相似
description: 从方向、投影到余弦相似度，理解点积的计算意义。
---

# 向量与点积：程序如何判断两个对象是否相似

## 先问一个问题

搜索系统把两篇文章编码成数字列表后，如何判断它们是否在讨论相近主题？关键不是逐项比较，而是比较两个向量的**方向**。

## 直觉

二维向量可以看作从原点射出的箭头。两个箭头越同向，它们的点积越大；垂直时，点积为零；方向相反时，点积为负。

对 $\mathbf{x}=(x_1,\ldots,x_n)$ 与 $\mathbf{y}=(y_1,\ldots,y_n)$：

$$\mathbf{x}\cdot\mathbf{y}=\sum_{i=1}^{n}x_i y_i$$

点积还满足几何关系：

$$\mathbf{x}\cdot\mathbf{y}=\lVert\mathbf{x}\rVert\lVert\mathbf{y}\rVert\cos\theta$$

将长度除掉，就得到常用的余弦相似度：

$$\cos\theta=\frac{\mathbf{x}\cdot\mathbf{y}}{\lVert\mathbf{x}\rVert\lVert\mathbf{y}\rVert}$$

## 代码实验

```python
from math import sqrt

def cosine_similarity(x, y):
    dot = sum(a * b for a, b in zip(x, y))
    norm_x = sqrt(sum(a * a for a in x))
    norm_y = sqrt(sum(b * b for b in y))
    return dot / (norm_x * norm_y)

print(cosine_similarity([3, 1, 0], [6, 2, 0]))  # 1.0：方向相同
print(cosine_similarity([1, 0, 0], [0, 1, 0]))  # 0.0：正交
```

## 工程边界

余弦相似度只比较方向，适合文本特征等“长度未必代表语义”的场景。若大小本身很重要，例如预算、流量或像素亮度，欧氏距离往往更合适。

## 常见误区

- 点积不是逐元素相乘；逐元素乘积仍是一个向量，点积是一个标量。
- 零向量没有方向，因此不能计算余弦相似度。

## 练习

为函数加入维度不一致和零向量的检测；再比较它与欧氏距离对同一组向量的排序结果。
