# 2010 Street Fighter — Faithful English Retranslation

A faithful English translation of the original Japanese Famicom version of **2010 Street Fighter**.

The North American release substantially rewrote the story to connect it more directly to the Street Fighter series. This project preserves the Japanese continuity instead: **Kevin Striker**, the **Parasites**, **Armored Insects**, the **Galaxy Police**, and the original terminology and plot structure.

The current release is **v1.01**. It is the source-audited maintenance build that corrects three dialogue lines while retaining the stable v1.0 renderer and gameplay behavior.

## Release

Patch:

```text
release/2010_Street_Fighter_English_Translation_v1.01.bps
```

Supported Japanese ROM SHA-256:

```text
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a
```

Expected translated ROM SHA-256:

```text
66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55
```

BPS SHA-256:

```text
bcaea7f01e331b1027a98dda123b2f23834450a268d9b6611445ef36b12d79d7
```

No ROM image is included.

## Tooling

The project uses one command-line interface and one generic BPS module:

```text
tools/sf2010.py   project-specific apply, verify, rebuild, and benchmark commands
tools/bps.py      dependency-free BPS codec
tools/data/       internal reproducibility inputs, not public release artifacts
```

Apply the release:

```bash
python tools/sf2010.py apply "Street Fighter 2010 (Japan).nes"
```

Verify the complete clean-ROM-to-release path:

```bash
python tools/sf2010.py verify "Street Fighter 2010 (Japan).nes" --verbose
```

Rebuild v1.01 and reproduce the canonical BPS byte-for-byte:

```bash
python tools/sf2010.py rebuild "Street Fighter 2010 (Japan).nes"
```

Benchmark the release tooling:

```bash
python tools/sf2010.py bench "Street Fighter 2010 (Japan).nes"
```

The benchmark reports median BPS-apply and verification time, median BPS-creation time, encoder peak memory, patch size, and canonical output identity. Performance changes are accepted only when the translated-ROM SHA-256 remains identical, the BPS round trip succeeds, release invariants pass, and the benchmark shows a runtime or memory improvement.

## v1.01 corrections

- Restores the explicit **"your strength"** wording in the Dagobah instruction.
- Corrects Dr. Jose's final-confrontation boast to preserve his first-person self-reference: **"I, Dr. Jose"**.
- Restores the forceful **"I'll test it on your body!"** wording in Jose's final line.

See [`docs/TRANSLATION.md`](docs/TRANSLATION.md) for source policy, terminology, release history, and the apostrophe-rendering note. The complete release script is in [`docs/FINAL_SCRIPT.txt`](docs/FINAL_SCRIPT.txt).

## Apostrophe rendering

The original renderer uses fixed-width character cells. The U.S. release also gives an apostrophe a full cell, so slightly unusual contraction spacing is an engine limitation rather than an unresolved translation bug. v1.01 keeps the stable dedicated apostrophe glyph rather than reintroducing the rejected ligature experiment.

## Credits

Project lead / translation editing / ROM hacking: **starlight_world**

Japanese translation reference: **The Cutting Room Floor (TCRF)**

Original game: **Capcom / Status (1990)**

## Legal

This is a non-commercial fan translation. No copyrighted ROM image is distributed. Game assets, names, trademarks, and copyrights remain the property of their respective owners.
