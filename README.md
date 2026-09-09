# 2010 Street Fighter — Faithful English Retranslation

A faithful English translation of the original Japanese Famicom version of **2010 Street Fighter**.

The official North American release substantially rewrote the game's story to connect it more directly to the Street Fighter series. This project instead preserves the Japanese continuity: **Kevin Striker**, the **Parasites**, **Armored Insects**, the **Galaxy Police**, and the original terminology and plot structure.

The English script was informed by the translation documented on **The Cutting Room Floor (TCRF)**, then checked against the Japanese game and original manual/transcripts and edited for natural English while preserving the original meaning. Kevin's surname is rendered **Striker**, following Capcom's later official English Character Guide.

## v1.01

Version 1.01 is a maintenance release built on the fully playtested **V12 / RC9** v1.0 release. It changes only three audited dialogue lines; gameplay code, renderer fixes, graphics, and the rest of the English script are unchanged.

### v1.01 script corrections

- Restores the explicit **"your strength"** wording in the Dagobah instruction.
- Corrects Dr. Jose's final-confrontation boast so his self-reference is clear in English: **"I, Dr. Jose"**.
- Restores the forceful **"I'll test it on your body!"** wording in Jose's final line.

The corrections were checked against the Japanese in-game text and the original manual transcription. Source references include the HZK reproduction/transcription of the Japanese manual and demo text (`https://www.ne.jp/asahi/hzk/kommander/2010top.html`) and Capcom's official English Kevin Striker profile (`https://game.capcom.com/cfn/sfv/column/130987?lang=en`). The v1.01 build deliberately reuses the stable v1.0 renderer and keeps the rejected V13 / RC10 apostrophe-ligature experiment out of the release path.

### Features

- Complete English translation of the Japanese Famicom release
- Original Japanese storyline and terminology retained
- Translated opening crawl
- Reworked dialogue layout and scrolling for English
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting of the v1.0 baseline

### Known cosmetic quirk

The original text renderer is tile-based and was not designed for English contractions. Apostrophes therefore have slightly unusual spacing in some words. This is cosmetic only. The release keeps the stable V12 / RC9 implementation rather than the rejected ligature experiment.

## Applying the patch

No ROM image is included. You must supply a clean, unmodified copy of the supported Japanese Famicom ROM.

Patch file:

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

You can apply the BPS patch with any compatible patcher, or use the included dependency-free Python tool:

```bash
python tools/apply_bps.py \
  "Street Fighter 2010 (Japan).nes" \
  release/2010_Street_Fighter_English_Translation_v1.01.bps \
  "2010 Street Fighter (English v1.01).nes"
```

To verify the complete clean-ROM-to-release path:

```bash
python tools/verify_release.py "Street Fighter 2010 (Japan).nes"
```

The verifier checks the supported source SHA-256, applies the included v1.01 BPS patch, and confirms the expected translated-ROM SHA-256.

To reproduce the maintenance build and BPS patch from a clean source ROM and the checked-in v1.0 baseline patch:

```bash
python tools/build_v101.py "Street Fighter 2010 (Japan).nes"
```

## Repository layout

- `release/` — v1.01 BPS patch, retained v1.0 patch, and release notes
- `docs/` — final scripts, translation notes, and the v1.01 build audit
- `src/history/` — retained late-stage v1.0 build and patch scripts
- `experiments/` — rejected post-v1.0 experiments; not release inputs
- `tools/` — dependency-free BPS application, v1.01 build, and release-verification utilities
- `HISTORY.md` — concise development-stage history

## Development history

- **V8 / RC4:** dialogue-system rebuild and English typography support
- **V9 / RC5:** final prose pass and packed-dialogue rebuild
- **RC6:** cursor restoration for the normal build
- **V10 / RC7:** cursor and Record 11 scrolling correction
- **V11 / RC8:** U.S.-style post-scroll behavior and temporary apostrophe experiment
- **V12 / RC9:** final v1.0 apostrophe implementation
- **V13 / RC10:** contraction-ligature experiment; rejected and not released
- **v1.01:** source-audited maintenance correction to Records 5, 10, and 20 only

Some earlier exploratory stages predate the retained source snapshot. The checked-in v1.01 BPS patch is the canonical current release artifact; v1.0 is retained for historical reproducibility.

## Credits

Project lead / translation editing / ROM hacking: **starlight_world**

Japanese translation reference: **The Cutting Room Floor (TCRF)**

Original game: **Capcom / Status (1990)**

## Legal

This is a non-commercial fan translation. No copyrighted ROM image is distributed. Game assets, names, trademarks, and copyrights remain the property of their respective owners.
