# 朴素贝叶斯垃圾邮件分类器

教学用途的词袋多项式朴素贝叶斯与最小批量逻辑回归。运行 `python -m unittest discover -s projects/naive_bayes_spam -p "test_*.py"`；前者使用拉普拉斯平滑和对数域评分，后者从伯努利似然推导交叉熵与梯度下降。它们不处理真实中文分词、数据漂移或生产级校准。
