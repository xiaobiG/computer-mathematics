---
title: 信任根轮换与阈值监督：谁有权更换验证规则
description: 用虚构元数据重放信任根轮换的阈值授权、纪元推进与监督证据边界，理解日志和单把根密钥都不足以自动安全更新。
courseLevel: "3（密码协议与工程边界）"
prerequisites: "公钥身份与生命周期、已签名更新防回滚、透明日志"
estimatedMinutes: 80
experiment: "根轮换、追加日志与紧急恢复客户端兼容性的人工复核"
---

# 信任根轮换与阈值监督：谁有权更换验证规则

## 学习目标

你将区分根 ID、独立运营者、恢复授权与客户端兼容，并重放虚构策略；本文不生成密钥、验签或修改信任库。

## 从“根密钥泄露后怎么办”开始

客户端预置根；一把泄露时既不能允许它独自改写后继根，也不能要求所有根永远在线。问题是：当前集合以什么旧门槛、版本状态和监督证据改变下一代规则？

## 定义：根集合、阈值与纪元

令当前状态为

$$T_e=(e,R_e,t_e),$$

其中 $e$ 是单调纪元，$R_e$ 是根 ID 集合，$t_e$ 是根数阈值。另声明每个根的虚构运营者映射 $o:R_e\to O$ 与独立运营者门槛 $d_e\le t_e$。候选提议为

