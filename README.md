# 2010 Street Fighter — Faithful English Retranslation

A faithful English translation of the original Japanese Famicom version of **2010 Street Fighter**.

The North American release rewrote the story to connect the game more directly to the Street Fighter series. This project preserves the Japanese continuity instead: **Kevin Striker**, the **Parasites**, **Armored Insects**, the **Galaxy Police**, and the original terminology and plot structure.

The script was checked against the Japanese game, the original manual/demo transcription, and reference translations, then edited for natural English without intentionally changing the original meaning. Kevin's surname is rendered **Striker**, following Capcom's later official English Character Guide.

## Current release: v1.01

v1.01 is a narrow maintenance update to v1.0. It makes three source-audited dialogue corrections while leaving gameplay, graphics, renderer behavior, and all other dialogue unchanged:

- Record 5 restores the explicit **"your strength"** wording in the Dagobah instruction.
- Record 10 restores Dr. Jose's first-person self-reference: **"I, Dr. Jose"**.
- Record 20 restores the assertive **"I'll test it on your body!"** wording.

### Features

- Complete English translation of the Japanese Famicom release
- Original Japanese storyline and terminology retained
- Translated opening crawl
- Reworked dialogue layout and scrolling for English
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting of the v1.0 runtime baseline

### Known renderer limitation

The game uses a fixed-width tile renderer. An apostrophe occupies a full 8-pixel character cell; the U.S. release uses the same basic full-cell mechanism for English contractions. v1.01 keeps the stable implementation and places a dedicated apostrophe glyph within that cell, so some contractions have slightly unusual spacing. This is cosmetic and intentionally retained rather than replacing the original text model with a custom ligature system.

## Applying the patch

No ROM image is included. Supply a clean, unmodified copy of the supported Japanese Famicom ROM.

Patch:

```text
release/2010_Street_Fighter_English_Translation_v1.01.bps
```

Supported source ROM SHA-256:

```text
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a
```

Expected translated ROM SHA-256:

```text
66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55
```

Apply with any BPS-compatible patcher, or use the included dependency-free utility:

```bash
python tools/apply_bps.py \
  "Street Fighter 2010 (Japan).nes" \
  release/2010_Street_Fighter_English_Translation_v1.01.bps \
  "2010 Street Fighter (English v1.01).nes"
```

Verify the complete clean-ROM-to-release path:

```bash
python tools/verify_release.py "Street Fighter 2010 (Japan).nes"
```

Reproduce the v1.01 ROM and BPS patch deterministically:

```bash
python tools/build_v101.py "Street Fighter 2010 (Japan).nes"
```

`build_v101.py` uses the retained v1.0 BPS as its verified baseline, applies only the three v1.01 dialogue corrections, and checks the resulting ROM and BPS hashes. The v1.0 patch remains in `release/` for this reproducibility path.

## Repository layout

- `release/` — current v1.01 patch, reproducibility baseline, and release notes
- `docs/` — current final script, translation notes, and build audit
- `tools/` — active patching, build, and verification utilities
- `HISTORY.md` — concise release history

Obsolete development-stage scripts, superseded V9 documentation, and the rejected apostrophe-ligature experiment have been removed from the active tree. They remain available through Git history if needed for archaeology.

## Sources

- Japanese manual and demo transcription: https://www.ne.jp/asahi/hzk/kommander/2010top.html
- Capcom official English Kevin Striker profile: https://game.capcom.com/cfn/sfv/column/130987?lang=en
- The Cutting Room Floor translation/reference material

## Credits

Project lead / translation editing / ROM hacking: **starlight_world**

Original game: **Capcom / Status (1990)**

## Legal

This is a non-commercial fan translation. No copyrighted ROM image is distributed. Game assets, names, trademarks, and copyrights remain the property of their respective owners.
