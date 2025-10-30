"""Analytics and reporting utilities for Final-Trace.

This module provides a self-contained analytics tool that exercises
the `PuzzleEngine` and collects runtime metrics. It produces a
compact JSON report and a lightweight text view useful for
demonstrations or offline analysis.

Design goals:
- Use only local imports and deterministic behavior where possible.
- Provide functions that are unit-testable and composable.
- Keep the API small: Collector class + report generators.

This file is intentionally long to provide a realistic, feature-rich
tool. It does not contain secrets or challenge hints.
"""
from __future__ import annotations

import json
import time
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Tuple

from core.engine import PuzzleEngine
from puzzles.registry import registry
from utils.crypto import fingerprint_text, simple_hash
from utils.helpers import textual_entropy


@dataclass
class AttemptRecord:
    """A small record representing a single attempt.

    Attributes:
        puzzle: puzzle name
        answer: input provided (kept as string for reporting)
        ok: boolean success indicator
        message: textual message returned by the engine
        duration: time in seconds the engine reported (float)
        ts: timestamp when attempt run (Unix seconds)
    """

    puzzle: str
    answer: str
    ok: bool
    message: str
    duration: float
    ts: float


class DataCollector:
    """Collects attempts from a PuzzleEngine and aggregates metrics.

    Typical usage:
        engine = PuzzleEngine(registry)
        collector = DataCollector(engine)
        collector.run_sample_attempts(sample_inputs)
        report = collector.report()

    The collector intentionally stores lightweight summaries rather
    than raw large payloads so reports are compact.
    """

    def __init__(self, engine: PuzzleEngine):
        self.engine = engine
        self.attempts: List[AttemptRecord] = []
        self._puzzle_counters: Counter = Counter()

    def record(self, puzzle: str, answer: Any) -> AttemptRecord:
        """Run a single attempt against the engine and record the result.

        Parameters
        - puzzle: puzzle name from `registry`
        - answer: an arbitrary answer value; converted to string for display

        Returns the created AttemptRecord.
        """
        start = time.time()
        ok, message = self.engine.attempt(puzzle, answer)
        duration = self.engine.store.get(f"attempt:{puzzle}:duration", 0) or (time.time() - start)
        rec = AttemptRecord(
            puzzle=puzzle,
            answer=str(answer),
            ok=bool(ok),
            message=str(message),
            duration=float(duration),
            ts=start,
        )
        self.attempts.append(rec)
        self._puzzle_counters[puzzle] += 1
        return rec

    def run_sample_attempts(self, samples: Iterable[Tuple[str,Any]]) -> List[AttemptRecord]:
        """Run a sequence of (puzzle,answer) samples and return recorded attempts."""
        out = []
        for puzzle, ans in samples:
            if puzzle not in registry:
                # skip unknown puzzles gracefully
                continue
            out.append(self.record(puzzle, ans))
        return out

    def sample_from_registry(self, per_puzzle: int = 3) -> List[Tuple[str,Any]]:
        """Generate deterministic sample inputs for each registered puzzle.

        The generator uses a stable hash of the puzzle name to produce
        repeatable sample answers. This avoids randomness while still
        exercising a variety of inputs.
        """
        samples: List[Tuple[str,Any]] = []
        for name in sorted(registry.keys()):
            base = simple_hash(name, rounds=2)[:8]
            # create a few predictable answers derived from the name
            for i in range(per_puzzle):
                samples.append((name, f"{base}-{i}"))
        return samples

    def summarize(self) -> Dict[str,Any]:
        """Produce aggregated metrics about the collected attempts.

        Returns a dictionary suitable for JSON serialization.
        """
        by_puzzle: Dict[str, List[AttemptRecord]] = defaultdict(list)
        for a in self.attempts:
            by_puzzle[a.puzzle].append(a)

        puzzles_summary = {}
        for pname, recs in by_puzzle.items():
            durations = [r.duration for r in recs if r.duration is not None]
            messages = [r.message for r in recs]
            puzzles_summary[pname] = {
                "attempts": len(recs),
                "successes": sum(1 for r in recs if r.ok),
                "duration_mean": statistics.mean(durations) if durations else 0.0,
                "duration_p50": statistics.median(durations) if durations else 0.0,
                "common_messages": Counter(messages).most_common(3),
            }

        overall = {
            "total_attempts": len(self.attempts),
            "unique_puzzles": len(by_puzzle),
            "top_puzzles": self._puzzle_counters.most_common(10),
        }

        return {"overall": overall, "puzzles": puzzles_summary}

    def report(self, pretty: bool = True) -> str:
        """Return a JSON report string representing the summary.

        If `pretty` is True the JSON is indented for human reading.
        """
        s = self.summarize()
        if pretty:
            return json.dumps(s, indent=2)
        return json.dumps(s, separators=(",", ":"))


