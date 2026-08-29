"""教学用途的模运算与小参数 RSA；不可用于真实安全场景。"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    if modulus <= 1 or exponent < 0:
        raise ValueError("模数必须大于 1，指数必须非负")
    result = 1
    base %= modulus
    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    divisor, x1, y1 = extended_gcd(b, a % b)
    return divisor, y1, x1 - (a // b) * y1


def modular_inverse(value: int, modulus: int) -> int:
    divisor, inverse, _ = extended_gcd(value, modulus)
    if divisor != 1:
        raise ValueError("模逆元不存在")
    return inverse % modulus


@dataclass(frozen=True)
class RsaKeyPair:
    modulus: int
    public_exponent: int
    private_exponent: int


def toy_rsa_keypair(p: int, q: int, public_exponent: int) -> RsaKeyPair:
    """由已知的小质数构造教学密钥；不生成也不验证生产级密钥。"""
    if p == q:
        raise ValueError("教学参数中的两个质数必须不同")
    phi = (p - 1) * (q - 1)
    if gcd(public_exponent, phi) != 1:
        raise ValueError("公开指数必须与 phi 互素")
    return RsaKeyPair(p * q, public_exponent, modular_inverse(public_exponent, phi))


def encrypt(message: int, key: RsaKeyPair) -> int:
    if not 0 <= message < key.modulus:
        raise ValueError("教学明文必须位于 [0, n) 内")
    return mod_pow(message, key.public_exponent, key.modulus)


def decrypt(ciphertext: int, key: RsaKeyPair) -> int:
    if not 0 <= ciphertext < key.modulus:
        raise ValueError("教学密文必须位于 [0, n) 内")
    return mod_pow(ciphertext, key.private_exponent, key.modulus)


def toy_rsa_sign(representative: int, key: RsaKeyPair) -> int:
    """Sign a small integer representative with the toy private exponent.

    This exposes the RSA verification equation for teaching only.  It is not a
    signature scheme: it has no hash-to-signature encoding, padding, key-size
    requirements, or side-channel protection.
    """
    if not 0 <= representative < key.modulus:
        raise ValueError("teaching representative must be in [0, n)")
    return mod_pow(representative, key.private_exponent, key.modulus)


def toy_rsa_verify(representative: int, signature: int, key: RsaKeyPair) -> bool:
    """Verify s**e == representative mod n for the teaching key pair."""
    if not 0 <= representative < key.modulus or not 0 <= signature < key.modulus:
        return False
    return mod_pow(signature, key.public_exponent, key.modulus) == representative


if __name__ == "__main__":
    key = toy_rsa_keypair(61, 53, 17)
    message = 65
    ciphertext = encrypt(message, key)
    print(f"n={key.modulus}, e={key.public_exponent}, d={key.private_exponent}")
    print(f"明文={message}, 密文={ciphertext}, 解密={decrypt(ciphertext, key)}")
