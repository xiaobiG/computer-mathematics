"""有限域椭圆曲线群运算的教学实现；绝不可用于真实密码学。"""

from __future__ import annotations

from dataclasses import dataclass

from projects.crypto_toybox.main import modular_inverse


Point = tuple[int, int] | None  # None 表示无穷远点 O。


def is_prime(value: int) -> bool:
    """足够检查小教学参数；生产系统应使用成熟的大整数与素性实现。"""
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


@dataclass(frozen=True)
class ToyCurve:
    """短 Weierstrass 曲线 y² = x³ + ax + b (mod p)，仅支持奇素数小参数。"""

    p: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if self.p <= 3 or not is_prime(self.p):
            raise ValueError("教学曲线需要大于 3 的奇素数模数")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("判别式为零，曲线存在奇点，不能形成所需群")

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def require_point(self, point: Point) -> None:
        if not self.contains(point):
            raise ValueError("点不在此曲线上")

    def add(self, left: Point, right: Point) -> Point:
        """按割线-切线公式计算 left + right，O 是加法单位元。"""
        self.require_point(left)
        self.require_point(right)
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            slope = ((3 * x1 * x1 + self.a) * modular_inverse(2 * y1 % self.p, self.p)) % self.p
        else:
            slope = ((y2 - y1) * modular_inverse((x2 - x1) % self.p, self.p)) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        return x3, y3

    def scalar_multiply(self, scalar: int, point: Point) -> Point:
        """重复平方式的 double-and-add；运行时间为 O(log scalar)。"""
        if scalar < 0:
            raise ValueError("教学实现仅接受非负标量")
        self.require_point(point)
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            scalar >>= 1
        return result


if __name__ == "__main__":
    curve = ToyCurve(p=17, a=2, b=2)
    generator = (5, 1)
    print(f"2G = {curve.scalar_multiply(2, generator)}")
    print(f"7G = {curve.scalar_multiply(7, generator)}")
