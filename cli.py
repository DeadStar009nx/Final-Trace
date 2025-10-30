"""A small CLI to inspect and attempt puzzles from the command line."""
import argparse
import json
from core.engine import PuzzleEngine
from puzzles.registry import registry


def main(argv=None):
    parser = argparse.ArgumentParser(description="Final-Trace puzzle CLI")
    parser.add_argument("action", choices=["list", "describe", "solve"], help="action")
    parser.add_argument("puzzle", nargs="?", help="puzzle name")
    parser.add_argument("--answer", help="answer payload")
    args = parser.parse_args(argv)

    engine = PuzzleEngine(registry)

    if args.action == "list":
        for p in engine.list_puzzles():
            print(p)
        return 0

    if args.action == "describe":
        if not args.puzzle:
            print("provide puzzle name")
            return 2
        if args.puzzle not in registry:
            print("unknown puzzle")
            return 3
        print(json.dumps(registry[args.puzzle].describe(), indent=2))
        return 0

    if args.action == "solve":
        if not args.puzzle:
            print("provide puzzle name")
            return 2
        payload = args.answer
        # naive parsing: try int, then hex, else raw string
        parsed = payload
        if payload is None:
            parsed = None
        else:
            try:
                parsed = int(payload)
            except Exception:
                # try hex
                s = payload.strip()
                if all(c in '0123456789abcdefABCDEF' for c in s) and len(s) % 2 == 0:
                    try:
                        parsed = bytes.fromhex(s)
                    except Exception:
                        parsed = payload
                else:
                    parsed = payload

        ok, message = engine.attempt(args.puzzle, parsed)
        print({"ok": ok, "message": message})
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
