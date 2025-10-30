"""Puzzle 3: small number theory puzzle that returns a checksum.
This module demonstrates longer code and some utilities being used.
"""
from .base import PuzzleBase
from .registry import register
from utils.helpers import checksum_digits


@register("echo-checksum")
class Puzzle3(PuzzleBase):
    """Supply the right numeric seed which yields a matching checksum."""

    SEED = 331

    def solve(self, answer):
        try:
            val = int(answer)
        except Exception:
            return False, "please provide an integer"

        calc = checksum_digits(val)
        # small rule: the sum plus seed modulo 100 should be 33
        if (calc + (self.SEED % 100)) % 100 == 33:
            return True, f"Valid seed — checksum {calc}"
        return False, f"Checksum {calc} not matching"
