---
title: 子群体性能：先检查样本量，再解释指标
description: 用最小样本量边界和可重放证书审计子群体性能，避免把少量观测的波动写成群体结论。
courseLevel: "3（分层评估与不确定性边界）"
prerequisites: "带标签窗口性能审计、Wilson 区间、抽样误差"
estimatedMinutes: 65
experiment: "冻结声明的组宇宙，报告零样本组，并在样本不足时拒绝组级结论"
---

# 子群体性能：先检查样本量，再解释指标

## 学习目标

你将能把带标签窗口按预先定义的组拆分，先报告每个已声明组的样本数（包括零样本组），再决定是否展示指标；理解样本不足与事后选组为何都应拒绝结论；并用证书防止把小群体或已声明但未出现的群体从报告中静默抹去。

## 指标公式与样本量推导

总体准确率可能掩盖局部风险，但按组切分也会减少每组样本。对预先声明的组宇宙 $G$ 中每个组 $g$，只有 $n_g\ge m$ 时才报告其混淆矩阵、准确率、Wilson 区间、Brier 与对数损失；当 $n_g<m$，输出 `insufficient_sample_for_group_conclusion`。

$$
\hat a_g=\frac{1}{n_g}\sum_{i:g_i=g}\mathbb{1}[\hat y_i=y_i].
$$

阈值 $m$ 是审计政策，不是普适科学常数。它应该结合窗口长度、错误成本、标签质量和隐私风险制定，并与已声明组宇宙一起被报告与证书绑定。

## 为什么“当前出现过的组”不能代替预先声明

假定审计设计阶段声明了 $G=\{\text{A},\text{B},\text{C}\}$，但本窗口只收到了 A、B 的标签。若程序从观测到的标签生成组列表，C 会完全消失；读者既看不到 $n_C=0$，也无法分辨它是未被覆盖、数据管道遗漏，还是事后被排除。正确报告应保留 C，并把它标为证据不足。

这不是要求所有群体标签都必然收集，也不是允许任意敏感属性进入系统。`declared_groups` 是经过治理、固定在查看结果**之前**的审计维度；每个实际观测的组必须属于它。新增观测组或删除声明组都会改变报告合同，而不该在结果出来后静默发生。

## 可运行实验

```python
from projects.naive_bayes_spam.subgroup_monitoring import (
    subgroup_certificate,
    subgroup_report,
)

declared_groups = ["A", "B", "C"]  # C 在这次窗口可以是零样本
report = subgroup_report(window, groups, 20, declared_groups)
for row in report["subgroups"]:
    print(row["group"], row["count"], row["sufficient_sample"])
assert subgroup_certificate(window, groups, report)
```

运行：

```bash
python -m unittest \
  projects.naive_bayes_spam.test_subgroup_monitoring
```

输出按 `declared_groups` 的顺序包含三行；即使 C 没有一条观测，也会得到 `count=0`、`metrics=None` 和 `insufficient_sample_for_group_conclusion`。完整反例在 [`test_subgroup_monitoring.py`](https://github.com/xiaobiG/computer-mathematics/blob/main/projects/naive_bayes_spam/test_subgroup_monitoring.py)。证书会拒绝将不足样本的小组改写为“样本充足”，也会拒绝更改声明的组宇宙。

算法先验证所有观测组属于 $G$，随后对 $G$ 中的每个成员建立索引并执行最低样本量检查。令窗口大小为 $n$、声明组数为 $|G|$，索引与指标合计为 $O(n)$，输出至少需要 $O(|G|)$；空间除报告外为 $O(n+|G|)$。这不是许可去枚举大量候选组：$G$ 的冻结时点与治理理由本身也是实验前提。

## 边界与误区

- 小组没有指标不代表“没有风险”，而是证据不足；应收集更多高质量标签或合并有业务依据的窗口。
- 当前窗口没出现某组不代表该组不在审计范围；零样本应显式保留，供检查覆盖、采样与标签流程。
- 结果出来后再添加、删除或合并组会改变比较次数和选择偏差；应建立新版本的审计设计，而不是改写旧报告。
- 指标差异不是群体属性的因果解释；可能来自样本、采集、标注或条件分布差异。
- 不应使用未经治理的敏感属性，也不应自动改变模型、门槛或服务。
- 同时报告组大小、窗口口径与不确定性；禁止只挑选差异最大的组。

## 练习

1. 为什么子群体报告必须先输出样本数？
2. 为什么已声明但零样本的组仍要出现在报告中？
3. 构造总准确率稳定而一个充分样本子群体退化的例子。
4. 说明最低样本量与声明组宇宙为何都要绑定进证书。
5. 写出一个不应由该报告自动执行的行动。

## 练习答案提示

1. 指标精度取决于分母，忽略它会夸大随机波动。
2. 它可能暴露覆盖或标签流程缺口；若不报告，读者无法区分“没有观察到”与“没有纳入审计”。
3. 让大组稳定、小组错误增加，再比较总体加权平均与组内指标。
4. 改变门槛会改变哪些组可以被解释；改变组宇宙还会改变哪些比较被看见，二者都属于结论的一部分。
5. 自动重训、调整阈值、停用某群体服务都需要额外治理与人工审批。

## 延伸

[带标签窗口性能审计](/probability-ml/labeled-window-performance-degradation)给出总体窗口口径；[联合证据](/probability-ml/joint-input-label-evidence)并列输入和结果信号。分层报告应始终服务于审计与复核，而不是群体排名。
