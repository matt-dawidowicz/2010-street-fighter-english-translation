# Translation and release notes

## Source policy

The Japanese game script is the primary translation source. The original Japanese manual and demo-text transcription are used for terminology and context, with TCRF as a secondary translation reference. Kevin's surname is rendered **Striker** in project documentation, following Capcom's later official English Character Guide; the surname does not appear in the in-game dialogue.

Primary online references:

- Japanese manual/demo transcription hub: https://www.ne.jp/asahi/hzk/kommander/2010top.html
- Capcom English Kevin Striker profile: https://game.capcom.com/cfn/sfv/column/130987?lang=en

## Canonical terminology

The release retains **Parasite**, **Armored Insect**, **Galaxy Police**, **Open Power**, **Dimensional Door**, and **Flip Shield**. **Dagobah** is retained as the intended planet spelling; the game deliberately uses Star Wars-derived planet names including Tatooine and Dagobah.

`BALLANTINE-TYPE` remains the best-supported reading of バランタイン型 because the original manual does not provide a Latin spelling.

## v1.01 corrections

### Record 5

v1.0:

```text
EQUIP IT, AND YOU'LL BE ONE STEP CLOSER TO PERFECTION...
```

v1.01:

```text
EQUIP IT, AND YOUR STRENGTH WILL COME ONE STEP CLOSER TO PERFECTION...
```

This restores the explicit Japanese reference to Kevin's strength approaching perfection.

### Record 10

v1.0:

```text
THAT'S RIGHT. OF ALL THE PARASITES CREATED BY DR. JOSE, YOU ARE THE GREATEST.
```

v1.01:

```text
THAT'S RIGHT. YOU ARE THE GREATEST PARASITE THAT I, DR. JOSE, HAVE CREATED.
```

Dr. Jose is the speaker. The Japanese uses a grandiose self-reference equivalent to "this Dr. Jose"; the v1.0 third-person English obscured that fact.

### Record 20

v1.0:

```text
KEVIN! LET ME TEST IT ON YOUR BODY!
```

v1.01:

```text
KEVIN! I'LL TEST IT ON YOUR BODY!
```

This restores the assertive force of Jose's Japanese declaration rather than making it sound like a request for permission.

All other release dialogue and the opening crawl remain unchanged. Record 14 was explicitly rechecked and retained because its v1.0 wording accurately reflects the Japanese.

## Renderer history and apostrophes

The stable release renderer descends from the v1.0 V12/RC9 path: cursor restoration, the Record 11/post-scroll correction, and the dedicated apostrophe glyph are retained unchanged in v1.01.

The engine is tile-based and advances one fixed-width cell for the apostrophe control code. The U.S. retail ROM uses the same fundamental full-cell approach, placing a comma-like glyph in the upper half of the cell. v1.01 uses a dedicated white upper-right apostrophe tile, which changes where the unavoidable empty space appears but does not attempt proportional typography.

A later ligature experiment combined `T'`, `I'`, `U'`, and `N'` into single glyphs to remove the extra cell. It changed packed text layout and produced runtime regressions, so it was rejected. The experiment is intentionally not retained in the active repository; Git history preserves it if archaeological reference is ever needed.

## Reproducibility

v1.01 is deterministically reconstructed from the supported clean Japanese ROM plus an internal v1.0 baseline patch under `tools/data/`. The public release artifact remains only the v1.01 BPS in `release/`.

`python tools/sf2010.py rebuild <rom>` asserts:

- the supported source SHA-256;
- the exact v1.0 baseline ROM SHA-256;
- Record 11 byte identity;
- cursor, apostrophe, and post-scroll renderer invariants;
- the exact v1.01 target SHA-256;
- the exact canonical v1.01 BPS SHA-256;
- a clean-source BPS round trip.

`python tools/sf2010.py bench <rom>` additionally measures the current BPS implementation and requires generated BPS identity with the checked-in release patch.
