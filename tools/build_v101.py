#!/usr/bin/env python3
"""Reproduce the v1.01 maintenance release from a clean Japanese ROM.

The builder first applies the retained v1.0 BPS patch, verifies the exact v1.0
ROM hash, then changes only Records 5, 10, and 20. Record 5 grows and is
relocated into unused packed-dialogue space; Records 10 and 20 remain in their
existing allocations. All unrelated pointers and the V10/V11/V12 renderer
fixes are asserted unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zlib

from apply_bps import apply_bps

ROOT = Path(__file__).resolve().parents[1]
BASE_PATCH = ROOT / "release" / "2010_Street_Fighter_English_Translation_v1.0.bps"
RELEASE_PATCH = ROOT / "release" / "2010_Street_Fighter_English_Translation_v1.01.bps"

SOURCE_SHA256 = "2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a"
BASE_SHA256 = "2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d"
TARGET_SHA256 = "66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55"
PATCH_SHA256 = "bcaea7f01e331b1027a98dda123b2f23834450a268d9b6611445ef36b12d79d7"

TEXT_BANK = 0x20010
TEXT_CPU = 0x8000
CORPUS_CLEAR_END = 0x2095E
PTR_ACTIVE = 0x152A0
PTR_COPY = 0x212A0
PTR_LEN = 42
F7 = 0xF7
F8 = 0xF8
FA = 0xFA
FB = 0xFB
FC = 0xFC
FE = 0xFE
FF = 0xFF
ELLIPSIS = 0x88

ENC = {chr(ord("A") + i): 0x0A + i for i in range(26)}
ENC.update({str(i): i for i in range(10)})
ENC.update({" ": 0x24, ".": 0x8E, ",": 0x8D, "-": 0x8F, "?": 0x89, "!": 0x8A})


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tile_width(text: str) -> int:
    width = 0
    i = 0
    while i < len(text):
        if text.startswith("...", i):
            width += 1
            i += 3
        else:
            width += 1
            i += 1
    return width


def encode_text(text: str) -> bytearray:
    out = bytearray()
    i = 0
    while i < len(text):
        if text.startswith("...", i):
            out.append(ELLIPSIS)
            i += 3
            continue
        c = text[i]
        if c == "'":
            out.append(FC)
        else:
            out.append(ENC[c])
        i += 1
    return out


def wrap_text(text: str, cap: int = 23) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if tile_width(candidate) <= cap:
            current = candidate
        else:
            if not current or tile_width(word) > cap:
                raise RuntimeError(f"cannot wrap safely: {word!r}")
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) == 1 and tile_width(lines[0]) + 2 > 24:
        return wrap_text(text, 22)
    return lines


def encode_group(text: str, open_quote: bool = True, close_quote: bool = True) -> tuple[bytearray, list[str]]:
    lines = wrap_text(text)
    out = bytearray([F7]) if open_quote else bytearray()
    for i, line in enumerate(lines):
        out += encode_text(line)
        if i + 1 < len(lines):
            out.append(FE)
    if close_quote:
        out.append(F8)
    return out, lines


def insert_scroll(raw: bytearray, pre_fe: int = 0) -> bytearray:
    if pre_fe + raw.count(FE) <= 5:
        return bytearray(raw)
    out = bytearray()
    count = pre_fe
    inserted = False
    for value in raw:
        out.append(value)
        if value == FE:
            count += 1
            if count == 5:
                out.append(FA)
                inserted = True
    if not inserted:
        out = bytearray([FA]) + out
    return out


def build_record5() -> bytes:
    groups = [
        ("KEVIN...", True, True),
        ("YOU BASTARD!", True, True),
        (
            "GO TO DAGOBAH, THE DESERT PLANET. I'VE HIDDEN A FLIP SHIELD GENERATOR THERE. "
            "EQUIP IT, AND YOUR STRENGTH WILL COME ONE STEP CLOSER TO PERFECTION...",
            True,
            True,
        ),
    ]
    raw = bytearray()
    for i, (text, open_quote, close_quote) in enumerate(groups):
        group, _ = encode_group(text, open_quote, close_quote)
        raw += group
        if i + 1 < len(groups):
            raw += bytes([FE, FB, FE])
    raw = insert_scroll(raw)
    raw.append(FF)
    return bytes(raw)


def build_single(text: str, open_quote: bool = True, close_quote: bool = True) -> bytes:
    raw, _ = encode_group(text, open_quote, close_quote)
    raw = insert_scroll(raw)
    raw.append(FF)
    return bytes(raw)


def bps_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        x = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(x | 0x80)
            return bytes(out)
        out.append(x)
        value -= 1


def signed_varint(delta: int) -> bytes:
    return bps_varint((abs(delta) << 1) | (1 if delta < 0 else 0))


def make_bps(source: bytes, target: bytes) -> bytes:
    """Create a deterministic compact BPS using source and target copies."""
    anchor_len = 8
    source_index: dict[bytes, list[int]] = {}
    for pos in range(len(source) - anchor_len + 1):
        source_index.setdefault(source[pos : pos + anchor_len], []).append(pos)
    for key, positions in list(source_index.items()):
        if len(positions) > 64:
            source_index[key] = positions[:32] + positions[-32:]

    patch = bytearray(b"BPS1")
    patch += bps_varint(len(source))
    patch += bps_varint(len(target))
    patch += bps_varint(0)

    target_index: dict[bytes, list[int]] = {}
    indexed_until = 0
    i = 0
    source_relative = 0
    target_relative = 0

    def add_target_until(limit: int) -> None:
        nonlocal indexed_until
        end = min(limit, len(target) - anchor_len + 1)
        while indexed_until < end:
            key = target[indexed_until : indexed_until + anchor_len]
            bucket = target_index.setdefault(key, [])
            if len(bucket) < 64:
                bucket.append(indexed_until)
            indexed_until += 1

    def longest(ref: bytes, target_pos: int, ref_pos: int, max_len: int | None = None) -> int:
        match_len = 0
        limit = min(len(target) - target_pos, len(ref) - ref_pos)
        if max_len is not None:
            limit = min(limit, max_len)
        while match_len < limit and target[target_pos + match_len] == ref[ref_pos + match_len]:
            match_len += 1
        return match_len

    while i < len(target):
        add_target_until(max(0, i - anchor_len + 1))

        if i < len(source) and target[i] == source[i]:
            j = i + 1
            while j < len(target) and j < len(source) and target[j] == source[j]:
                j += 1
            patch += bps_varint(((j - i - 1) << 2) | 0)
            i = j
            continue

        best_type = "none"
        best_len = 0
        best_pos: int | None = None
        if i + anchor_len <= len(target):
            key = target[i : i + anchor_len]
            for source_pos in source_index.get(key, []):
                match_len = longest(source, i, source_pos)
                if match_len > best_len:
                    best_type, best_len, best_pos = "source", match_len, source_pos
            for target_pos in target_index.get(key, []):
                match_len = longest(target, i, target_pos)
                if match_len > best_len:
                    best_type, best_len, best_pos = "target", match_len, target_pos

        if best_len >= 12 and best_pos is not None:
            if best_type == "source":
                patch += bps_varint(((best_len - 1) << 2) | 2)
                patch += signed_varint(best_pos - source_relative)
                source_relative = best_pos + best_len
            else:
                patch += bps_varint(((best_len - 1) << 2) | 3)
                patch += signed_varint(best_pos - target_relative)
                target_relative = best_pos + best_len
            i += best_len
            continue

        j = i + 1
        while j < len(target):
            add_target_until(max(0, j - anchor_len + 1))
            if j < len(source) and target[j] == source[j]:
                break
            useful_copy = False
            if j + anchor_len <= len(target):
                key = target[j : j + anchor_len]
                for source_pos in source_index.get(key, [])[:16]:
                    if longest(source, j, source_pos, 12) >= 12:
                        useful_copy = True
                        break
                if not useful_copy:
                    for target_pos in target_index.get(key, [])[:16]:
                        if longest(target, j, target_pos, 12) >= 12:
                            useful_copy = True
                            break
            if useful_copy:
                break
            j += 1

        patch += bps_varint(((j - i - 1) << 2) | 1)
        patch += target[i:j]
        i = j

    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch).to_bytes(4, "little")
    return bytes(patch)


def build(source: bytes) -> tuple[bytes, bytes]:
    if sha256(source) != SOURCE_SHA256:
        raise RuntimeError("source SHA-256 does not match the supported Japanese ROM")

    base = apply_bps(source, BASE_PATCH.read_bytes())
    if sha256(base) != BASE_SHA256:
        raise RuntimeError("retained v1.0 baseline patch produced an unexpected ROM")

    ptrs = [int.from_bytes(base[PTR_ACTIVE + i : PTR_ACTIVE + i + 2], "little") for i in range(0, PTR_LEN, 2)]
    if ptrs[:5] != [ptrs[0]] * 5:
        raise RuntimeError("unexpected aliased pointer layout")

    def record_bounds(index: int) -> tuple[int, int]:
        start = TEXT_BANK + (ptrs[index] - TEXT_CPU)
        end = base.index(FF, start, CORPUS_CLEAR_END) + 1
        return start, end

    r5 = build_record5()
    r10 = build_single("THAT'S RIGHT. YOU ARE THE GREATEST PARASITE THAT I, DR. JOSE, HAVE CREATED.", True, False)
    r20 = build_single("KEVIN! I'LL TEST IT ON YOUR BODY!", True, True)

    o10, e10 = record_bounds(10)
    o20, e20 = record_bounds(20)
    if len(r10) > e10 - o10 or len(r20) > e20 - o20:
        raise RuntimeError("maintenance replacement no longer fits its reserved record allocation")

    live_end = max(record_bounds(i)[1] for i in [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    if any(base[live_end:CORPUS_CLEAR_END]):
        raise RuntimeError("expected unused packed-dialogue tail is not blank")
    if live_end + len(r5) > CORPUS_CLEAR_END:
        raise RuntimeError("Record 5 relocation would overflow packed-dialogue space")

    out = bytearray(base)
    out[o10:e10] = bytes(e10 - o10)
    out[o10 : o10 + len(r10)] = r10
    out[o20:e20] = bytes(e20 - o20)
    out[o20 : o20 + len(r20)] = r20

    new5_cpu = TEXT_CPU + (live_end - TEXT_BANK)
    out[live_end : live_end + len(r5)] = r5
    for table in (PTR_ACTIVE, PTR_COPY):
        out[table + 10 : table + 12] = new5_cpu.to_bytes(2, "little")

    for index in range(21):
        if index == 5:
            continue
        for table in (PTR_ACTIVE, PTR_COPY):
            if out[table + index * 2 : table + index * 2 + 2] != base[table + index * 2 : table + index * 2 + 2]:
                raise RuntimeError(f"unexpected pointer change for Record {index}")

    # Stable v1.0 renderer invariants.
    if not (out[0x17064] == 0xC4 and out[0x17263] == 0xC4 and out[0x1712D] == 0xC5):
        raise RuntimeError("v1.0 cursor/apostrophe renderer invariant changed")
    if bytes(out[0x171F8 : 0x171F8 + 12]) != bytes.fromhex("a9 20 85 01 20 b7 b1 a9 01 85 73 60"):
        raise RuntimeError("v1.0 post-scroll renderer invariant changed")

    r11_start, r11_end = record_bounds(11)
    if out[r11_start:r11_end] != base[r11_start:r11_end]:
        raise RuntimeError("Record 11 changed unexpectedly")
    r11 = bytes(out[r11_start:r11_end])
    if r11[: r11.index(FA)].count(FE) != 5:
        raise RuntimeError("Record 11 fifth-line scroll invariant failed")

    target = bytes(out)
    if sha256(target) != TARGET_SHA256:
        raise RuntimeError(f"unexpected v1.01 target SHA-256: {sha256(target)}")

    patch = make_bps(source, target)
    if sha256(patch) != PATCH_SHA256:
        raise RuntimeError(f"unexpected v1.01 BPS SHA-256: {sha256(patch)}")
    if apply_bps(source, patch) != target:
        raise RuntimeError("generated BPS failed clean-source round trip")
    return target, patch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="clean supported Japanese ROM")
    parser.add_argument(
        "--rom",
        type=Path,
        default=Path("2010_Street_Fighter_English_Translation_v1.01.nes"),
        help="output translated ROM path",
    )
    parser.add_argument(
        "--patch",
        type=Path,
        default=Path("2010_Street_Fighter_English_Translation_v1.01.bps"),
        help="output BPS path",
    )
    args = parser.parse_args()

    target, patch = build(args.source.read_bytes())
    args.rom.write_bytes(target)
    args.patch.write_bytes(patch)

    print(f"ROM:   {args.rom}  sha256={sha256(target)}")
    print(f"BPS:   {args.patch}  sha256={sha256(patch)}")
    if RELEASE_PATCH.exists():
        print(f"repo release patch identical: {RELEASE_PATCH.read_bytes() == patch}")


if __name__ == "__main__":
    main()
