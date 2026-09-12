---
title: 子群体性能：先检查样本量，再解释指标
description: 用最小样本量边界和可重放证书审计子群体性能，避免把少量观测的波动写成群体结论。
courseLevel: "3（分层评估与不确定性边界）"
prerequisites: "带标签窗口性能审计、Wilson 区间、抽样误差"
estimatedMinutes: 50
experiment: "按组报告带标签窗口指标，并在样本不足时拒绝组级结论"
---

# 子群体性能：先检查样本量，再解释指标

## 学习目标

你将能把带标签窗口按预先定义的组拆分，先报告组样本数，再决定是否展示指标；理解样本不足为何应拒绝结论；并用证书防止把小群体伪装为充分样本。

## 指标公式与样本量推导

总体准确率可能掩盖局部风险，但按组切分也会减少每组样本。对组 $g$，只有 $n_g\ge m$ 时才报告其混淆矩阵、准确率、Wilson 区间、Brier 与对数损失；当 $n_g<m$，输出 `insufficient_sample_for_group_conclusion`。

$$
\hat a_g=\frac{1}{n_g}\sum_{i:g_i=g}\mathbb{1}[\hat y_i=y_i].
$$

阈值 $m$ 是审计政策，不是普适科学常数。它应该结合窗口长度、错误成本、标签质量和隐私风险制定，并被报告与证书绑定。

## 可运行实验

```python
report = subgroup_report(window, groups, 20)
for row in report["subgroups"]:
    print(row["group"], row["count"], row["sufficient_sample"])
assert subgroup_certificate(window, groups, report)
```

运行：

```bash
python -m unittest \
  projects.naive_bayes_spam.test_subgroup_monitoring
```

完整反例在 [`test_subgroup_monitoring.py`](https://github.com/xiaobiG/computer-mathematics/blob/main/projects/naive_bayes_spam/test_subgroup_monitoring.py)。证书会拒绝将不足样本的小组改写为“样本充足”。

## 边界与误区

- 小组没有指标不代表“没有风险”，而是证据不足；应收集更多高质量标签或合并有业务依据的窗口。
- 指标差异不是群体属性的因果解释；可能来自样本、采集、标注或条件分布差异。
- 不应使用未经治理的敏感属性，也不应自动改变模型、门槛或服务。
- 同时报告组大小、窗口口径与不确定性；禁止只挑选差异最大的组。

## 练习

1. 为什么子群体报告必须先输出样本数？
2. 构造总准确率稳定而一个充分样本子群体退化的例子。
3. 说明最低样本量为何也要绑定进证书。
4. 写出一个不应由该报告自动执行的行动。

## 练习答案提示

1. 指标精度取决于分母，忽略它会夸大随机波动。
2. 让大组稳定、小组错误增加，再比较总体加权平均与组内指标。
3. 改变门槛会改变哪些组可以被解释，属于结论的一部分。
4. 自动重训、调整阈值、停用某群体服务都需要额外治理与人工审批。

## 延伸

[带标签窗口性能审计](/probability-ml/labeled-window-performance-degradation)给出总体窗口口径；[联合证据](/probability-ml/joint-input-label-evidence)并列输入和结果信号。分层报告应始终服务于审计与复核，而不是群体排名。
