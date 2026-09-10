2010 STREET FIGHTER
Faithful English Retranslation
Version 1.01

OVERVIEW
--------
This patch provides a faithful English translation of the original Japanese
Famicom version of 2010 Street Fighter.

The North American release rewrote the story to connect the game more directly
to the Street Fighter series. This translation preserves the Japanese
continuity instead, including Kevin Striker, the Parasites, Armored Insects,
Galaxy Police, and the original terminology and plot structure.

The script was checked against the Japanese game, the original manual/demo
transcription, and reference translations, then edited for natural English
without intentionally changing the original meaning.

V1.01 CHANGES
-------------
- Record 5 restores the explicit "your strength" wording in the Dagobah scene.
- Record 10 restores Dr. Jose's first-person self-reference: "I, Dr. Jose".
- Record 20 restores the forceful "I'll test it on your body!" wording.

Gameplay code, graphics, renderer behavior, and all other dialogue are unchanged
from the v1.0 runtime baseline.

FEATURES
--------
- Complete English translation of the Japanese Famicom release
- Original Japanese storyline and terminology retained
- Translated opening story sequence
- Reworked English dialogue layout and scrolling
- English quotation marks and punctuation support
- Cursor and long-dialogue renderer fixes
- Selected technical fixes from the U.S. release carried back where appropriate
- Full start-to-finish playtesting of the v1.0 runtime baseline

KNOWN RENDERER LIMITATION
-------------------------
The game uses a fixed-width tile renderer. An apostrophe occupies a full
8-pixel character cell; the U.S. release uses the same basic full-cell mechanism
for contractions. v1.01 keeps the stable implementation, so some apostrophes
have slightly unusual spacing. This is cosmetic and intentional.

PATCH
-----
Format: BPS
File: 2010_Street_Fighter_English_Translation_v1.01.bps

No ROM image is included.

SUPPORTED SOURCE
----------------
Source ROM SHA-256:
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a

Expected translated ROM SHA-256:
66aff12851c2328a54da8c1dfaaa654235d50c2eb5c167feb769abdcb48b6f55

v1.01 BPS SHA-256:
bcaea7f01e331b1027a98dda123b2f23834450a268d9b6611445ef36b12d79d7

PATCHING
--------
Use any BPS-compatible patcher, or the included dependency-free Python tool:

  python tools/apply_bps.py \
    "Street Fighter 2010 (Japan).nes" \
    release/2010_Street_Fighter_English_Translation_v1.01.bps \
    "2010 Street Fighter (English v1.01).nes"

Verification:

  python tools/verify_release.py "Street Fighter 2010 (Japan).nes"

Deterministic rebuild:

  python tools/build_v101.py "Street Fighter 2010 (Japan).nes"

The rebuild tool uses the retained v1.0 patch as a verified baseline and then
applies only the three v1.01 dialogue corrections.

SOURCES
-------
Japanese manual and demo transcription:
  https://www.ne.jp/asahi/hzk/kommander/2010top.html

Capcom official English Kevin Striker profile:
  https://game.capcom.com/cfn/sfv/column/130987?lang=en

Additional translation reference:
  The Cutting Room Floor (TCRF)

CREDITS
-------
Project lead / translation editing / ROM hacking: starlight_world
Original game: Capcom / Status, 1990

LEGAL
-----
This is a fan-made, non-commercial translation patch. No copyrighted ROM image
is distributed. You must provide your own legally obtained copy of the original
game. Game assets, names, trademarks, and copyrights remain the property of
their respective owners.
