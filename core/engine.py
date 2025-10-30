"""Puzzle engine that registers and runs puzzles.

This module implements the central engine: helper classes, a simple
in-memory persistence shim, execution tracing, and configurable rules
for puzzle solving.
"""
from typing import Dict, Any, Tuple
import time
import traceback


class PuzzleError(Exception):
    pass


class InMemoryStore:
    """Very small persistence shim used by the engine to store attempts and state."""

    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def incr(self, key, delta=1):
        self._data[key] = self._data.get(key, 0) + delta
        return self._data[key]


class PuzzleEngine:
    """Main engine.

    - registry: mapping of puzzle name -> puzzle class
    - store: persistence shim
    """

    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry
        self.store = InMemoryStore()

    def list_puzzles(self):
        return list(self.registry.keys())

    def attempt(self, puzzle_name: str, answer: Any) -> Tuple[bool, str]:
        if puzzle_name not in self.registry:
            raise PuzzleError("puzzle not found")
        puzzle_cls = self.registry[puzzle_name]
        puzzle = puzzle_cls(self)
        attempt_id = f"attempt:{puzzle_name}:{int(time.time()*1000)}"
        try:
            started = time.time()
            ok, message = puzzle.solve(answer)
            duration = time.time() - started
            self.store.incr(f"puzzle:{puzzle_name}:attempts")
            self.store.set(f"{attempt_id}:duration", duration)
            self.store.set(f"{attempt_id}:ok", ok)
            self.store.set(f"{attempt_id}:message", message)
            return ok, message
        except Exception as e:
            tb = traceback.format_exc()
            self.store.set(f"{attempt_id}:error", tb)
            return False, f"internal error: {e}"

    def get_stats(self):
        # gather simple stats from store
        stats = {}
        for k, v in self.store._data.items():
            stats[k] = v
        return stats
