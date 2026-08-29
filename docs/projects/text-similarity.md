---
title: 项目：最小文本相似度检索器
description: 用词频向量和余弦相似度构建一个可测试的文档排序工具。
---

# 项目：最小文本相似度检索器

## 目标

给定查询文本和一组文档，按余弦相似度从高到低返回文档。项目不依赖第三方库，重点是让“分词 → 向量 → 点积 → 归一化 → 排序”的每一步都可见。

## 数学连接

- [向量与点积](/linear-algebra/vectors-dot-product)：相似度的分子；
- [矩阵乘法](/linear-algebra/matrix-multiplication)：批量检索的自然延伸；
- [期望与方差](/probability-ml/expectation-variance)：词频统计的基础。

余弦相似度为：

$$\operatorname{sim}(q,d)=\frac{q\cdot d}{\lVert q\rVert\lVert d\rVert}$$

## 运行

```bash
python projects/text_similarity/main.py
python -m unittest projects.text_similarity.test_main
```

示例将搜索“矩阵 向量 相似度”，并输出每个文档的分数。

## 可观察的实验

1. 增加一个词更多、但主题相同的文档，比较点积与余弦相似度；
2. 将查询替换为未出现的词，确认零向量的安全处理；
3. 实现 TF-IDF，观察常见词的权重为何会降低。

## 工程边界

这个项目将中文拆为单个字符、英文拆为词，不处理真实中文分词、停用词、词形归一化或语义嵌入。真实搜索系统需使用更成熟的分词与索引方案。
