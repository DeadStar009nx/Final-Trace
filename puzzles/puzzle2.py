"""Puzzle 2: small crypto puzzle using XOR & base conversions."""
from .base import PuzzleBase
from .registry import register
import base64


@register("xor-echo")
class Puzzle2(PuzzleBase):
    """XOR the provided key with the challenge blob to reveal a phrase."""

    _blob_b64 = "SGVsbG8sIEV4cGVkaXRpb24gMzMh"

    def solve(self, answer):
        # Accept either hex key string or integer
        try:
            blob = base64.b64decode(self._blob_b64)
        except Exception:
            return False, "corrupt blob"

        key = None
        if isinstance(answer, str):
            s = answer.strip()
            # hex
            if all(c in '0123456789abcdefABCDEF' for c in s) and len(s) % 2 == 0:
                try:
                    key = bytes.fromhex(s)
                except Exception:
                    key = None
        elif isinstance(answer, (bytes, bytearray)):
            key = bytes(answer)

        if key is None:
            return False, "provide hex key"

        out = bytes(b ^ key[i % len(key)] for i, b in enumerate(blob))
        try:
            text = out.decode('utf-8')
        except Exception:
            text = repr(out)

        if "Expedition" in text or "Expedition".lower() in text.lower():
            return True, f"Revealed: {text}"
        return False, f"Revealed but not expected: {text}"
