# 朴素贝叶斯垃圾邮件分类器

教学用途的二元贝叶斯更新轨迹、双侧置换检验、词袋多项式朴素贝叶斯、伯努利 MLE/MAP、最小批量逻辑回归与有限状态 Metropolis–Hastings。运行 `python -m unittest discover -s projects/naive_bayes_spam -p "test_*.py"`；模块分别覆盖证据归一化、交换标签下的 p 值模拟、平滑与对数域评分、似然参数估计、交叉熵梯度下降和详细平衡接受率。它们不处理真实中文分词、数据漂移或生产级校准。
