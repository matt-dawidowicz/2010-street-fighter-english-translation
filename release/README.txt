2010 STREET FIGHTER
Faithful English Retranslation
Version 1.0

OVERVIEW
--------
This patch provides a faithful English translation of the original Japanese
Famicom version of 2010 Street Fighter.

The official North American release substantially rewrote the story to tie the
game more directly to the Street Fighter series. This translation preserves
the Japanese continuity instead: Kevin Straker remains the protagonist, and
the Parasites, Armored Insects, Galaxy Police, and original terminology are
retained.

The English script was informed by the translation documented on The Cutting
Room Floor (TCRF), checked against the Japanese game and manual, and edited for
natural English without intentionally changing the original meaning.

RELEASE STATUS
--------------
v1.0 is the fully playtested V12 / RC9 build.

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
- Full start-to-finish playtesting

PATCH CONTENTS
--------------
Patch format: BPS
Patch file: 2010_Street_Fighter_English_Translation_v1.0.bps

No ROM image is included.

SUPPORTED SOURCE
----------------
Apply the patch to a clean, unmodified copy of the supported Japanese Famicom
ROM.

Source ROM SHA-256:
2189de9029ec706edd8b6bbd67d66925fdd363c7d00149fabf113c8fd3cf0e0a

Expected translated ROM SHA-256:
2a79d8be801178cc46ee859009df906c3f1fe48d58ba126aba806303d64c8c5d

PATCHING
--------
Use any BPS-compatible patcher, or use the dependency-free Python utility
included in the repository:

  python tools/apply_bps.py \
    "Street Fighter 2010 (Japan).nes" \
    release/2010_Street_Fighter_English_Translation_v1.0.bps \
    "2010 Street Fighter (English v1.0).nes"

To validate the supported source and resulting translated ROM:

  python tools/verify_release.py "Street Fighter 2010 (Japan).nes"

KNOWN QUIRK
-----------
The original text renderer is tile-based and was not designed for English
contractions. Apostrophes can therefore have slightly unusual spacing. This is
a cosmetic limitation of the stable v1.0 implementation.

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
