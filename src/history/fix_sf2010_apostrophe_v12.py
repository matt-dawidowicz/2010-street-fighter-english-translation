#!/usr/bin/env python3
"""Reproduce the V12/RC9 apostrophe glyph fix used by release v1.0.

V11/RC8 temporarily pointed the $FC apostrophe handler at tile $D0, which is a
colored graphics fragment in the live CHR context. V12/RC9 instead reserves
blank tile $C5 and draws a white upper-right apostrophe into it. The renderer
continues to advance by one full tile; this is the small cosmetic spacing quirk
accepted for v1.0.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROM_SIZE = 393232
APOSTROPHE_TILE_IMMEDIATE = 0x1712D
APOSTROPHE_TILE = 0xC5
# Six nonzero CHR bytes make the tiny white mark in both bitplanes.
CHR_PATCHES = {
    0x5CC65: bytes.fromhex("06 02 04"),
    0x5CC6D: bytes.fromhex("06 02 04"),
}


def patch(data: bytes) -> bytes:
    if len(data) != ROM_SIZE:
        raise ValueError(f"unexpected ROM size: {len(data)}")
    out = bytearray(data)

    if out[APOSTROPHE_TILE_IMMEDIATE] != 0xD0:
        raise ValueError(
            f"expected V11/RC8 apostrophe immediate $D0 at "
            f"{APOSTROPHE_TILE_IMMEDIATE:#x}"
        )
    out[APOSTROPHE_TILE_IMMEDIATE] = APOSTROPHE_TILE

    for off, replacement in CHR_PATCHES.items():
        current = bytes(out[off : off + len(replacement)])
        if current != b"\x00" * len(replacement):
            raise ValueError(f"expected blank CHR bytes at {off:#x}, got {current.hex()}")
        out[off : off + len(replacement)] = replacement

    return bytes(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="DEBUG V11 or normal RC8 ROM")
    ap.add_argument("output", type=Path, help="DEBUG V12 or normal RC9 ROM")
    args = ap.parse_args()
    args.output.write_bytes(patch(args.input.read_bytes()))


if __name__ == "__main__":
    main()
