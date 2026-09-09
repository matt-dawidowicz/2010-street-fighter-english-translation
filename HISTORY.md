# Development Notes

This repository intentionally preserves both the shipped v1.0 path, the v1.01 maintenance release, and the late abandoned experiment that followed v1.0.

## v1.01 maintenance release

v1.01 keeps the complete V12 / RC9 v1.0 runtime baseline and changes only three source-audited dialogue records:

- Record 5 restores the explicit "your strength" wording in the Dagobah instruction.
- Record 10 restores Jose's first-person self-reference: "I, Dr. Jose".
- Record 20 restores the assertive "I'll test it on your body!" wording.

The maintenance builder leaves Record 11 byte-identical, preserves the V10/V11/V12 renderer fixes, and relocates only the enlarged Record 5 into unused packed-dialogue space.

## v1.0 release baseline

**v1.0 = normal RC9 / V12 behavior**

The final v1.0 release keeps the corrected Record 11 scrolling/post-scroll behavior and cursor restoration. It also uses a dedicated white apostrophe tile. The resulting contraction spacing is slightly unusual but stable and readable.

## Rejected V13 / RC10 experiment

The ligature experiment attempted to combine `T'`, `I'`, `U'`, and `N'` into single glyphs to remove the extra fixed-width apostrophe cell. Although promising in isolated tests, it produced regressions in the real game and was abandoned. Files under `experiments/` are historical only and must not be treated as release inputs.
