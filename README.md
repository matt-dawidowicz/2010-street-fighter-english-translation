# 2010 Street Fighter — Faithful English Retranslation

A faithful English translation of the original Japanese Famicom version of **2010 Street Fighter**.

Unlike the official North American localization, this project preserves the Japanese storyline and terminology: **Kevin Straker**, the **Parasites**, **Armored Insects**, the **Galaxy Police**, and the rest of the original continuity. It does not use the U.S. rewrite that turns Kevin into Ken and introduces Troy/Cyboplasm material.

The English script was heavily informed by the translation documented on **The Cutting Room Floor (TCRF)**, with additional checking against the Japanese game and manual and a prose pass for natural English.

## Release v1.0

The public release is the **V12 / RC9** state that completed full-game playtesting. The later apostrophe-ligature experiment was deliberately abandoned after runtime regressions and is retained only under `experiments/` for historical transparency.

### Features

- Complete English translation of the Japanese Famicom release
- Original Japanese storyline and terminology retained
- English opening crawl
- Reworked dialogue layout and scrolling for English
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting

### Known cosmetic quirk

The stock text system is tile-based and was not designed for English contractions. Apostrophes can have slightly unusual spacing. This is cosmetic only and was accepted for v1.0 rather than risking additional renderer regressions.

## Applying the patch

No ROM image is included in this repository.

Use the BPS patch in `release/` with a clean copy of the Japanese Famicom ROM.

Supported source ROM SHA-256:

```text
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a
```

Expected translated ROM SHA-256:

```text
2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d
```

You can use Floating IPS (Flips), or the included dependency-free Python BPS applier:

```bash
python tools/apply_bps.py \
  "Street Fighter 2010 (Japan).nes" \
  release/2010_Street_Fighter_English_Translation_v1.0.bps \
  "2010 Street Fighter (English v1.0).nes"
```

To verify the release against the supported source ROM:

```bash
python tools/verify_release.py "Street Fighter 2010 (Japan).nes"
```

## Repository layout

- `release/` — public BPS patch
- `src/history/` — retained development-stage patch/build scripts
- `docs/` — final script, layout audits, and translation notes
- `experiments/` — abandoned post-v1.0 experiments, not part of the release
- `tools/` — generic release application/verification tooling

## Development history

The retained code reflects the project's late-stage development sequence:

- **V8 / RC4:** dialogue-system rebuild and English typography support
- **V9 / RC5:** final prose pass and packed dialogue rebuild
- **RC6:** cursor restoration for the normal build
- **V10 / RC7:** cursor/Record 11 scrolling correction
- **V11 / RC8:** U.S.-style post-scroll behavior; temporary apostrophe experiment
- **V12 / RC9:** final v1.0 apostrophe glyph used by the release
- **V13 / RC10:** experimental contraction ligatures; rejected and not released

Some earlier exploratory stages predated the retained source snapshot. The public v1.0 BPS patch plus `tools/apply_bps.py` provides a deterministic clean-ROM-to-release path, while the retained late-stage scripts document the semantic text/renderer work that produced the release.

## Credits

Project / translation editing / ROM hacking: **Matt Dawidowicz**

Japanese translation reference: **The Cutting Room Floor (TCRF)**

Original game: **Capcom / Status (1990)**

## Legal

This is a non-commercial fan translation. No copyrighted ROM image is distributed. Game assets, names, trademarks, and copyrights remain the property of their respective owners.
