# 2010 Street Fighter — Faithful English Retranslation

A faithful English translation of the original Japanese Famicom version of **2010 Street Fighter**.

The official North American release substantially rewrote the game's story to connect it more directly to the Street Fighter series. This project instead preserves the Japanese continuity: **Kevin Straker**, the **Parasites**, **Armored Insects**, the **Galaxy Police**, and the original terminology and plot structure.

The English script was informed by the translation documented on **The Cutting Room Floor (TCRF)**, then checked against the Japanese game and manual and edited for natural English while preserving the original meaning.

## v1.0

Version 1.0 corresponds to the fully playtested **V12 / RC9** build. A later V13 / RC10 apostrophe-ligature experiment introduced runtime regressions and was rejected; it remains under `experiments/` for historical reference only.

### Features

- Complete English translation of the Japanese Famicom release
- Original Japanese storyline and terminology retained
- Translated opening crawl
- Reworked dialogue layout and scrolling for English
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting

### Known cosmetic quirk

The original text renderer is tile-based and was not designed for English contractions. Apostrophes therefore have slightly unusual spacing in some words. This is cosmetic only. The v1.0 release keeps the stable V12 / RC9 implementation rather than the rejected ligature experiment.

## Applying the patch

No ROM image is included. You must supply a clean, unmodified copy of the supported Japanese Famicom ROM.

Patch file:

```text
release/2010_Street_Fighter_English_Translation_v1.0.bps
```

Supported source ROM SHA-256:

```text
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a
```

Expected translated ROM SHA-256:

```text
2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d
```

You can apply the BPS patch with any compatible patcher, or use the included dependency-free Python tool:

```bash
python tools/apply_bps.py \
  "Street Fighter 2010 (Japan).nes" \
  release/2010_Street_Fighter_English_Translation_v1.0.bps \
  "2010 Street Fighter (English v1.0).nes"
```

To verify the complete clean-ROM-to-release path:

```bash
python tools/verify_release.py "Street Fighter 2010 (Japan).nes"
```

The verifier checks the supported source SHA-256, applies the included BPS patch, and confirms the expected translated-ROM SHA-256.

## Repository layout

- `release/` — v1.0 BPS patch and release notes
- `docs/` — final script and translation notes
- `src/history/` — retained late-stage build and patch scripts
- `experiments/` — rejected post-v1.0 experiments; not release inputs
- `tools/` — dependency-free BPS application and release-verification utilities
- `HISTORY.md` — concise development-stage history

## Development history

- **V8 / RC4:** dialogue-system rebuild and English typography support
- **V9 / RC5:** final prose pass and packed-dialogue rebuild
- **RC6:** cursor restoration for the normal build
- **V10 / RC7:** cursor and Record 11 scrolling correction
- **V11 / RC8:** U.S.-style post-scroll behavior and temporary apostrophe experiment
- **V12 / RC9:** final v1.0 apostrophe implementation
- **V13 / RC10:** contraction-ligature experiment; rejected and not released

Some earlier exploratory stages predate the retained source snapshot. The checked-in v1.0 BPS patch is the canonical public release artifact; the retained scripts document the late-stage text and renderer work that produced it.

## Credits

Project lead / translation editing / ROM hacking: **starlight_world**

Japanese translation reference: **The Cutting Room Floor (TCRF)**

Original game: **Capcom / Status (1990)**

## Legal

This is a non-commercial fan translation. No copyrighted ROM image is distributed. Game assets, names, trademarks, and copyrights remain the property of their respective owners.
