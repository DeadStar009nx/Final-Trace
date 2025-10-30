"""Base classes and helpers for puzzles."""
from typing import Tuple, Optional


class PuzzleBase:

    def __init__(self, engine):
        self.engine = engine
 """Create a deeper inspection of attempt messages and textual features.

    This function applies a small fingerprint and entropy heuristic to
    message strings so a report can surface atypical or high-entropy
    outputs.
    """
    @classmethod
    def describe(cls):
        return {
            "name": getattr(cls, "__puzzle_name__", cls.__name__),
            "description": getattr(cls, "__doc__", "No description"),
        }

    def solve(self, answer) -> Tuple[bool, str]:
        raise NotImplementedError()