def ascii_bar(count: int, max_count: int, width: int = 40) -> str:
    """Return a small ASCII bar for text reports.

    This function scales `count` relative to `max_count` and emits a bar
    composed of `#` characters up to `width` characters.
    """
    if max_count <= 0:
        return ""
    filled = int((count / max_count) * width)
    return "#" * filled + "-" * (width - filled)


def text_report(summary: Dict[str,Any]) -> str:
    """Generate a compact human-readable text report from summary dict."""
    lines: List[str] = []
    overall = summary.get("overall", {})
    lines.append("Final-Trace Analytics Report")
    lines.append(f"Total attempts: {overall.get('total_attempts', 0)}")
    lines.append(f"Unique puzzles exercised: {overall.get('unique_puzzles', 0)}")
    top = overall.get("top_puzzles", [])
    if top:
        max_c = top[0][1]
        lines.append("")
        lines.append("Top puzzles by attempts:")
        for name, cnt in top:
            lines.append(f" - {name:20} {cnt:4} {ascii_bar(cnt, max_c)}")

    lines.append("")
    lines.append("Per-puzzle summary (name: attempts/success/mean-dur):")
    puzzles = summary.get("puzzles", {})
    for pname, pdata in sorted(puzzles.items(), key=lambda x: -x[1]["attempts"]):
        lines.append(
            f" - {pname:20} {pdata['attempts']:4}/{pdata['successes']:3}   mean={pdata['duration_mean']:.3f}s"
        )

    return "\n".join(lines)


def generate_detailed_inspection(attempts: List[AttemptRecord]) -> Dict[str,Any]:
    """Create a deeper inspection of attempt messages and textual features.

    This function applies a small fingerprint and entropy heuristic to
    message strings so a report can surface atypical or high-entropy
    outputs.
    """
    msg_stats: Dict[str, Dict[str, Any]] = {}
    for a in attempts:
        key = fingerprint_text(a.message)
        ent = textual_entropy(a.message)
        if key not in msg_stats:
            msg_stats[key] = {"examples": [], "count": 0, "max_entropy": 0.0}
        st = msg_stats[key]
        st["count"] += 1
        st["examples"].append(a.message)
        st["max_entropy"] = max(st["max_entropy"], ent)

    # Trim examples for compactness
    for v in msg_stats.values():
        if len(v["examples"]) > 3:
            v["examples"] = v["examples"][:3]
    return msg_stats


def main(argv: List[str] | None = None) -> int:
    """Command-line entry point for the analysis tool.

    Behavior:
    - Build an engine
    - Generate deterministic sample inputs
    - Run attempts
    - Print JSON and textual reports

    Returns an exit code integer.
    """
    # Build engine using package registry
    engine = PuzzleEngine(registry)
    collector = DataCollector(engine)

    samples = collector.sample_from_registry(per_puzzle=4)
    collector.run_sample_attempts(samples)

    summary = collector.summarize()
    print(text_report(summary))

    detailed = generate_detailed_inspection(collector.attempts)
    # Print concise JSON to stdout for tooling
    print("\nJSON Summary:\n")
    print(collector.report(pretty=True))
    print("\nMessage inspection (fingerprint -> stats):\n")
    print(json.dumps(detailed, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
