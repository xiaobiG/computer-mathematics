# 朴素贝叶斯垃圾邮件分类器

教学用途的词袋多项式朴素贝叶斯、最小批量逻辑回归与有限状态 Metropolis–Hastings。运行 `python -m unittest discover -s projects/naive_bayes_spam -p "test_*.py"`；前者使用拉普拉斯平滑和对数域评分，后者从伯努利似然推导交叉熵与梯度下降，MCMC 模块从详细平衡推导接受率。它们不处理真实中文分词、数据漂移或生产级校准。
