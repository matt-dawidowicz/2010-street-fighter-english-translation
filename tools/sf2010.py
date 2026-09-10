#!/usr/bin/env python3
"""Apply, verify, rebuild, and benchmark the Street Fighter 2010 v1.01 release."""

from __future__ import annotations

import argparse
import hashlib
import statistics
import struct
import time
import tracemalloc
from pathlib import Path

import bps

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATCH = ROOT / "release" / "2010_Street_Fighter_English_Translation_v1.01.bps"
BASELINE_PATCH = ROOT / "tools" / "data" / "v1.0-baseline.bps"

VERSION = "1.01"
SOURCE_SHA256 = "2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a"
BASE_SHA256 = "2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d"
TARGET_SHA256 = "66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55"
PATCH_SHA256 = "bcaea7f01e331b1027a98dda123b2f23834450a268d9b6611445ef36b12d79d7"

TEXT_BANK = 0x20010
TEXT_CPU = 0x8000
CORPUS_CLEAR_END = 0x2095E
PTR_ACTIVE = 0x152A0
PTR_COPY = 0x212A0
PTR_STRUCT = struct.Struct("<21H")
F7, F8, FA, FB, FC, FE, FF = 0xF7, 0xF8, 0xFA, 0xFB, 0xFC, 0xFE, 0xFF
ELLIPSIS = 0x88
_FE = bytes([FE])

_ENC = {chr(ord("A") + i): 0x0A + i for i in range(26)}
_ENC.update({str(i): i for i in range(10)})
_ENC.update({" ": 0x24, ".": 0x8E, ",": 0x8D, "-": 0x8F, "?": 0x89, "!": 0x8A, "'": FC})
_ENCODE_TRANSLATION = {i: "\u0100" for i in range(128)}
_ENCODE_TRANSLATION.update({ord(char): chr(value) for char, value in _ENC.items()})


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_supported_source(path: Path) -> bytes:
    source = path.read_bytes()
    digest = sha256(source)
    if digest != SOURCE_SHA256:
        raise SystemExit(f"unsupported source ROM: sha256={digest}")
    return source


def tile_width(text: str) -> int:
    return len(text) - 2 * text.count("...")


def encode_text(text: str) -> bytearray:
    try:
        encoded = text.replace("...", chr(ELLIPSIS)).translate(_ENCODE_TRANSLATION).encode("latin-1")
    except UnicodeEncodeError as exc:
        raise ValueError(f"unsupported dialogue character in {text!r}") from exc
    return bytearray(encoded)


def wrap_text(text: str, cap: int = 23) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
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


def encode_group(text: str, open_quote: bool = True, close_quote: bool = True) -> bytearray:
    lines = wrap_text(text)
    out = bytearray([F7]) if open_quote else bytearray()
    out += bytes([FE]).join(encode_text(line) for line in lines)
    if close_quote:
        out.append(F8)
    return out


def insert_scroll(raw: bytearray, pre_fe: int = 0) -> bytearray:
    if pre_fe + raw.count(FE) <= 5:
        return bytearray(raw)
    needed = 5 - pre_fe
    if needed <= 0:
        return bytearray([FA]) + raw
    pos = -1
    for _ in range(needed):
        pos = raw.find(_FE, pos + 1)
        if pos < 0:
            raise RuntimeError("could not locate required dialogue scroll boundary")
    return raw[: pos + 1] + bytes([FA]) + raw[pos + 1 :]


def build_record5() -> bytes:
    groups = (
        ("KEVIN...", True, True),
        ("YOU BASTARD!", True, True),
        (
            "GO TO DAGOBAH, THE DESERT PLANET. I'VE HIDDEN A FLIP SHIELD GENERATOR THERE. "
            "EQUIP IT, AND YOUR STRENGTH WILL COME ONE STEP CLOSER TO PERFECTION...",
            True,
            True,
        ),
    )
    separator = bytes([FE, FB, FE])
    raw = bytearray(separator.join(bytes(encode_group(*group)) for group in groups))
    raw = insert_scroll(raw)
    raw.append(FF)
    return bytes(raw)


def build_single(text: str, open_quote: bool = True, close_quote: bool = True) -> bytes:
    raw = insert_scroll(encode_group(text, open_quote, close_quote))
    raw.append(FF)
    return bytes(raw)


def _pointers(data: bytes, table: int = PTR_ACTIVE) -> tuple[int, ...]:
    return PTR_STRUCT.unpack_from(data, table)


def _record_bounds(data: bytes, ptrs: tuple[int, ...], index: int) -> tuple[int, int]:
    start = TEXT_BANK + (ptrs[index] - TEXT_CPU)
    end = data.index(FF, start, CORPUS_CLEAR_END) + 1
    return start, end


