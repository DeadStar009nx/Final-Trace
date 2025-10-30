"""Script to generate mock data and sample attempts for the engine.

This script can be used by event authors to pre-populate the in-memory store
or to generate sample run logs used in tests.
"""
import json
from core.engine import PuzzleEngine
from puzzles.registry import registry


def generate_sample_run():
    engine = PuzzleEngine(registry)
    samples = []
    # try some sample answers
    for name in registry.keys():
        # dumb attempts: first try a bad value, then try something more plausible
        samples.append((name, "badanswer"))
        samples.append((name, "33"))
    results = []
    for name, ans in samples:
        ok, msg = engine.attempt(name, ans)
        results.append({"puzzle": name, "answer": ans, "ok": ok, "message": msg})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    generate_sample_run()
