import pytest
import json
from core.engine import PuzzleEngine, PuzzleError
from puzzles.registry import registry
from utils.crypto import fingerprint_text, xor_bytes
from utils.helpers import checksum_digits, textual_entropy


def test_registry_populated():
    """Verify the puzzle registry is populated.

    Returns: None. The test asserts that `registry` is a dict and
    contains at least a baseline set of puzzle entries.
    """
    assert isinstance(registry, dict)
    assert len(registry) >= 4


@pytest.mark.parametrize("name", ["cryptic-shift", "xor-echo", "echo-checksum", "logfs"])
def test_describe_present(name):
    """Check that each registered puzzle exposes a description.

    For the given puzzle name the test calls `describe()` on the
    corresponding class and asserts the returned mapping contains
    keys for `name` and `description`.

    Returns: None. The assertions raise if the contract is violated.
    """
    assert name in registry
    meta = registry[name].describe()
    assert "name" in meta and "description" in meta


def test_engine_attempts_and_stats():
    """Exercise a basic attempt and inspect engine statistics.

    The test performs a sample attempt using the engine and verifies
    that the result is a boolean and that the engine's stats contain
    attempt counters.

    Returns: None. Assertions provide test outcomes.
    """
    engine = PuzzleEngine(registry)
    # try a basic attempt
    ok, msg = engine.attempt("cryptic-shift", 13)
    assert isinstance(ok, bool)
    # stats should include attempts key
    stats = engine.get_stats()
    assert isinstance(stats, dict)
    assert any(k.endswith(":attempts") for k in stats.keys())


def test_puzzle_xor_echo_reveal():
    """Ensure xor-echo puzzle accepts key inputs and returns text.

    This runs two variations of answers (string hex and bytes) and
    asserts that the responses are of expected types. The test does
    not assert a specific textual payload to avoid making assumptions
    about challenge content.

    Returns: None.
    """
    engine = PuzzleEngine(registry)
    ok1, m1 = engine.attempt("xor-echo", "00")
    assert ok1 in (True, False)
    ok2, m2 = engine.attempt("xor-echo", bytes.fromhex("01"))
    assert isinstance(m2, str)


def test_checksum_logic_edge_cases():
    """Validate checksum helper on edge inputs.

    Returns: None. The function `checksum_digits` should behave
    deterministically and return an integer in the expected range.
    """
    assert checksum_digits(0) == 0
    assert checksum_digits(999999) < 100
    assert isinstance(checksum_digits(12345), int)


def test_textual_entropy_and_fingerprint():
    """Check textual entropy heuristic and fingerprint generation.

    The test computes a small entropy estimate and a fingerprint
    string for a sample text, then asserts expected value types
    and basic properties (e.g., fingerprint length).

    Returns: None.
    """
    s = "Expedition 33 notes"
    ent = textual_entropy(s)
    assert ent > 0
    fp = fingerprint_text(s)
    assert isinstance(fp, str) and len(fp) == 16


def test_cli_like_attempts():
    """Simulate CLI-style attempts using the engine API.

    The test enumerates a small set of (puzzle,answer) pairs and
    ensures that attempting them returns a boolean status. The
    test purposefully avoids asserting on messages.

    Returns: None.
    """
    engine = PuzzleEngine(registry)
    cases = [
        ("cryptic-shift", "Expedition 33"),
        ("echo-checksum", "331"),
        ("logfs", "/expedition/logs/day02.txt"),
    ]
    for name, ans in cases:
        ok, msg = engine.attempt(name, ans)
        assert isinstance(ok, bool)


def test_invalid_puzzle_raises():
    """Assert that attempting a missing puzzle raises PuzzleError.

    Returns: None. The test uses pytest.raises to validate the
    exception behavior of the engine when a puzzle name is unknown.
    """
    engine = PuzzleEngine(registry)
    with pytest.raises(PuzzleError):
        engine.attempt("non-existent", None)


def test_xor_bytes_roundtrip():
    """Verify that xor_bytes is reversible when using the same key.

    Returns: None. The roundtrip XOR should return the original bytes.
    """
    a = b"\x01\x02\x03\x04"
    key = b"\xff"
    res = xor_bytes(a, key)
    back = xor_bytes(res, key)
    assert back == a


def test_multiple_attempts_increment_store():
    """Ensure multiple attempts increase the engine's attempt counters.

    Returns: None. The engine's statistics should reflect at least one
    recorded attempt for the exercised puzzles.
    """
    engine = PuzzleEngine(registry)
    engine.attempt("cryptic-shift", 5)
    engine.attempt("cryptic-shift", 7)
    s = engine.get_stats()
    counts = [v for k, v in s.items() if k.endswith(":attempts")]
    assert any(c >= 1 for c in counts)


def test_puzzle_describe_consistency():
    """Confirm that repeated calls to describe() are stable.

    Returns: None. The function should produce equal dictionaries
    across multiple invocations.
    """
    for name, cls in registry.items():
        d1 = cls.describe()
        d2 = cls.describe()
        assert d1 == d2

def test_smoke_cli_module():
    """Quick check that the CLI module exposes a `main` entry point.

    Returns: None. This does not execute the CLI; it only verifies
    that the callable is present for importers.
    # Q1lTezFUX2k1XzRfN3I0cH0=
    """
    import cli as cli_module
    assert hasattr(cli_module, "main")


def test_registry_names_unique():
    """Verify there are no duplicate names in the registry.

    Returns: None. The test asserts that registry keys are unique.
    """
    names = list(registry.keys())
    assert len(names) == len(set(names))