def _assert_renderer_invariants(data: bytes) -> None:
    if (data[0x17064], data[0x17263], data[0x1712D]) != (0xC4, 0xC4, 0xC5):
        raise RuntimeError("cursor/apostrophe renderer invariant changed")
    if data[0x171F8 : 0x171F8 + 12] != bytes.fromhex("a9 20 85 01 20 b7 b1 a9 01 85 73 60"):
        raise RuntimeError("post-scroll renderer invariant changed")


def _audit_target(base: bytes, target: bytes, base_ptrs: tuple[int, ...], target_ptrs: tuple[int, ...]) -> dict[str, int]:
    expected = bytearray(struct.pack("<21H", *base_ptrs))
    expected[10:12] = target_ptrs[5].to_bytes(2, "little")
    if target[PTR_ACTIVE : PTR_ACTIVE + PTR_STRUCT.size] != expected:
        raise RuntimeError("unexpected active pointer-table change")
    if target[PTR_COPY : PTR_COPY + PTR_STRUCT.size] != expected:
        raise RuntimeError("unexpected mirrored pointer-table change")

    r11_start, r11_end = _record_bounds(base, base_ptrs, 11)
    if target[r11_start:r11_end] != base[r11_start:r11_end]:
        raise RuntimeError("Record 11 changed unexpectedly")
    r11 = target[r11_start:r11_end]
    scroll = r11.index(FA)
    if r11[:scroll].count(FE) != 5:
        raise RuntimeError("Record 11 fifth-line scroll invariant failed")

    _assert_renderer_invariants(target)
    changed = sum(a != b for a, b in zip(base, target, strict=True))
    return {
        "changed_bytes": changed,
        "record5_old": _record_bounds(base, base_ptrs, 5)[0],
        "record5_new": _record_bounds(target, target_ptrs, 5)[0],
        "record5_cpu": target_ptrs[5],
    }


def build_release(source: bytes) -> tuple[bytes, bytes, dict[str, int]]:
    if sha256(source) != SOURCE_SHA256:
        raise RuntimeError("source SHA-256 does not match the supported Japanese ROM")

    base = bps.apply(source, BASELINE_PATCH.read_bytes())
    if sha256(base) != BASE_SHA256:
        raise RuntimeError("internal v1.0 baseline patch produced an unexpected ROM")

    ptrs = _pointers(base)
    if ptrs[:5] != (ptrs[0],) * 5:
        raise RuntimeError("unexpected aliased pointer layout")

    r5 = build_record5()
    r10 = build_single("THAT'S RIGHT. YOU ARE THE GREATEST PARASITE THAT I, DR. JOSE, HAVE CREATED.", True, False)
    r20 = build_single("KEVIN! I'LL TEST IT ON YOUR BODY!", True, True)

    o10, e10 = _record_bounds(base, ptrs, 10)
    o20, e20 = _record_bounds(base, ptrs, 20)
    if len(r10) > e10 - o10 or len(r20) > e20 - o20:
        raise RuntimeError("maintenance replacement no longer fits its reserved record allocation")

    live_end = max(_record_bounds(base, ptrs, index)[1] for index in (0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20))
    if any(base[live_end:CORPUS_CLEAR_END]):
        raise RuntimeError("expected unused packed-dialogue tail is not blank")
    if live_end + len(r5) > CORPUS_CLEAR_END:
        raise RuntimeError("Record 5 relocation would overflow packed-dialogue space")

    out = bytearray(base)
    out[o10:e10] = bytes(e10 - o10)
    out[o10 : o10 + len(r10)] = r10
    out[o20:e20] = bytes(e20 - o20)
    out[o20 : o20 + len(r20)] = r20
    out[live_end : live_end + len(r5)] = r5

    new5_cpu = TEXT_CPU + (live_end - TEXT_BANK)
    for table in (PTR_ACTIVE, PTR_COPY):
        out[table + 10 : table + 12] = new5_cpu.to_bytes(2, "little")

    target = bytes(out)
    target_ptrs = _pointers(target)
    audit = _audit_target(base, target, ptrs, target_ptrs)
    if sha256(target) != TARGET_SHA256:
        raise RuntimeError(f"unexpected v1.01 target SHA-256: {sha256(target)}")

    patch = bps.create(source, target)
    if sha256(patch) != PATCH_SHA256:
        raise RuntimeError(f"unexpected v1.01 BPS SHA-256: {sha256(patch)}")
    if bps.apply(source, patch) != target:
        raise RuntimeError("generated BPS failed clean-source round trip")
    return target, patch, audit


