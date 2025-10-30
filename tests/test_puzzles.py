from puzzles.registry import registry


def test_registry_has_default_puzzles():
    assert isinstance(registry, dict)
    # Expect at least the four puzzles registered
    for name in ["cryptic-shift", "xor-echo", "echo-checksum", "logfs"]:
        assert name in registry