$$U=(e',R',t',A,W).$$

这里 $A$ 是声称已由当前根验证的授权标识集合，$W$ 表示监督/见证证据是否可用。教学策略的核心条件是

$$e'>e,\quad A\subseteq R_e,\quad |A|\ge t_e,\quad |o(A)|\ge d_e,\quad 1\le t'\le |R'|.
$$

根数和运营者数都按**旧**状态检查；两把根若同属一个运营者，不能假装成两方批准。纪元阻止旧提议重放，根集合也必须真实改变。

## 算法：先验证旧规则，再描述新规则

策略解析唯一根和阈值，检查纪元/集合变化、旧根授权数和运营者覆盖、新阈值及见证；见证缺失即停在人工复核，其他情形也至多“仅策略接受”。`approval_claims` 只是外部验证器已确认的教学声明，不是多签实现。

## 可运行实验：重放虚构根轮换报告

```python
from projects.crypto_toybox.root_rotation import (
    trust_root_rotation_certificate,
    trust_root_rotation_report,
)

state = {
    "epoch": 4, "root_ids": ["root-a", "root-b", "root-c"], "threshold": 2,
    "root_operator_ids": ["operator-a", "operator-b", "operator-c"],
    "minimum_distinct_approval_operators": 2,
}
proposal = {
    "new_epoch": 5,
    "new_root_ids": ["root-b", "root-d", "root-e"],
    "new_threshold": 2,
    "approval_claims": ["root-a", "root-b"],  # 外部验签后的教学声明
    "witness_evidence_available": True,
}
report = trust_root_rotation_report(state, proposal)
assert report["decision"] == "accept_for_policy_only"
assert report["automatic_apply"] is False
assert trust_root_rotation_certificate(report)["valid"]
```

运行 `python -m unittest projects.crypto_toybox.test_root_rotation`。合同 `trust-root-rotation-audit/v2` 重放状态、提议、运营者覆盖、失败项和结论；同一运营者控制的两把根不能满足独立性门槛。报告固定 `automatic_apply=False` 和 `cryptographic_verification="not_performed"`。

## 跨课实验：把追加日志产物接到轮换复核

上一课的 `append_only_report` 携带旧/新条目和追加结论；下游检查新增根是否以 `key:<root-id>` 出现在未改写的新条目中。

```python
from projects.crypto_toybox.root_rotation import (
    root_rotation_log_link_review,
    trust_root_rotation_report,
)
from projects.crypto_toybox.transparency_log import append_only_report

rotation = trust_root_rotation_report(state, proposal)
log = append_only_report(
    ["key:root-a", "key:root-b", "key:root-c"],
    ["key:root-a", "key:root-b", "key:root-c", "key:root-d", "key:root-e"],
)
review = root_rotation_log_link_review(rotation, log)
assert review["log_covers_added_roots"]
assert review["decision"] == "manual_review_with_policy_and_append_only_log_evidence"
assert review["automatic_apply"] is False
assert review["identity_binding"] == "not_established_by_log_entries"
```

删掉 `key:root-e` 会得到缺少日志条目；篡改日志会被拒绝。覆盖完整仍不验证批准、密钥/身份绑定或一致观察，故不能自动应用。

## 紧急恢复：客户端格式与预置授权不是同一件事

事件声明 `root-a` 受损时，含它的正常批准不能直接当紧急授权。客户端预置格式、纪元、根和恢复运营者；计划声明受损根、格式、恢复声明与带外通道。不同客户端会停在不同人工步骤：

```python
from projects.crypto_toybox.root_rotation import (
    root_rotation_recovery_compatibility_certificate,
    root_rotation_recovery_compatibility_report,
)

clients = [
    {"client_id": "modern", "trusted_root_ids": ["root-a", "root-b", "root-c"], "stored_epoch": 4,
     "supported_policy_versions": [1, 2], "recovery_operator_ids": ["recovery-a", "recovery-b"],
     "minimum_distinct_recovery_operators": 2},
    {"client_id": "legacy", "trusted_root_ids": ["root-a", "root-b", "root-c"], "stored_epoch": 4,
     "supported_policy_versions": [1], "recovery_operator_ids": ["recovery-a", "recovery-b"],
     "minimum_distinct_recovery_operators": 2},
]
emergency = {"policy_format_version": 2, "compromised_root_ids": ["root-a"],
             "recovery_claim_operator_ids": ["recovery-a", "recovery-b"], "out_of_band_channel_declared": True}
compatibility = root_rotation_recovery_compatibility_report(rotation, clients, emergency)
assert compatibility["client_reports"][0]["decision"] == "manual_recovery_with_declared_authorities"
assert compatibility["client_reports"][1]["decision"] == "manual_recovery_required_unsupported_policy_format"
assert root_rotation_recovery_compatibility_certificate(rotation, clients, emergency, compatibility)
```

它只检查虚构声明与预置状态是否相交，不验恢复签名、身份、通道或设备；格式、纪元或授权覆盖失败都不能悄悄回退。

## 正确性与工程边界

本合同以 $|A|\ge t_e$ 排除单根、$|o(A)|\ge d_e$ 排除同运营者重复、$A\subseteq R_e$ 排除新根自授权、$e'>e$ 排除重放；证书重算全部条件。见证处理分叉/可观察性，不证明新根可信或替代阈值；不可用时人工复核。

真实根轮换还涉及根材料保护、签名格式、设备状态、阈值成员失效、地域/组织独立性、时间源与日志一致性。阈值 $2/3$ 不是普适答案；它取决于风险、可用性和治理责任。

## 失败案例与工程边界

- **新根自授权或同运营者冒充多方。** 必须相对旧状态、外部核验的映射检查。
- **阈值或见证不足仍继续。** 它们分别遗漏授权独立性和分叉可观察性，应人工复核。
- **格式不懂就回退。** 兼容性失败会变成回滚入口；保留人工恢复状态。
- **把本代码接进信任库。** 禁止。真实系统应采用经过审计的更新框架、密钥管理、阈值签名/审批协议与事件响应流程。

## 常见误区

- “日志证明新根合法。”它不授予根权限。
- “阈值就是独立。”计数不保证人员、设备或组织独立。
- “策略接受即可替换根。”本课没有自动授权。

## 练习

1. 为什么仅有 $a$ 不能把 $\{a,b,c\}$、阈值 2 换为 $\{x\}$？
2. 为何检查 $|A|\ge t_e$ 而不是 $|A|\ge t'$？
3. **编码**：篡改批准或新增日志条目，确认下游拒绝；再令客户端不支持恢复格式。
4. **开放**：为离线设备说明成员失联、见证不可用和纪元损坏时的恢复责任。

## 练习答案提示

1. 当前规则要两份旧根授权；$x$ 尚未有权限。
2. 用 $t'$ 会让攻击者先把它降为 1 再自授权；旧阈值才已被信任。
3. 区分阈值、旧根归属、日志和格式失败；证书必须重算。
4. 明确受保护恢复能力、证据和停机窗口，不能让代码默认风险偏好。

## 延伸与下一步

先复习[公钥身份与密钥生命周期](/number-theory-crypto/public-key-lifecycle)中的身份和撤销，再连接[已签名更新与防回滚](/number-theory-crypto/signed-release-anti-rollback)的本地状态，以及[透明日志的 Merkle 证明](/number-theory-crypto/transparency-logs)的可审计历史。三者共同约束根轮换，但没有任何单一哈希、签名或策略报告能替代完整的生产治理。
