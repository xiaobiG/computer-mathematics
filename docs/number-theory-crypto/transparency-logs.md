---
title: 透明日志的 Merkle 证明：成员、追加与信任边界
description: 用小型 SHA-256 Merkle 树重放成员证明与追加前缀审计，理解日志可审计性不能自动建立信任锚。
courseLevel: "3（密码协议与工程边界）"
prerequisites: "哈希、数字签名、公钥身份与密钥生命周期"
estimatedMinutes: 60
experiment: "append-only-merkle-log/v1：成员证明与追加前缀报告"
---

# 透明日志的 Merkle 证明：成员、追加与信任边界

## 学习目标

你将能解释 Merkle 根如何承诺一组有序条目、如何用 $O(\log n)$ 个兄弟哈希验证成员，以及为什么“新日志以前缀保留旧日志”比只比较两个根更强。你也会区分日志可审计性与信任锚更新本身。本课只处理本地虚构字符串，不实现证书透明度、签名、网络服务或真实密钥。

## 从“我看到了一个公钥”开始

若发布者在公开日志中登记了公钥，客户端希望检查两件不同的事：某个条目确实出现过，且后来版本没有悄悄改写旧条目。把叶哈希写成 $h_L(x)=H(\mathtt{leaf}\|x)$，内部节点为 $h_N(a,b)=H(\mathtt{node}\|a\|b)$，树根 $r$ 就是对整个有序列表的短承诺。标签避免把叶内容和内部节点的字节串混为同一类输入。

## 成员证明与追加条件

对第 $i$ 个叶，验证者沿树向上组合其兄弟哈希；平衡树高度为 $O(\log n)$，所以证明大小也为 $O(\log n)$。但 $r_{old}\ne r_{new}$ 只说明内容不同，不能说明新增是追加。教学合同直接保留两份小列表并检查

$$L_{new}[0:|L_{old}|]=L_{old},\qquad |L_{new}|\ge |L_{old}|.$$

现实透明日志会用紧凑一致性证明替代下载整份前缀；这里选择可读的前缀重放，目的是突出“追加”和“重写”的语义差异。

## 可运行实验

```python
from projects.crypto_toybox.transparency_log import (
    append_only_certificate, append_only_report, checkpoint_from_entries,
    inclusion_certificate, inclusion_proof, split_view_certificate, split_view_report,
)

old = ["key:alpha", "key:beta", "key:gamma"]
proof = inclusion_proof(old, 1)
assert inclusion_certificate(proof)

report = append_only_report(old, old + ["key:delta"])
assert report["decision"] == "append_only"
assert append_only_certificate(report)
assert report["trust_anchor_update_verified"] is False

checkpoint_a = checkpoint_from_entries("fictional-log", old)
checkpoint_b = checkpoint_from_entries("fictional-log", ["key:alpha", "key:evil", "key:gamma"])
fork_check = split_view_report(checkpoint_a, checkpoint_b)
assert fork_check["candidate_equivocation"]
assert fork_check["checkpoint_authentication"] == "not_verified"
assert split_view_certificate(checkpoint_a, checkpoint_b, fork_check)
```

运行 `python -m unittest projects.crypto_toybox.test_transparency_log`。`append-only-merkle-log/v1` 会重建两棵树、成员证明和前缀结论；篡改条目或把旧列表中 `key:beta` 重写为另一个值都会被拒绝。

## 分叉视图：什么才算矛盾证据

两个根不同并不自动表示日志作恶。日志从 $n$ 个条目追加到 $n+1$ 个条目时，根必然变化；此时需要一致性证明（本课用完整前缀重放代替）来判断新检查点是否延续旧检查点。反过来，如果两个检查点声称来自**同一日志身份**、树大小相同却根不同，那么同一有序条目序列不可能同时产生这两个根；这是候选分叉证据。

