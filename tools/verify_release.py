#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

from apply_bps import apply_bps

SOURCE_SHA256 = "2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a"
TARGET_SHA256 = "2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d"
PATCH = Path(__file__).resolve().parents[1] / "release" / "2010_Street_Fighter_English_Translation_v1.0.bps"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_release.py <clean-japanese-rom.nes>")
    source = Path(sys.argv[1]).read_bytes()
    if sha256(source) != SOURCE_SHA256:
        raise SystemExit("source SHA-256 does not match the supported Japanese ROM")
    target = apply_bps(source, PATCH.read_bytes())
    digest = sha256(target)
    if digest != TARGET_SHA256:
        raise SystemExit(f"target SHA-256 mismatch: {digest}")
    print("OK")
    print(f"source sha256: {SOURCE_SHA256}")
    print(f"target sha256: {TARGET_SHA256}")


if __name__ == "__main__":
    main()
