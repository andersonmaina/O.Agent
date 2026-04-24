"""
Mathematical utilities and calculations
"""

import math
import statistics
from typing import List, Optional
from functools import reduce


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage of value out of total."""
    if total == 0:
        return 0.0
    return (value / total) * 100


def calculate_average(numbers: List[float]) -> float:
    """Calculate arithmetic mean of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def calculate_median(numbers: List[float]) -> float:
    """Calculate median of numbers."""
    if not numbers:
        return 0.0
    return statistics.median(numbers)


def calculate_mode(numbers: List[float]) -> List[float]:
    """Calculate mode(s) of numbers."""
    if not numbers:
        return []
    try:
        return [statistics.mode(numbers)]
    except statistics.StatisticsError:
        return statistics.multimode(numbers)


def calculate_std_dev(numbers: List[float], sample: bool = True) -> float:
    """Calculate standard deviation."""
    if len(numbers) < 2:
        return 0.0
    if sample:
        return statistics.stdev(numbers)
    return statistics.pstdev(numbers)


def calculate_variance(numbers: List[float], sample: bool = True) -> float:
    """Calculate variance."""
    if len(numbers) < 2:
        return 0.0
    if sample:
        return statistics.variance(numbers)
    return statistics.pvariance(numbers)


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def get_factors(n: int) -> List[int]:
    """Get all factors of a number."""
    factors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)


def gcd(a: int, b: int) -> int:
    """Calculate greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Calculate least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def fibonacci(n: int) -> List[int]:
    """Generate first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq


def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)


def permutations(n: int, r: int = None) -> int:
    """Calculate number of permutations."""
    if r is None:
        r = n
    return math.perm(n, r)


def combinations(n: int, r: int) -> int:
    """Calculate number of combinations."""
    return math.comb(n, r)


def power(base: float, exponent: float) -> float:
    """Calculate power of a number."""
    return base ** exponent


def sqrt(n: float) -> float:
    """Calculate square root."""
    return math.sqrt(n)


def cbrt(n: float) -> float:
    """Calculate cube root."""
    if n < 0:
        return -(-n) ** (1/3)
    return n ** (1/3)


def log(n: float, base: float = math.e) -> float:
    """Calculate logarithm."""
    return math.log(n, base)


def log10(n: float) -> float:
    """Calculate base-10 logarithm."""
    return math.log10(n)


def log2(n: float) -> float:
    """Calculate base-2 logarithm."""
    return math.log2(n)


def sin(x: float) -> float:
    """Calculate sine (radians)."""
    return math.sin(x)


def cos(x: float) -> float:
    """Calculate cosine (radians)."""
    return math.cos(x)


def tan(x: float) -> float:
    """Calculate tangent (radians)."""
    return math.tan(x)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return math.radians(degrees)


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(radians)


def round_to(value: float, decimals: int = 0) -> float:
    """Round to specified decimal places."""
    return round(value, decimals)


def floor(value: float) -> int:
    """Round down to nearest integer."""
    return math.floor(value)


def ceil(value: float) -> int:
    """Round up to nearest integer."""
    return math.ceil(value)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end."""
    return start + t * (end - start)


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate 2D Euclidean distance."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """Calculate 3D Euclidean distance."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