def verify_release(source: bytes, verbose: bool = False) -> bytes:
    patch = RELEASE_PATCH.read_bytes()
    if sha256(patch) != PATCH_SHA256:
        raise RuntimeError("release BPS SHA-256 mismatch")
    target = bps.apply(source, patch)
    if sha256(target) != TARGET_SHA256:
        raise RuntimeError("translated ROM SHA-256 mismatch")
    _assert_renderer_invariants(target)

    print("OK")
    print(f"version:       {VERSION}")
    print(f"source sha256: {SOURCE_SHA256}")
    print(f"target sha256: {TARGET_SHA256}")
    print(f"patch sha256:  {PATCH_SHA256}")
    if verbose:
        print(f"patch bytes:   {len(patch)}")
        print("renderer:      stable V12/RC9 cursor, apostrophe, and post-scroll invariants PASS")
        print("release BPS:   clean-source round trip PASS")
    return target


def _median_seconds(fn, runs: int) -> float:
    samples = []
    for _ in range(2):
        fn()
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def benchmark(source: bytes, apply_runs: int, create_runs: int) -> None:
    patch = RELEASE_PATCH.read_bytes()
    target = bps.apply(source, patch)
    if sha256(target) != TARGET_SHA256:
        raise RuntimeError("benchmark target hash mismatch")

    apply_time = _median_seconds(lambda: bps.apply(source, patch), apply_runs)

    def full_verify() -> None:
        rebuilt = bps.apply(source, patch)
        if sha256(rebuilt) != TARGET_SHA256:
            raise RuntimeError("verify benchmark hash mismatch")

    verify_time = _median_seconds(full_verify, apply_runs)
    create_time = _median_seconds(lambda: bps.create(source, target), create_runs)

    tracemalloc.start()
    generated = bps.create(source, target)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if generated != patch:
        raise RuntimeError("benchmark encoder no longer reproduces canonical v1.01 BPS")

    print("Street Fighter 2010 v1.01 benchmark")
    print(f"BPS apply median:       {apply_time * 1000:.3f} ms  ({apply_runs} runs)")
    print(f"release verify median:  {verify_time * 1000:.3f} ms  ({apply_runs} runs)")
    print(f"BPS create median:      {create_time * 1000:.3f} ms  ({create_runs} runs)")
    print(f"BPS create peak memory: {peak / (1024 * 1024):.3f} MiB")
    print(f"patch size:             {len(patch)} bytes")
    print("canonical BPS identity: PASS")
    print("target ROM identity:    PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_apply = sub.add_parser("apply", help="apply the canonical v1.01 BPS")
    p_apply.add_argument("source", type=Path)
    p_apply.add_argument("--output", type=Path, default=Path("2010_Street_Fighter_English_Translation_v1.01.nes"))

    p_verify = sub.add_parser("verify", help="verify the canonical release from a clean source ROM")
    p_verify.add_argument("source", type=Path)
    p_verify.add_argument("--verbose", action="store_true")

    p_rebuild = sub.add_parser("rebuild", help="rebuild v1.01 and its BPS from the internal v1.0 baseline")
    p_rebuild.add_argument("source", type=Path)
    p_rebuild.add_argument("--rom", type=Path, default=Path("2010_Street_Fighter_English_Translation_v1.01.nes"))
    p_rebuild.add_argument("--patch", type=Path, default=Path("2010_Street_Fighter_English_Translation_v1.01.bps"))

    p_bench = sub.add_parser("bench", help="benchmark BPS apply, verification, creation, and memory")
    p_bench.add_argument("source", type=Path)
    p_bench.add_argument("--apply-runs", type=int, default=51)
    p_bench.add_argument("--create-runs", type=int, default=3)

    args = parser.parse_args()
    source = _load_supported_source(args.source)

    if args.command == "apply":
        target = verify_release(source)
        args.output.write_bytes(target)
        print(f"wrote: {args.output}")
    elif args.command == "verify":
        verify_release(source, args.verbose)
    elif args.command == "rebuild":
        target, patch, audit = build_release(source)
        args.rom.write_bytes(target)
        args.patch.write_bytes(patch)
        print(f"ROM: {args.rom}  sha256={TARGET_SHA256}")
        print(f"BPS: {args.patch}  sha256={PATCH_SHA256}")
        print(f"release BPS identical: {patch == RELEASE_PATCH.read_bytes()}")
        print(
            "audit: changed_bytes={changed_bytes} record5=0x{record5_old:x}->0x{record5_new:x} cpu=0x{record5_cpu:04x}".format(
                **audit
            )
        )
    elif args.command == "bench":
        if args.apply_runs < 1 or args.create_runs < 1:
            raise SystemExit("benchmark run counts must be positive")
        benchmark(source, args.apply_runs, args.create_runs)


if __name__ == "__main__":
    main()
