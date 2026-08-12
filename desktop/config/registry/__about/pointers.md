# The Pointer Registry

**Script:** [Pointers (script)](../pointers.py)

## Purpose

THE PERMISSION MATRIX — what each pointer may carry, and per SHAPE
(owner ruling 2026-08-04/05).

Until this landed, "which kind of theme may this pointer show" was
knowledge nobody had written down: the dial did what its render paths
happened to support, the Watch Face picker guessed from the global
default, and every session that asked had to re-derive the answer from
four modules.

Layer: config — pure DATA, imports nothing.

## Contents

- **The kinds** — `WEEK` (6+3), `DOZEN` (12+1), `CUBE` (24+3), `WHEEL`
  (N+centre).
- **The shapes** — `STAR` and `POLYGON`, the same two words
  `constants.POINTER_SHAPES` uses.
- **`POINTERS`** — pointer → `seats` (what the reader counts on the
  dial) and `carries` (shape → the kinds it may show, in picker order).
  An empty tuple is an ANSWER, not an omission.
- **`carries` / `may_carry` / `pointers_carrying`** — the matrix as
  three questions, so no caller re-derives it. An unknown pointer
  answers empty rather than raising: a settings file from a future
  build must never detonate a picker.

## The rulings it encodes

- **The Calendar refuses the week in both shapes.** It is cut into
  twelve and a week theme brings nine members at most; nine into twelve
  leaves three wedges to invent, and the registry invents nothing.
- **The shape changes the answer on the Rose.** Drawn as a STAR the
  Compass stands in focus with the remaining rays behind it — still
  hoverable — so the week and the cube can be read together. Drawn as
  DIAMONDS every one of the twenty-four is a seat and takes no guest:
  only the cube fills twenty-four.
- **The cube rides the Rose and the Calendar alone** — twenty-four
  seats, or twelve wedges each holding a whole AXIS (the outward and
  inward faces of one opposition).
- **Aurora carries no circular theme at all.** Its content rides one to
  three subdials, which show only today — a separate mechanism, outside
  this matrix on purpose.

## Connections

### Used by
- `tests/test_pointer_registry.py` — pins the matrix against the
  pointer list, the dial counts and the archetype grid
- the Watch Face theme picker (the per-pointer default table this
  unblocks)

### Related
- [Registry (folder)](../___registry.md)