实验中的 `split_view_report` 将这两种情形分开：同大小不同根给出 `candidate_equivocation_requires_authenticated_checkpoints`，不同大小则给出 `inconclusive_requires_append_only_consistency_evidence`。但两者都不触发自动动作，且固定 `checkpoint_authentication="not_verified"`：代码只重放课堂中的完整条目，不能证明 `operator_id` 真对应哪个网络日志或两个检查点真的由它签发。现实客户端还需要协议规定的检查点签名、日志身份绑定、gossip 或独立监督者。

## 将产物交给下游协议复核

`append_only_report` 的下一步不是“日志因此可信”，而是将这份可重算的追加产物传给[信任根轮换](/number-theory-crypto/trust-root-rotation)。下游只检查候选新增根是否在未改写的新日志条目中出现，并仍固定人工复核、禁止自动应用。于是，改变 `new_entries` 会改变根轮换复核中的缺失条目；但 Merkle 前缀证明仍不能验证批准签名、密钥材料或身份绑定。

## 正确性与边界

在 SHA-256 抗碰撞的假设下，成功的成员证明把给定条目绑定到给定根；前缀比较再证明这份**教学中的完整新列表**没有改写旧列表。奇数层重复最后叶只是一种明确的课堂树规则，真实生态的树形与一致性证明格式必须由对应协议规定。

Merkle 根不告诉你谁运营日志、日志是否可用、不同观察者是否看到同一棵树，也不授权新的根密钥。因此报告固定 `trust_anchor_update_verified=False`：透明日志是审计证据的一层，不是信任锚更新协议。

## 失败案例与工程边界

- **只看新根。** 根改变无法区分“追加新密钥”和“替换旧密钥”。
- **只接受单个成员证明。** 它不证明日志对其他观察者一致，也不证明后续追加。
- **分叉视图。** 恶意日志可能向不同客户端给出不同根；需要监督者、gossip 或协议级一致性机制。
- **把不同大小的根当分叉。** 正常追加也会改变根和树大小；必须验证追加关系，而非只比较根字符串。
- **把候选冲突当可执行惩罚。** 同大小不同根只有在两个检查点可认证地属于同一日志时才构成矛盾；本课不验证签名或网络身份。
- **把日志条目当身份。** `key:alpha` 是示例字符串；仍需可信身份绑定与用途约束。
- **把本代码用于生产。** 禁止。真实系统应使用已审计的透明日志协议、客户端库与运营流程。

## 常见误区

- **“有哈希就有信任。”** 哈希提供完整性承诺，不提供发布者身份。
- **“追加证明替代撤销。”** 撤销状态、有效期和客户端策略仍需独立检查。
- **“日志可用就不存在回滚。”** 客户端仍须保护最低版本并验证更新上下文。
- **“列表前缀检查很高效。”** 它是本课的可读实现；大规模系统使用协议规定的一致性证明。

## 练习

1. 为什么成员证明需要记录兄弟哈希位于左侧还是右侧？
2. 给出一个根改变但不是追加的两列表例子。
3. 说明透明日志如何帮助发现密钥替换，却为何不能独自认证密钥身份。
4. 哪些额外机制可降低分叉视图风险？
5. 为什么“同一身份、同一树大小、不同根”比“两个大小不同的根”更接近分叉证据？还缺少哪项验证？

## 练习答案提示

1. 哈希组合通常不交换；左右顺序改变会得到不同父节点。
2. 例如把旧列表第二项替换后再添加一项；根会变，前缀条件失败。
3. 观察者可比较登记历史，但身份仍来自信任锚、证书或带外确认。
4. 多方监督、gossip、见证者或协议定义的一致性证明；具体选择依赖威胁模型。
5. 同一有序条目列表在固定树规则下只能对应一个根；大小不同可能只是追加。仍需确认检查点签名与日志身份。

## 延伸

[已签名更新为何仍可能回滚](/number-theory-crypto/signed-release-anti-rollback)说明客户端最低版本状态；[公钥身份与密钥生命周期](/number-theory-crypto/public-key-lifecycle)说明身份、用途与撤销；[哈希与密码存储](/number-theory-crypto/hashing-passwords)复习哈希不等于身份认证。
