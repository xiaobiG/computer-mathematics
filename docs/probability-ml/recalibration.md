---
title: 概率再校准：验证集把分数变回概率
description: 从 logistic 校准推导 Platt scaling，严格区分训练、验证与测试集，并用可复跑实验审计概率损失。
courseLevel: "3（概率模型评估与工程验证）"
prerequisites: "条件概率、sigmoid、交叉熵、概率校准与可靠性曲线"
estimatedMinutes: 60
experiment: "在独立验证集拟合 Platt scaling，并对保留数据比较 Brier 与对数损失"
---

# 概率再校准：验证集把分数变回概率

## 学习目标

读完后，你能说明为什么“分类排序正确”不等于“概率可信”；从 logistic 函数推导 Platt scaling；严格区分训练、验证和测试集；在验证集拟合再校准器并在保留集上报告 Brier 分数与对数损失；并识别把最终测试集用于调参造成的数据泄漏。

## 从一个计算问题开始

垃圾过滤模型为 100 封邮件都报出 $0.90$ 的垃圾概率，其中只有约 75 封实际是垃圾。若排序任务只关心“垃圾邮件排在正常邮件前面”，模型可能仍然有用；但自动隔离、风险定价或人工审核容量规划需要的是兑现承诺的概率，而不是过度自信的分数。

我们不应在最终测试集上把 $0.90$ 调成 $0.75$：那会把答案偷看进模型。正确流程是：分类器在训练集学习，校准器只在验证集拟合，最后一次才在从未参与选择的测试集报告结果。

## 从分数到再校准函数

设原模型输出 $p\in[0,1]$。先取稳定的对数赔率

$$x=\operatorname{logit}(p)=\log\frac{p}{1-p}.$$

Platt scaling 用验证集拟合两个参数 $a,b$：

$$q=\sigma(ax+b),\qquad \sigma(t)=\frac{1}{1+e^{-t}}.$$

然后最小化验证集的二元负对数似然（可加一个很小的 $L_2$ 正则）：

$$
L(a,b)=-\frac1n\sum_{i=1}^n\left[y_i\log q_i+(1-y_i)\log(1-q_i)\right]+\frac\lambda2a^2.
$$

由 $\frac{d\sigma(t)}{dt}=\sigma(t)(1-\sigma(t))$ 可得

$$
\frac{\partial L}{\partial a}=\frac1n\sum_i(q_i-y_i)x_i+\lambda a,
\qquad
\frac{\partial L}{\partial b}=\frac1n\sum_i(q_i-y_i).
$$

因此可用全批量梯度下降更新 $a,b$。若 $a>0$，它保持原分数的排序；若验证数据提示相反排序，得到负斜率不是“修复成功”的信号，而是应该审计模型、标签和切分。

## 可运行实验：只在验证集拟合

项目中的 `PlattCalibrator` 接收分数和标签，不接收分类器对象，目的是让数据切分不能被隐藏：

```python
from projects.naive_bayes_spam.recalibration import PlattCalibrator, brier_score, log_loss

validation_scores = [0.9] * 8 + [0.1] * 8
validation_labels = [True, True, True, True, True, True, False, False] + [True, True, False, False, False, False, False, False]

calibrator = PlattCalibrator(learning_rate=0.2, max_steps=1000)
calibrator.fit(validation_scores, validation_labels)

# 真实项目中，这一批必须是从未参与 fit 的最终测试集。
test_scores = [0.9, 0.1, 0.9, 0.1]
test_labels = [True, False, False, False]
calibrated = calibrator.predict_proba(test_scores)
print(brier_score(test_scores, test_labels), brier_score(calibrated, test_labels))
print(log_loss(test_scores, test_labels), log_loss(calibrated, test_labels))
```

运行：

```bash
python -m unittest projects.naive_bayes_spam.test_recalibration
```

实现对每个候选梯度步执行回溯：只有正则化验证目标不增加时才接受该步。`objective_trace` 因而成为可检查的优化轨迹；它证明的是这个小实现遵循了自己的下降契约，不证明任何新数据也会变好。端点 $p=0,1$ 会在取 logit 前裁剪到极小开区间；这防止无穷值，但也提醒我们绝对概率本身往往已是危险的建模信号。

## 如何报告，而不是挑结果

| 数据分区 | 允许做什么 | 不允许做什么 |
| --- | --- | --- |
| 训练集 | 拟合原分类器和特征处理 | 宣称泛化表现 |
| 验证集 | 选择校准方式、正则和停止参数 | 反复用作最终成功证据 |
| 测试集 | 一次性报告 Brier、对数损失和可靠性分箱 | 依据结果再改 $a,b$、分箱或阈值 |

Brier 分数关注平方概率误差；对数损失对“极度自信但错误”的预测惩罚更强。二者下降仍不能证明公平性、因果正确性或面对分布变化后的可靠性。应结合[可靠性曲线](/probability-ml/calibration-reliability)报告每箱样本量和 Wilson 区间。

## 正确性、边界与反例

代码拒绝空数据、长度不等、非 $[0,1]$ 分数、单一类别验证集和未拟合预测。单一类别时，校准器可以把所有输出推向该类别，却无法学到有意义的概率映射；应扩大或重新设计验证样本。

反例是：验证集上所有 $0.9$ 分数恰好都是正例，但线上新来源中它们只有一半为正例。校准器会因验证集偶然而继续维持高置信度；它没有检测到分布改变，也不能替代后续的漂移监控。再校准是受限的后处理，不是安全认证。

## 常见误区

- **“校准后准确率必须提高。”** 不一定；单调映射常不改变排序或阈值类别，改善的是概率语义。
- **“验证损失下降就证明测试集也下降。”** 错；验证集用于选择，最终结论必须来自保留测试集。
- **“只要输出在 0 到 1 就是概率。”** 错；范围合法不代表频率承诺兑现。
- **“把测试集再校准一次更公平。”** 错；这会泄漏测试标签，并使报告过于乐观。

## 练习

1. **基础题**：计算 $p=0.8$ 的 logit，并写出 $a=1,b=0$ 时再校准后为何仍为 $0.8$。
2. **推导题**：从二元负对数似然推导 $\partial L/\partial b$。
3. **编码题**：为 `PlattCalibrator` 增加一个只读报告，列出拟合前后验证集的 Brier 与对数损失；不得让报告重新拟合参数。
4. **开放题**：为时间变化的垃圾邮件流设计训练、验证和测试的时间切分，并说明什么观测会触发人工审计而非自动上线校准器。

## 练习答案提示

1. $\operatorname{logit}(0.8)=\log4$；代入 $\sigma(\operatorname{logit}(p))$ 即回到 $p$。
2. 令 $t_i=ax_i+b$，使用链式法则；每项对 $b$ 的导数为 $q_i-y_i$，最后取均值。
3. 复用 `brier_score` 与 `log_loss`，只接受已经拟合的对象和显式传入的评估数组；测试报告调用前后 `slope`、`intercept` 不变。
4. 按到达时间切分，不能随机打乱未来样本；监控分箱偏差、对数损失、类别比例和词汇分布，异常时先检查标注、来源和业务风险。

## 延伸

[概率校准与可靠性曲线](/probability-ml/calibration-reliability)说明如何审计概率承诺；[交叉熵与 KL 散度](/probability-ml/cross-entropy-kl)解释对数损失的来源；下一步将研究数据漂移如何让一个在验证集上合格的校准器失效。
