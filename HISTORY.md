# Development Notes

This repository intentionally preserves both the shipped v1.0 path and the late abandoned experiment that followed it.

## Release baseline

**v1.0 = normal RC9 / V12 behavior**

The final release keeps the corrected Record 11 scrolling/post-scroll behavior and cursor restoration. It also uses a dedicated white apostrophe tile. The resulting contraction spacing is slightly unusual but stable and readable.

## Rejected V13 / RC10 experiment

The ligature experiment attempted to combine `T'`, `I'`, `U'`, and `N'` into single glyphs to remove the extra fixed-width apostrophe cell. Although promising in isolated tests, it produced regressions in the real game and was abandoned. Files under `experiments/` are historical only and must not be treated as release inputs.
