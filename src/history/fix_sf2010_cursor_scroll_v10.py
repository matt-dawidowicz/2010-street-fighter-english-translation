#!/usr/bin/env python3
"""Reproduce the V10/RC7 cursor restoration and Record 11 scroll fix.

This script reconstructs the small late-stage patch from the exact byte-level
changes validated during playtesting. It expects either DEBUG V9 or normal RC6
as input and writes the corresponding next-stage ROM.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROM_SIZE = 393232
CURSOR_IMMEDIATES = (0x17064, 0x17263)
RECORD11_SCROLL_WINDOW = (0x20301, 0x20343)  # end-exclusive
FA = 0xFA
FE = 0xFE


def patch(data: bytes, restore_cursor: bool) -> bytes:
    if len(data) != ROM_SIZE:
        raise ValueError(f"unexpected ROM size: {len(data)}")
    out = bytearray(data)

    if restore_cursor:
        # DEBUG V9 had the cursor intentionally blanked ($24). Restore stock $C4.
        for off in CURSOR_IMMEDIATES:
            if out[off] not in (0x24, 0xC4):
                raise ValueError(f"unexpected cursor byte at {off:#x}: {out[off]:#x}")
            out[off] = 0xC4
    else:
        # Normal RC6 already contains the restored cursor.
        for off in CURSOR_IMMEDIATES:
            if out[off] != 0xC4:
                raise ValueError(f"expected restored cursor at {off:#x}")

    start, end = RECORD11_SCROLL_WINDOW
    window = bytes(out[start:end])
    if not window or window[0] != FA or window[-1] != FE:
        raise ValueError("Record 11 scroll window does not match the V9/RC6 layout")

    # V9 counted Record 10's line advances when deciding where to insert FA in
    # Record 11. Move FA from the beginning of this window to after Record 11's
    # fifth FE instead, preserving the record length and all other bytes.
    out[start:end] = window[1:] + bytes([FA])
    return bytes(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument(
        "--normal",
        action="store_true",
        help="input is normal RC6 (cursor already restored); default is DEBUG V9",
    )
    args = ap.parse_args()
    result = patch(args.input.read_bytes(), restore_cursor=not args.normal)
    args.output.write_bytes(result)


if __name__ == "__main__":
    main()
