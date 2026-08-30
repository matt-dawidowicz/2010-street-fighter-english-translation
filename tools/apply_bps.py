#!/usr/bin/env python3
"""Small dependency-free BPS patch applier used to verify/apply release v1.0."""

from __future__ import annotations

import argparse
import binascii
import struct
from pathlib import Path


def decode_number(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    shift = 1
    while True:
        x = data[pos]
        pos += 1
        value += (x & 0x7F) * shift
        if x & 0x80:
            return value, pos
        shift <<= 7
        value += shift


def decode_signed(data: bytes, pos: int) -> tuple[int, int]:
    value, pos = decode_number(data, pos)
    negative = value & 1
    value >>= 1
    return (-value if negative else value), pos


def apply_bps(source: bytes, patch: bytes) -> bytes:
    if patch[:4] != b"BPS1":
        raise ValueError("not a BPS patch")
    if len(patch) < 16:
        raise ValueError("truncated BPS patch")

    body_end = len(patch) - 12
    source_crc, target_crc, patch_crc = struct.unpack("<III", patch[-12:])
    if binascii.crc32(source) & 0xFFFFFFFF != source_crc:
        raise ValueError("source ROM CRC32 does not match patch")
    if binascii.crc32(patch[:-4]) & 0xFFFFFFFF != patch_crc:
        raise ValueError("BPS patch CRC32 mismatch")

    pos = 4
    source_size, pos = decode_number(patch, pos)
    target_size, pos = decode_number(patch, pos)
    metadata_size, pos = decode_number(patch, pos)
    pos += metadata_size
    if source_size != len(source):
        raise ValueError(f"source size mismatch: expected {source_size}, got {len(source)}")

    target = bytearray()
    source_relative = 0
    target_relative = 0

    while len(target) < target_size:
        if pos >= body_end:
            raise ValueError("truncated BPS action stream")
        command, pos = decode_number(patch, pos)
        action = command & 3
        length = (command >> 2) + 1

        if action == 0:
            start = len(target)
            target += source[start : start + length]
        elif action == 1:
            target += patch[pos : pos + length]
            pos += length
        elif action == 2:
            delta, pos = decode_signed(patch, pos)
            source_relative += delta
            target += source[source_relative : source_relative + length]
            source_relative += length
        else:
            delta, pos = decode_signed(patch, pos)
            target_relative += delta
            for _ in range(length):
                target.append(target[target_relative])
                target_relative += 1

    if len(target) != target_size:
        raise ValueError("BPS produced wrong target size")
    if binascii.crc32(target) & 0xFFFFFFFF != target_crc:
        raise ValueError("target CRC32 mismatch")
    return bytes(target)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("patch", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    args.output.write_bytes(apply_bps(args.source.read_bytes(), args.patch.read_bytes()))


if __name__ == "__main__":
    main()
