# Changelog

## v1.01 — current release

v1.01 is a source-audited maintenance update to v1.0. It changes only three dialogue records:

- Record 5 restores the explicit "your strength" wording in the Dagobah instruction.
- Record 10 restores Dr. Jose's first-person self-reference: "I, Dr. Jose".
- Record 20 restores the assertive "I'll test it on your body!" wording.

The update preserves the established renderer behavior, Record 11 long-dialogue handling, cursor behavior, graphics, and gameplay code. Record 5 is relocated into unused dialogue space because the corrected line is longer; Records 10 and 20 remain within their existing allocations.

## v1.0

Initial public translation release. This established the complete English script, opening crawl, English punctuation support, dialogue layout, long-text scrolling fixes, and the stable fixed-width apostrophe implementation used by v1.01.

The v1.0 runtime baseline was playtested from start to finish.

## Renderer note

The original text engine allocates a full character cell to apostrophes. The North American release uses the same basic fixed-width approach, so slightly unusual contraction spacing is an engine limitation rather than a translation defect. A custom ligature experiment was tested during development but rejected after runtime regressions.

## Repository maintenance

The active tree now contains only current release documentation and tooling. Superseded V9 documents, old stage-specific patch scripts, and rejected experimental code were removed after v1.01. They remain recoverable from Git history.
