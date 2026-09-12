"""最小文本相似度检索器：词频向量 + 余弦相似度。"""

from __future__ import annotations

from collections import Counter
from math import sqrt
from re import findall
from typing import Iterable

Vector = Counter[str]


def tokenize(text: str) -> list[str]:
    """保留英文词和单个中文字符；用于教学示例而非生产分词。"""
    return [token.lower() for token in findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]", text)]


def vectorize(text: str) -> Vector:
    return Counter(tokenize(text))


def cosine_similarity(left: Vector, right: Vector) -> float:
    """返回两个稀疏词频向量的余弦相似度；零向量返回 0。"""
    dot = sum(count * right[token] for token, count in left.items())
    left_norm = sqrt(sum(count * count for count in left.values()))
    right_norm = sqrt(sum(count * count for count in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def rank_documents(query: str, documents: Iterable[str]) -> list[tuple[int, float]]:
    """按相似度降序排列；相同分数时维持输入顺序。"""
    query_vector = vectorize(query)
    scores = [
        (index, cosine_similarity(query_vector, vectorize(document)))
        for index, document in enumerate(documents)
    ]
    return sorted(scores, key=lambda item: item[1], reverse=True)


if __name__ == "__main__":
    docs = [
        "矩阵乘法描述线性变换的组合。",
        "图搜索可以找到最短路径。",
        "向量点积与余弦相似度用于文本检索。",
    ]
    for index, score in rank_documents("矩阵 向量 相似度", docs):
        print(f"文档 {index}: {score:.3f} — {docs[index]}")
