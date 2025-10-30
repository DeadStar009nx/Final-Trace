"""Puzzle 1: Simple Caesar-like challenge with an extra twist.

This puzzle expects the user to provide a numeric shift that, when
applied to a scrambled phrase, yields a recognizable sentence.
"""
from .base import PuzzleBase
from .registry import register


@register("cryptic-shift")
class Puzzle1(PuzzleBase):
    """Decode the expedition log by applying the correct shift."""

    _cipher_text = "Guvf vf gur racenpgvba bs Rkqvgrra 33"

    def solve(self, answer):
        # Expect either numeric shift or exact decoded phrase
        if isinstance(answer, int):
            decoded = self._rot_n(self._cipher_text, answer)
            if "Expedition" in decoded or "Expedition".lower() in decoded.lower():
                return True, f"Decoded: {decoded}"
            return False, f"Decoded but not recognizable: {decoded}"
        if isinstance(answer, str):
            normalized = answer.strip()
            if "Expedition" in normalized or "expedition" in normalized:
                return True, "Nice! Looks like the phrase is present."
            return False, "String provided but not correct."
        return False, "Unsupported answer type"

    @staticmethod
    def _rot_n(s, n):
        # Simple rot-n on ASCII letters
        out = []
        for ch in s:
            if 'a' <= ch <= 'z':
                out.append(chr((ord(ch) - ord('a') + n) % 26 + ord('a')))
            elif 'A' <= ch <= 'Z':
                out.append(chr((ord(ch) - ord('A') + n) % 26 + ord('A')))
            else:
                out.append(ch)
        return ''.join(out)
