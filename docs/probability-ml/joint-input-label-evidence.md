---
title: 联合证据：输入漂移与带标签性能如何一起审计
description: 将同一观测窗口的输入类别变化与延迟标签性能并列报告，避免把同时出现的信号误解为因果关系。
courseLevel: "3（监控证据、延迟标签与工程边界）"
prerequisites: "数据漂移监控、带标签窗口性能审计、概率校准"
estimatedMinutes: 55
experiment: "以同一窗口的类别、概率和标签生成联合证据报告与重放证书"
---

# 联合证据：输入漂移与带标签性能如何一起审计

## 学习目标

你将学会把输入类别变化与标签到达后的性能变化保存在同一份报告中；区分“两个信号同时出现”与“一个信号造成另一个”；用输入合同防止拼接无关窗口；并把结果限制为人工复核。

## 从一个计算问题开始

`invoice` 类别本周明显增多，同时延迟标签显示对数损失升高。两件事发生在同一时间并不证明新类别导致了性能退化：标注规范、采集管道或未记录的群体变化也可能改变结果。可靠报告应保留两类证据，却拒绝编造解释。

## 同一窗口的合同

每个快照包含 `categories` 和一个带 `probabilities`、`labels` 的带标签窗口；两者长度必须相等。于是第 $i$ 个类别、预测和标签描述同一观测。参考与当前快照各自可以有不同样本量，但不能把本月类别频率与另一批邮件的标签随意拼接。

联合报告复用 PSI/总变差作为输入证据，复用准确率、Wilson 区间、Brier 与对数损失作为结果证据。它输出：

$$
S_{input},\quad S_{outcome},\quad S=S_{input}\lor S_{outcome}.
$$

这里 $S$ 仅代表“需要复核”。即便 $S_{input}=S_{outcome}=1$，报告仍固定写入 `causal_interpretation: "not_established"` 与 `automatic_action: "none"`。

## 可运行实验与证书

```python
report = joint_evidence_report(reference, current)
assert report["causal_interpretation"] == "not_established"
assert report["policy"]["automatic_action"] == "none"
assert joint_evidence_certificate(reference, current, report)
```

完整样例与三种反例见 [`test_joint_evidence_monitoring.py`](https://github.com/xiaobiG/computer-mathematics/blob/main/projects/naive_bayes_spam/test_joint_evidence_monitoring.py)。运行：

```bash
python -m unittest \
  projects.naive_bayes_spam.test_joint_evidence_monitoring
```

证书会拒绝被改成“输入漂移造成损失”的报告，也会拒绝类别数与带标签窗口长度不等的快照。

## 正确性、反例与边界

- **只有输入信号**：新来源使 PSI 升高，而保留标签上的性能稳定；应检查来源和覆盖，不能宣布模型失效。
- **只有结果信号**：输入类别频率近似不变，但对数损失升高；可能是概念、标签或数据管道变化，不能用 PSI 的低值排除风险。
- **两个信号同时出现**：值得优先复核，却仍不是因果结论。
- **小样本窗口**：Wilson 区间展示准确率估计不确定性；它不替代时间切分、标注质量与群体审计。

## 常见误区

- **“同一窗口就能证明因果。”** 同一窗口只减少了错误拼接证据的风险。
- **“联合信号必须自动重训。”** 报告明确禁止这种自动行动。
- **“没有 PSI 信号就没有性能风险。”** $P(Y\mid X)$ 可在 $P(X)$ 稳定时变化。
- **“PSI 和损失可相加为一个通用风险分。”** 它们量纲、阈值与业务含义不同，应并列解释。

## 练习

1. 解释为什么合同要检查 `categories` 与标签数组等长。
2. 构造一个 PSI 高、准确率不变的窗口，并写出合理复核问题。
3. 说明为何 `causal_interpretation` 也必须被证书绑定。
4. 为延迟一周的标签设计人工复核清单。

## 练习答案提示

1. 否则输入证据和结果证据不再来自同一批观测。
2. 增加合法新来源类别；检查数据采集和群体覆盖，而不是直接改模型。
3. 否则可在指标不变时篡改叙述，造成比数值篡改更隐蔽的错误决策。
4. 记录时间范围、数据/标注版本、输入来源、群体覆盖、损失变化与审批结论。

## 延伸

[数据漂移监控](/probability-ml/data-drift-monitoring)解释无标签时的输入证据；[带标签窗口性能审计](/probability-ml/labeled-window-performance-degradation)解释标签到达后的结果证据。下一阶段应研究分层子群体的样本量与不确定性，而不增加自动化行动。
