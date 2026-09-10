#!/usr/bin/env python3
"""Minimal dependency-free BPS codec used by the Street Fighter 2010 tools."""

from __future__ import annotations

import binascii
import struct

_MAGIC = b"BPS1"
_ANCHOR_LEN = 8
_MIN_COPY = 12


def _decode_number(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    shift = 1
    while True:
        if pos >= len(data):
            raise ValueError("truncated BPS varint")
        x = data[pos]
        pos += 1
        value += (x & 0x7F) * shift
        if x & 0x80:
            return value, pos
        shift <<= 7
        value += shift


def _decode_signed(data: bytes, pos: int) -> tuple[int, int]:
    value, pos = _decode_number(data, pos)
    return (-(value >> 1) if value & 1 else value >> 1), pos


def _encode_number(value: int) -> bytes:
    if value < 0:
        raise ValueError("BPS varints cannot encode negative values")
    out = bytearray()
    while True:
        x = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(x | 0x80)
            return bytes(out)
        out.append(x)
        value -= 1


def _encode_signed(delta: int) -> bytes:
    return _encode_number((abs(delta) << 1) | (delta < 0))


def apply(source: bytes, patch: bytes) -> bytes:
    """Apply a BPS patch and validate source, patch, and target CRC32 values."""
    if patch[:4] != _MAGIC:
        raise ValueError("not a BPS patch")
    if len(patch) < 16:
        raise ValueError("truncated BPS patch")

    body_end = len(patch) - 12
    source_crc, target_crc, patch_crc = struct.unpack_from("<III", patch, body_end)
    if binascii.crc32(source) & 0xFFFFFFFF != source_crc:
        raise ValueError("source ROM CRC32 does not match patch")
    if binascii.crc32(patch[:-4]) & 0xFFFFFFFF != patch_crc:
        raise ValueError("BPS patch CRC32 mismatch")

    pos = 4
    source_size, pos = _decode_number(patch, pos)
    target_size, pos = _decode_number(patch, pos)
    metadata_size, pos = _decode_number(patch, pos)
    if pos + metadata_size > body_end:
        raise ValueError("truncated BPS metadata")
    pos += metadata_size
    if source_size != len(source):
        raise ValueError(f"source size mismatch: expected {source_size}, got {len(source)}")

    target = bytearray()
    source_relative = 0
    target_relative = 0

    while len(target) < target_size:
        if pos >= body_end:
            raise ValueError("truncated BPS action stream")
        command, pos = _decode_number(patch, pos)
        action = command & 3
        length = (command >> 2) + 1

        if action == 0:
            start = len(target)
            end = start + length
            if end > len(source):
                raise ValueError("SourceRead exceeds source")
            target += source[start:end]
        elif action == 1:
            end = pos + length
            if end > body_end:
                raise ValueError("TargetRead exceeds patch body")
            target += patch[pos:end]
            pos = end
        elif action == 2:
            delta, pos = _decode_signed(patch, pos)
            source_relative += delta
            end = source_relative + length
            if source_relative < 0 or end > len(source):
                raise ValueError("SourceCopy exceeds source")
            target += source[source_relative:end]
            source_relative = end
        else:
            delta, pos = _decode_signed(patch, pos)
            target_relative += delta
            available = len(target) - target_relative
            if target_relative < 0 or available <= 0:
                raise ValueError("TargetCopy references unavailable target data")
            if length <= available:
                target += target[target_relative : target_relative + length]
            else:
                seed = bytes(target[target_relative:])
                repeats, remainder = divmod(length, len(seed))
                target += seed * repeats + seed[:remainder]
            target_relative += length

        if len(target) > target_size:
            raise ValueError("BPS produced more data than declared target size")

    if len(target) != target_size:
        raise ValueError("BPS produced wrong target size")
    if binascii.crc32(target) & 0xFFFFFFFF != target_crc:
        raise ValueError("target CRC32 mismatch")
    return bytes(target)


def _source_positions(source: bytes, key: bytes, cache: dict[bytes, tuple[int, ...]]) -> tuple[int, ...]:
    """Match the reference encoder's first-32/last-32 cap without a full-ROM index."""
    cached = cache.get(key)
    if cached is not None:
        return cached

    first: list[int] = []
    pos = source.find(key)
    while pos >= 0 and len(first) < 65:
        first.append(pos)
        pos = source.find(key, pos + 1)

    if len(first) <= 64 and pos < 0:
        result = tuple(first)
    else:
        last: list[int] = []
        pos = source.rfind(key)
        while pos >= 0 and len(last) < 32:
            last.append(pos)
            pos = source.rfind(key, 0, pos)
        result = tuple(first[:32] + list(reversed(last)))

    cache[key] = result
    return result


def _target_positions(target: bytes, key: bytes, end: int) -> tuple[int, ...]:
    """Return up to the first 64 eligible prior target anchors."""
    positions: list[int] = []
    search_end = min(len(target), end + len(key) - 1)
    pos = target.find(key, 0, search_end)
    while pos >= 0 and len(positions) < 64:
        positions.append(pos)
        pos = target.find(key, pos + 1, search_end)
    return tuple(positions)


def _common_prefix(ref: bytes, target: bytes, target_pos: int, ref_pos: int, max_len: int | None = None) -> int:
    limit = min(len(target) - target_pos, len(ref) - ref_pos)
    if max_len is not None:
        limit = min(limit, max_len)
    n = 0
    while n < limit and target[target_pos + n] == ref[ref_pos + n]:
        n += 1
    return n


def create(source: bytes, target: bytes) -> bytes:
    """Create a deterministic compact BPS patch without a full-ROM source index."""
    patch = bytearray(_MAGIC)
    patch += _encode_number(len(source))
    patch += _encode_number(len(target))
    patch += _encode_number(0)

    source_cache: dict[bytes, tuple[int, ...]] = {}
    i = 0
    source_relative = 0
    target_relative = 0

    while i < len(target):
        if i < len(source) and target[i] == source[i]:
            mismatch = i + 1
            limit = min(len(source), len(target))
            while mismatch < limit and target[mismatch] == source[mismatch]:
                mismatch += 1
            patch += _encode_number(((mismatch - i - 1) << 2) | 0)
            i = mismatch
            continue

        best_type = 0
        best_len = 0
        best_pos = -1
        if i + _ANCHOR_LEN <= len(target):
            key = target[i : i + _ANCHOR_LEN]
            for source_pos in _source_positions(source, key, source_cache):
                match_len = _common_prefix(source, target, i, source_pos)
                if match_len > best_len:
                    best_type, best_len, best_pos = 2, match_len, source_pos

            eligible_end = max(0, i - _ANCHOR_LEN + 1)
            for target_pos in _target_positions(target, key, eligible_end):
                match_len = _common_prefix(target, target, i, target_pos)
                if match_len > best_len:
                    best_type, best_len, best_pos = 3, match_len, target_pos

        if best_len >= _MIN_COPY:
            patch += _encode_number(((best_len - 1) << 2) | best_type)
            if best_type == 2:
                patch += _encode_signed(best_pos - source_relative)
                source_relative = best_pos + best_len
            else:
                patch += _encode_signed(best_pos - target_relative)
                target_relative = best_pos + best_len
            i += best_len
            continue

        literal_end = i + 1
        while literal_end < len(target):
            if literal_end < len(source) and target[literal_end] == source[literal_end]:
                break
            useful_copy = False
            if literal_end + _ANCHOR_LEN <= len(target):
                key = target[literal_end : literal_end + _ANCHOR_LEN]
                for source_pos in _source_positions(source, key, source_cache)[:16]:
                    if _common_prefix(source, target, literal_end, source_pos, _MIN_COPY) >= _MIN_COPY:
                        useful_copy = True
                        break
                if not useful_copy:
                    eligible_end = max(0, literal_end - _ANCHOR_LEN + 1)
                    for target_pos in _target_positions(target, key, eligible_end)[:16]:
                        if _common_prefix(target, target, literal_end, target_pos, _MIN_COPY) >= _MIN_COPY:
                            useful_copy = True
                            break
            if useful_copy:
                break
            literal_end += 1

        patch += _encode_number(((literal_end - i - 1) << 2) | 1)
        patch += target[i:literal_end]
        i = literal_end

    patch += binascii.crc32(source).to_bytes(4, "little")
    patch += binascii.crc32(target).to_bytes(4, "little")
    patch += binascii.crc32(patch).to_bytes(4, "little")
    return bytes(patch)
