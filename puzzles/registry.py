"""Registry for puzzles.
This file includes a decorator-based registry and registers several example puzzles.
"""
from typing import Dict, Type
from .base import PuzzleBase

registry: Dict[str, Type[PuzzleBase]] = {}


def register(name: str):
    def _decorator(cls: Type[PuzzleBase]):
        registry[name] = cls
        cls.__puzzle_name__ = name
        return cls

    return _decorator


# Import puzzles to ensure they register themselves
from . import puzzle1  # noqa: F401
from . import puzzle2  # noqa: F401
from . import puzzle3  # noqa: F401
from . import puzzle4  # noqa: F401
