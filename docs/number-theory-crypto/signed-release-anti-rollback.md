---
title: 已签名更新为何仍可能回滚：版本状态与撤销可用性
description: 用可重放的虚构发布元数据审计，区分数学验签、身份信任、防回滚状态与撤销信息不可用时的策略。
courseLevel: "3（密码协议与工程边界）"
prerequisites: "数字签名、公钥身份与密钥生命周期、比较与状态机"
estimatedMinutes: 60
experiment: "signed-release-policy-audit/v1：审计虚构发布版本、身份、用途、撤销状态与受保护的最低版本"
---

# 已签名更新为何仍可能回滚：版本状态与撤销可用性

## 学习目标

你将能解释一份签名有效的旧更新为何仍必须拒绝；把“已接受的最低版本”视为受保护状态而不是普通字段；区分撤销信息不可用时的拒绝与人工复核策略；并能重放一份**虚构元数据**审计报告。本文不生成密钥、不验真实签名、不联网下载撤销信息，也不安装任何软件。

## 从“旧包也有有效签名”开始

假设版本 7 曾正常发布，后来发现其中存在严重漏洞，发布者已签名版本 8 修复它。攻击者如果把仍带原始有效签名的版本 7 交给客户端，单独的验签等式仍可能成立。因此客户端还需要保存自己已接受的状态 $v_{\min}$，并要求候选版本 $v$ 满足

$$v>v_{\min}.$$

签名回答“谁认可了精确消息”；单调版本策略回答“这个消息相对于我已知状态是否足够新”。后者是协议状态与本地保护问题，不能由公钥密码等式自动给出。

## 直觉与定义：接受是多条件合取

对教学中的候选发布记录，令 $S$ 表示外部成熟库已给出的“签名声明有效”，$I$ 表示公钥身份可信，$K$ 表示密钥 active，$C$ 表示上下文匹配，$R$ 表示撤销信息可用。一个**仅用于教学审计**的接受条件是

$$A=(v>v_{\min})\land S\land I\land K\land C\land R.$$

这里的 `signature_claim_valid` 只是输入字段，绝不是本文实现的验签结果。它的作用是隔离问题：即使先假设数学验签通过，版本回滚、公钥替换、用途错误和撤销状态仍各自能拒绝候选。

## 可运行实验：重放虚构策略报告

```python
from projects.crypto_toybox.release_policy import (
    signed_release_policy_certificate,
    signed_release_policy_report,
)

candidate = {
    "version": 8,
    "key_id": "demo-release-key-2026",
    "algorithm": "Ed25519",
    "context": "software-update/v1",
    "signature_claim_valid": True,       # 教学输入，不是本代码验签
    "key_identity_trusted": True,
    "key_status": "active",
    "revocation_info_available": True,
}
report = signed_release_policy_report(7, candidate)
assert report["decision"] == "accept_for_policy_only"
assert report["automatic_install"] is False
assert signed_release_policy_certificate(report)["valid"]
```

运行 `python -m unittest projects.crypto_toybox.test_release_policy`。报告合同是 `signed-release-policy-audit/v1`：字段必须精确匹配；证书从候选记录和策略独立重放检查、失败项和结论。它不访问网络、文件系统、密钥库或软件包。

## 正确性与边界

在固定的教学合同内，报告会拒绝 $v\leq v_{\min}$，即使 `signature_claim_valid=True`；也会拒绝未信任身份、非允许算法、错误上下文、非 active 密钥或不可用的撤销信息。若撤销信息不可用，策略只能显式产生 `reject` 或 `manual_review`，不会把它静默变为接受。

这并不证明真实更新安全：现实中的版本语义、信任锚更新、时钟、离线设备、镜像攻击、恢复路径、透明日志以及撤销分发都需要独立威胁模型。特别地，`accept_for_policy_only` 不等于可安装，`automatic_install` 始终为 `False`。

## 失败案例与工程边界

- **有效的旧版本。** 版本 7 的签名未必失效，但 $7\leq7$，所以应拒绝。
- **公钥替换。** 攻击者可提供自己有效的签名声明；`key_identity_trusted=False` 仍必须拒绝。
- **撤销信息不可用。** `fail-open` 会把未知状态当安全；本合同只允许拒绝或停在人工复核。
- **本地状态可被覆盖。** 如果攻击者能任意降低 $v_{\min}$，单调检查失去意义；状态本身必须被保护。
- **把教学报告接入更新器。** 禁止这样做。真实系统应采用成熟的软件更新框架、签名库、信任根和组织风险流程。

## 常见误区

- **“版本号大就够了。”** 还要验证身份、算法、用途/上下文、密钥状态和撤销信息。
- **“撤销只和有效期有关。”** 失窃密钥可在到期前被撤销，且撤销信息的时效与可用性本身是风险。
- **“manual_review 等于接受。”** 它表示证据不完整，自动安装仍为 false。
- **“签名字段为真就安全。”** 本实验故意把它当假设，以展示剩余检查为何不可省略。

## 练习

1. 为什么 $v\geq v_{\min}$ 不足以阻止同版本替换或重复部署？在何种协议语义下才可能允许相等？
2. 将例子中的 `context` 改成 `telemetry-config/v1`，说明为何即使签名声明为真也要拒绝。
3. 对离线设备比较 `reject` 与 `manual_review` 的可用性和风险；为什么不能默认选其中之一？
4. 哪些组件必须保护 $v_{\min}$，才能使防回滚检查成立？

## 练习答案提示

1. 相等版本可能被重放；只有内容哈希、通道与幂等语义都被协议绑定时，才可显式允许。
2. 上下文是域分离和用途限制；更新签名不能自动授权配置通道。
3. 拒绝优先保护完整性但会阻断更新；人工复核保留运营决策，两者取决于威胁模型和恢复能力。
4. 本地持久化、可信硬件或受控恢复流程都可能参与；关键是攻击者不能无授权降低它。

## 延伸

[公钥身份与密钥生命周期](/number-theory-crypto/public-key-lifecycle)解释前置的身份、轮换和撤销状态；[数字签名](/number-theory-crypto/digital-signatures)回到公开验证的数学骨架；[消息认证码](/number-theory-crypto/message-authentication-codes)对照共享密钥系统中的重放边界。
