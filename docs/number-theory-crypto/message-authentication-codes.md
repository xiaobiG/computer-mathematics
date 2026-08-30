---
title: 消息认证码：完整性为什么需要密钥
description: 从攻击者可重算哈希的反例出发，解释 HMAC 的结构、验证流程、常量时间比较与“认证不等于保密”的边界。
courseLevel: "2–3（密码原语、协议与工程边界）"
prerequisites: "哈希、共享密钥、威胁模型与字节编码"
estimatedMinutes: 50
experiment: "用标准库 HMAC 为消息生成标签，并验证消息或标签篡改会失败"
---

# 消息认证码：完整性为什么需要密钥

## 学习目标

读完后，你能区分哈希、MAC 与加密；说明攻击者为何能重算裸哈希；使用标准库生成和验证 HMAC；并识别重放、密钥管理和明文泄露等 MAC 无法单独解决的问题。

## 从“附加 SHA-256”失败开始

客户端发送 `amount=100` 和其 SHA-256 摘要。中间人把消息改为 `amount=900`，再计算新摘要即可通过校验：哈希能发现意外损坏，却不能证明消息来自持钥者。MAC 引入只有通信双方知道的密钥 $K$，目标是让不知道 $K$ 的攻击者难以为新消息伪造有效标签。

## 定义与 HMAC 结构

MAC 是函数 $t=\operatorname{MAC}_K(m)$；接收者重新计算并比较标签。安全目标是选择消息攻击下的不可伪造性，而不是“摘要看起来随机”。HMAC 以哈希 $H$ 组合内外两层：

$$\operatorname{HMAC}_K(m)=H((K'\oplus opad)\,\|\,H((K'\oplus ipad)\,\|\,m)).$$

这里 $K'$ 是按块大小处理的密钥，`ipad`/`opad` 是固定不同填充。不要用 `hash(key || message)` 替代 HMAC：某些哈希构造会受长度扩展等问题影响；直接调用标准库 HMAC。

## 可运行实验

```python
from projects.crypto_toybox.message_auth import hmac_tag, verify_hmac

key, message = b"demo-shared-key", b"amount=100"
tag = hmac_tag(key, message)
assert verify_hmac(key, message, tag)
assert not verify_hmac(key, b"amount=900", tag)
```

```bash
python -m unittest projects.crypto_toybox.test_message_auth
```

标签生成与验证为消息长度的 $O(n)$；实现使用 `compare_digest`，避免普通逐字节比较尽早退出所造成的一类时序信号。测试覆盖正常验证、消息篡改、标签篡改和空密钥拒绝。

## 正确性与工程边界

验证函数以同一密钥和消息重算 HMAC，再常量时间比较。标签匹配说明“持有该共享密钥的一方计算过同一字节串”，不说明谁在多人共享密钥中发送，也不提供不可否认性。MAC 也不加密消息；旁观者仍可读取 `amount=100`。需要保密和认证时使用经审计的 AEAD 协议，而不是手工拼接加密与 MAC。

## 失败案例与常见误区

- **重放**：攻击者可重发一条曾经有效的 MAC 消息；加入序号、时间窗或随机 nonce，并由协议验证新鲜性。
- **歧义编码**：`("ab", "c")` 与 `("a", "bc")` 若直接拼接字节可能相同；必须定义长度前缀或规范序列化。
- **密钥复用**：同一密钥不应随意跨协议、跨用途复用；应按协议使用 KDF 分离密钥。
- **认证当作授权**：MAC 只证明持钥，不能替代服务器端权限检查。

## 练习

1. **基础题**：说明为什么攻击者能为修改后的裸哈希消息重算摘要，却不能在未知密钥下重算 HMAC。
2. **推导题**：写出 HMAC 内外层的输入，并解释为何两个不同填充是必要结构的一部分。
3. **编码题**：为带序号的消息设计无歧义编码，并测试旧序号重放被拒绝。
4. **开放题**：为 API 请求认证列出必须覆盖的方法、路径、主体、时间和 nonce，并说明日志中哪些字段不能泄露。

## 练习答案提示

1. 裸哈希没有秘密，攻击者可对修改后消息再算摘要；HMAC 的标签依赖未知密钥，攻击者不能凭公开消息重算有效标签。
2. HMAC 形如 $H((K\oplus opad)\|H((K\oplus ipad)\|m))$；内外两层与不同填充形成规范构造，不能简化为随意字符串拼接。
3. 用长度前缀或规范二进制序列化编码序号和主体；服务端保存/验证单调序号或去重窗口，旧序号即使标签正确也必须拒绝。
4. 认证输入应覆盖方法、规范路径、主体哈希、时间、nonce 和密钥标识；日志不能记录密钥、完整认证标签或敏感主体，且需避免泄漏可重放材料。

## 延伸

[哈希与密码存储](/number-theory-crypto/hashing-passwords)区分 KDF 与 MAC；[Diffie–Hellman](/number-theory-crypto/diffie-hellman)说明协商共享秘密后仍需要认证；[密码学玩具箱](/projects/crypto-toybox)提供实验。真实协议优先使用 TLS、平台签名机制和受审计库。
