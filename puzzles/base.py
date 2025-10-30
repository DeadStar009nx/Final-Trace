"""Base classes and helpers for puzzles."""
from typing import Tuple, Optional


class PuzzleBase:
    """A puzzle implementation should subclass this.

    Methods:
    - describe() -> dict: metadata for listing
    - solve(answer) -> (bool, message): attempt to solve
    """

    def __init__(self, engine):
        self.engine = engine

    @classmethod
    def describe(cls):
        return {
            "name": getattr(cls, "__puzzle_name__", cls.__name__),
            "description": getattr(cls, "__doc__", "No description"),
        }

    def solve(self, answer) -> Tuple[bool, str]:
        raise NotImplementedError()
