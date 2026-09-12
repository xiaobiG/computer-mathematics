---
title: 时间块 Bootstrap：相关观测不能逐条重抽
description: 在预定义时间块的受限合同下，为校准窗口差异按完整块重采样，并说明块边界与依赖假设。
courseLevel: "3（概率监控与依赖数据边界）"
prerequisites: "冻结窗口差异的 Bootstrap、概率校准、时间序列基础"
estimatedMinutes: 55
experiment: "block-window-calibration-bootstrap/v1：固定种子下按完整时间块重采样 ECE 差"
---

# 时间块 Bootstrap：相关观测不能逐条重抽

## 学习目标

- 解释观测级 bootstrap 为何隐含可交换观测单位；
- 将相邻事件组成预定义时间块并按完整块重采样；
- 区分可重放区间、时间依赖假设与部署决策；
- 知道何时需要更长块、移动块 bootstrap 或专门时间序列模型。

## 从一个计算问题开始

邮件流量、传感器读数或模型请求常成批出现：同一分钟的事件共享上游系统、用户群或延迟状态。若把每条记录独立放回抽样，重采样样本会把一个突发块拆散，低估这种共同波动。时间块 bootstrap 先在分析前划定块，再把整块作为可重抽单位。

## 定义与推导

将冻结窗口写成按时间排序的块 $C_1,\ldots,C_B$。一次重采样抽块索引 $I_1,\ldots,I_B$，样本是

$$C_{I_1}\Vert C_{I_2}\Vert\cdots\Vert C_{I_B}.$$

块内概率、标签与顺序不被拆开，因此短程相关性仍保留在块中。参考/当前窗口各自重复这个过程，重算 ECE 差并取固定百分位端点。它假设块间近似可交换、块长足以容纳相关性；种子和区间并不能证明这两个前提。

## 可运行实验

```python
from projects.naive_bayes_spam.block_window_calibration_bootstrap import (
    block_window_calibration_bootstrap_certificate,
    block_window_calibration_bootstrap_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION

def block(probabilities, labels):
    return {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": probabilities, "labels": labels}

old = [block([.5, .5], [1, 0]), block([.5, .5], [1, 0])]
new = [block([.8, .8], [1, 0]), block([.8, .8], [1, 0])]
report = block_window_calibration_bootstrap_report("old", old, "new", new, minimum_window_size=4, repeats=20, seed=7)
assert report["bootstrap_policy"]["resampling_unit"] == "predefined_labeled_time_block"
assert report["bootstrap_policy"]["automatic_action"] == "none"
assert block_window_calibration_bootstrap_certificate("old", old, "new", new, report)
```

运行 `python -m unittest projects.naive_bayes_spam.test_block_window_calibration_bootstrap`。报告绑定块大小、重复次数、种子、分箱和区间；证书重建整份报告，篡改块大小或端点会被拒绝。

## 正确性与边界

固定输入、块边界和种子时，块索引、拼接后的观测和 ECE 差序列均可重放。该证书只证明报告遵守声明的块重采样设计，不证明块间独立、块长足够、总体差异方向或因果解释，`automatic_action` 始终为 `none`。合同要求每个窗口至少两个非空块；一个块无法表达块间抽样变化。

## 失败案例与工程边界

- **事后切块。** 把选择偏差藏进了重采样设计；边界必须预先冻结。
- **块太短。** 跨块相关仍被切断，区间可能过窄。
- **块太长。** 有效块数很小，更多 repeats 无法弥补信息不足。
- **用户簇而非时间相关。** 应按用户/设备簇重采样。
- **非平稳趋势。** 块间可交换不合理时，应建模趋势、季节性或使用专门时间序列方法。

## 常见误区

- “按块抽样就解决时间依赖。”不对，它只保留已划定块内结构。
- “更多 repeats 能修复错误块长。”不对，计算精度不等于统计设计正确。
- “区间决定是否上线。”不对，报告不具有自动行动授权。

## 练习

1. 为什么按单条观测抽样会拆散同一分钟的共同故障？
2. 将四个小时块改成两个更长块，说明有效重采样单位减少的含义。
3. 写一个按用户簇而非时间块重采样的伪代码设计。
4. 设计一个趋势持续上升的反例，说明块间可交换为何不合理。

## 练习答案提示

1. 单条抽样可任意混合块内记录，消除了同批事件一起出现的结构。
2. 块数变少意味着块间重排的样本空间变小，区间通常更不稳定。
3. 先抽用户 ID，再保留该用户全部预定义记录与顺序。
4. 后期块系统性更高时，早晚块不来自相同机制。

## 延伸

[冻结窗口差异的 Bootstrap](/probability-ml/frozen-window-bootstrap)说明观测级合同；[冻结窗口的校准比较](/probability-ml/frozen-window-calibration-comparison)给出点差异；[数据漂移监控](/probability-ml/data-drift-monitoring)讨论输入分布随时间变化的证据边界。
