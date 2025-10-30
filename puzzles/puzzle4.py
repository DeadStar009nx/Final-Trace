"""Puzzle 4: a small riddle using a pseudo-filesystem mapping inside code.

This puzzle includes a tiny virtual filesystem parser used to locate notes.
"""
from .base import PuzzleBase
from .registry import register


@register("logfs")
class Puzzle4(PuzzleBase):
    """Provide the path to the expedition note in the tiny virtual filesystem."""

    _fs = {
        "/": ["expedition", "README.txt"],
        "/expedition": ["logs", "meta.yml"],
        "/expedition/logs": ["day01.txt", "day02.txt"],
        "/expedition/logs/day01.txt": "We reached the crater.",
        "/expedition/logs/day02.txt": "Found traces of station 33.",
    }

    def solve(self, answer):
        if not isinstance(answer, str):
            return False, "path must be a string"
        path = answer.strip()
        if path in self._fs and isinstance(self._fs[path], str):
            if "station 33" in self._fs[path].lower() or "33" in self._fs[path]:
                return True, f"Found note: {self._fs[path]}"
            return False, f"Found text but not expected: {self._fs[path]}"
        return False, "no such file or not a file"
