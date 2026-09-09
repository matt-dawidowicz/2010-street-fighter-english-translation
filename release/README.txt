2010 STREET FIGHTER
Faithful English Retranslation
Version 1.01

OVERVIEW
--------
This patch provides a faithful English translation of the original Japanese
Famicom version of 2010 Street Fighter.

The official North American release substantially rewrote the story to tie the
game more directly to the Street Fighter series. This translation preserves
the Japanese continuity instead: Kevin Striker remains the protagonist, and
the Parasites, Armored Insects, Galaxy Police, and original terminology are
retained.

The English script was informed by the translation documented on The Cutting
Room Floor (TCRF), checked against the Japanese game and original manual/demo
transcripts, and edited for natural English without intentionally changing the
original meaning. Kevin's surname follows Capcom's later official English
rendering, Kevin Striker.

RELEASE STATUS
--------------
v1.01 is a maintenance release built on the fully playtested V12 / RC9 v1.0
baseline. Gameplay code, renderer fixes, graphics, and all dialogue other than
the three corrections below are unchanged.

V1.01 SCRIPT CORRECTIONS
------------------------
- Record 5 restores the explicit "your strength" wording in the Dagobah scene.
- Record 10 makes Dr. Jose's self-reference unambiguous: "I, Dr. Jose".
- Record 20 restores the forceful "I'll test it on your body!" wording.

These changes were checked against the Japanese in-game text and original
manual transcription. Primary online references used for this maintenance audit:

  https://www.ne.jp/asahi/hzk/kommander/2010top.html
  https://game.capcom.com/cfn/sfv/column/130987?lang=en

A later V13 / RC10 experiment attempted to combine apostrophes with preceding
letters to improve contraction spacing. It caused runtime regressions and was
rejected. The experiment is preserved in the source repository for historical
reference only and is not part of this release.

FEATURES
--------
- Complete English translation of the Japanese Famicom version
- Original Japanese storyline and terminology retained
- Translated opening story sequence
- Reworked English dialogue layout and scrolling
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting of the v1.0 baseline

PATCH CONTENTS
--------------
Patch format: BPS
Patch file: 2010_Street_Fighter_English_Translation_v1.01.bps

The previous v1.0 patch is retained in the repository for historical
reproducibility. No ROM image is included.

SUPPORTED SOURCE
----------------
Apply the patch to a clean, unmodified copy of the supported Japanese Famicom
ROM.

Source ROM SHA-256:
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a

Expected translated ROM SHA-256:
66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55

v1.01 BPS SHA-256:
bcaea7f01e331b1027a98dda123b2f23834450a268d9b6611445ef36b12d79d7

PATCHING
--------
Use any BPS-compatible patcher, or use the dependency-free Python utility
included in the repository:

  python tools/apply_bps.py \
    "Street Fighter 2010 (Japan).nes" \
    release/2010_Street_Fighter_English_Translation_v1.01.bps \
    "2010 Street Fighter (English v1.01).nes"

To validate the supported source and resulting translated ROM:

  python tools/verify_release.py "Street Fighter 2010 (Japan).nes"

To reproduce the v1.01 ROM and BPS from the clean source plus the retained v1.0
baseline patch:

  python tools/build_v101.py "Street Fighter 2010 (Japan).nes"

KNOWN QUIRK
-----------
The original text renderer is tile-based and was not designed for English
contractions. Apostrophes can therefore have slightly unusual spacing. This is
a cosmetic limitation of the stable V12 / RC9 implementation.

CREDITS
-------
Project lead / translation editing / ROM hacking: starlight_world
Japanese translation reference: The Cutting Room Floor (TCRF)
Original game: Capcom / Status, 1990

LEGAL
-----
This is a fan-made, non-commercial translation patch. No copyrighted ROM image
is distributed. You must provide your own legally obtained copy of the original
game. Game assets, names, trademarks, and copyrights remain the property of
their respective owners.
