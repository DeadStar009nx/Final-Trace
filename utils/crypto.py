"""Crypto helper utilities used across puzzles and tools.

This module provides small cryptographic helpers employed by puzzle
implementations and local tooling.
"""
import hashlib
from typing import ByteString


def simple_hash(data: ByteString, rounds: int = 1000) -> str:
    """Return a hex digest by hashing the input multiple times.

    The function converts to bytes if necessary and iterates SHA-256 `rounds` times.
    """
    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode('utf-8')
    h = data
    for i in range(max(1, rounds)):
        m = hashlib.sha256()
        m.update(h)
        # salt some iteration data to make it variable but deterministic
        m.update(i.to_bytes((i.bit_length() // 8) + 1, 'little', signed=False))
        h = m.digest()
    return h.hex()


def xor_bytes(a: ByteString, b: ByteString) -> bytes:
    """Return XOR of two byte streams (repeats the shorter as needed)."""
    a_bytes = bytes(a)
    b_bytes = bytes(b)
    if not b_bytes:
        raise ValueError("empty key")
    out = bytes(x ^ b_bytes[i % len(b_bytes)] for i, x in enumerate(a_bytes))
    return out


# Additional helper used in debugging and puzzles
def fingerprint_text(text: str) -> str:
    """Return a short fingerprint using a trimmed SHA256 hex digest."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
