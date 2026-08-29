---
title: 哈希、MAC 与密码存储：为什么“加密密码”仍是错误模型
description: 区分哈希、MAC、盐与密码 KDF，用 PBKDF2 教学示例理解验证、成本参数和离线猜测边界。
courseLevel: "2–3（安全工程）"
prerequisites: "哈希、随机性与威胁模型"
estimatedMinutes: 55
experiment: "比较加盐与慢 KDF 的离线猜测成本"
---

# 哈希、MAC 与密码存储：为什么“加密密码”仍是错误模型

## 学习目标

读完后，你能区分通用哈希、MAC、加密与密码 KDF 的目标；写出密码记录应保存的字段；用标准库做一个仅教学的 PBKDF2 验证示例；并解释盐、成本参数、常数时间比较和登录限速分别防御什么。

## 从一次数据库泄露开始

若数据库保存明文密码，泄露立即变成账户接管。若保存 `SHA256(password)`，攻击者可离线高速枚举常见密码，并将同一摘要与其他泄露库关联。若保存可逆加密密码，密钥一旦泄露仍可批量恢复全部原文。

正确目标不是“日后取回密码”，而是：服务器收到候选密码时，能判断它是否与当初设置的一致，同时让偷走数据库的人每猜一次都付出昂贵成本。

## 四个相似名词，四种不同目标

| 原语 | 输入与密钥 | 目标 | 不能替代 |
| --- | --- | --- | --- |
| 通用哈希 | 任意消息，无密钥 | 完整性指纹、索引 | 密码 KDF、身份认证 |
| MAC/HMAC | 消息与共享密钥 | 证明持钥者产生/认证消息 | 密码存储、加密 |
| 对称加密 | 明文与密钥 | 保密且通常需认证模式 | 不可逆密码验证 |
| 密码 KDF | 密码、盐、成本参数 | 增大离线猜测成本 | 登录限速、MFA |

哈希的抗碰撞不等于适合密码：密码的熵很低，攻击者无需找碰撞，只要逐个猜测并比较输出。密码 KDF 故意慢，并尽可能耗内存；优先使用平台认可的 Argon2id，其次按环境选择 scrypt/bcrypt/PBKDF2。

## 存储记录与验证流程

每个账户生成唯一随机盐 $s$，并保存一个自描述记录：

```text
algorithm = argon2id
version = ...
salt = 随机字节
memory/time/parallelism = 成本参数
derived_key = KDF(password, salt, parameters)
```

验证时读取同一记录，重新派生候选值并做安全比较。盐无需保密；它让相同密码产生不同记录，并使攻击者不能为所有用户预先做一张通用彩虹表。成本参数也不固定：应随着硬件与服务延迟预算升级，并在成功登录时逐步迁移旧记录。

## 可运行教学示例：使用库，不自造 KDF

```python
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes

def make_password_record(password: str, *, rounds=200_000) -> dict:
    if not password or rounds < 100_000:
        raise ValueError("示例要求非空密码和足够迭代次数")
    salt = token_bytes(16)
    derived = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return {"algorithm": "pbkdf2_sha256", "rounds": rounds, "salt": salt, "derived": derived}

def verify_password(password: str, record: dict) -> bool:
    if record.get("algorithm") != "pbkdf2_sha256":
        raise ValueError("未知或不受支持的记录格式")
    candidate = pbkdf2_hmac("sha256", password.encode("utf-8"),
                             record["salt"], record["rounds"])
    return compare_digest(candidate, record["derived"])

record = make_password_record("demo-only-password")
assert verify_password("demo-only-password", record)
assert not verify_password("wrong-password", record)
```

这段代码展示记录形状与验证流，不是完整认证系统：示例成本参数不是普适安全建议；生产环境应通过所选库和部署硬件的基准测试确定参数，并交给受审计的身份平台处理会话、恢复、MFA 和监控。

## 为什么安全比较与限速都需要

普通字节比较可能在第一个不同字节提前返回，理论上泄露比较时长；`compare_digest` 尽量避免该类信号。它主要减少在线侧信道，不会阻止已获数据库的攻击者离线计算。

KDF 抬高**每次离线猜测**成本；登录限速、IP/账户节流、MFA 和异常检测限制**在线猜测**。它们防御面不同，不能用“已经加盐”代替。

## 失败案例与工程边界

- **共享盐或用户名作盐**：可减少预计算，但仍让相同密码容易关联；每条记录须随机盐。
- **快速哈希加很多轮循环**：容易写错、未必内存硬；使用专用 KDF 的经过审查实现。
- **把 pepper 当盐**：pepper 是额外服务器秘密，泄露模型不同，且不能替代随机盐和 KDF。
- **只防数据库泄露**：钓鱼、恶意客户端、会话劫持和密码重用仍需 MFA、TLS、会话管理与用户教育。

## 常见误区

1. “哈希是加密的一种。”错误：哈希设计为不可逆摘要，加密设计为可解密保密。
2. “盐必须保密。”错误：盐可公开，唯一性与随机性才重要。
3. “一次 KDF 调用就安全。”错误：算法、参数、随机数、比较、限速和系统边界共同决定风险。
4. “保存加密密码便于找回。”错误：密码找回应使用一次性恢复流程，不应恢复旧密码。

## 练习

1. **基础题**：列出一条密码记录必须保存的五类字段，并说明哪些可公开。
2. **推导题**：若攻击者有 $N$ 个用户和一张预计算表，说明唯一随机盐为何使其不能直接复用同一张表；指出这并不增加单个低熵密码的熵。
3. **编码题**：为示例添加“成功登录后若 rounds 过旧则重新派生”的迁移函数，并测试错误密码不会触发迁移。
4. **开放题**：为一个高价值账户系统画出在线与离线攻击面，分别分配 KDF、限速、MFA、会话失效和告警措施。

## 延伸

MAC 在协议中认证消息，而密码 KDF 验证低熵口令；不要互换二者。继续阅读[Diffie–Hellman](/number-theory-crypto/diffie-hellman)，理解密钥协商后仍需要 KDF 与认证。生产实践请遵循所用平台和库的最新安全指南，而非复制本页参数。
