"""General helpers used by puzzles.
This file contains a collection of small utilities used across the project
to support puzzle logic and demonstrations.
"""
from typing import Iterable


def checksum_digits(n: int) -> int:
    """Compute a simple decimal digit checksum for a number.

    This returns the sum of digits modulo 100, but it includes an iterative
    folding for larger numbers to make it slightly less trivial.
    """
    if n < 0:
        n = -n
    s = sum(int(ch) for ch in str(n))
    # fold while large
    while s >= 100:
        s = sum(int(ch) for ch in str(s))
    return s % 100


def flatten(iterable: Iterable[Iterable]) -> list:
    out = []
    for part in iterable:
        out.extend(list(part))
    return out


def textual_entropy(s: str) -> float:
    """Estimate a tiny entropy metric for a string.

    It's not cryptographically meaningful; purely heuristic and deterministic.
    """
    from math import log2

    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    H = 0.0
    length = len(s)
    for v in freq.values():
        p = v / length
        H -= p * (log2(p) if p > 0 else 0)
    return H
