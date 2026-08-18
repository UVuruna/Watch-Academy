# Dialog Base

**Script:** [Dialog Base (script)](../dialog_base.py)

## Purpose
`AcademyDialog(QDialog)` — one Watch Academy window, and the four things
every one of them does.

Seven top-level dialogs open off the dial: [Encyclopedia](
../encyclopedia/__about/dialog.md), [Observatory](observatory.md),
[Report](report.md), [Shortcuts](shortcuts_window.md), [Time
Travel](time_travel.md), [Settings](
../settings_dialog/__about/dialog.md) and the [Watch Face
Window](../watch_face/__about/window.md). Each of them opened by writing
the same four incantations again — the translation overlay, a `tr` over
it, the `"Watch Academy — <name>"` title, and the stay-on-top flag —
which is why the [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md)
listed "top-level dialog" as a kind with eight instances and NO base
class. A window now declares what it is called and whether it floats.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.APP_NAME`
  and `ui_text.ui`, the chrome translator

### Used by
- the seven windows above; every one of them calls
  `super().__init__(title, overlay, stay_on_top, parent)` as its first
  statement

## Design Decisions
- **`stay_on_top` is a parameter, not a policy.** A window is NORMAL by
  default (owner 2026-07-13 — it must yield to whatever has focus); in
  "top" z-mode the dial forces itself to the TRUE top of the Z-order
  (`native.assert_topmost`, HWND_TOPMOST) and an ordinary window would
  open UNDER it (owner verdict 2026-07-19). The Encyclopedia, the
  Observatory and the Watch Face window pass the controller's reading
  through; the always-modal four ask for it outright.
- **`apply_theme(self)` is NOT in the base**, and that is the one line
  the audit's count included that stayed put. Its POSITION is
  load-bearing and differs by window: the Watch Face window themes
  BEFORE it builds, because it computes its own minimum from the pages'
  size hints and the QSS paddings are part of the real size (measured
  20px on the Colors groups); the others theme after their content
  exists. Pulling it into `__init__` would silently move every one of
  those measurements — a behaviour change wearing a refactor's clothes.
- **Neither is the opening size or the computed minimum.** Each window
  measures its own content: a nav column plus the widest panel, a
  chart's aspect ratio, a table's rows. There is nothing to share.
- **`_tr` is a METHOD, not a lambda attribute.** Six windows assigned a
  closure over `overlay`; the Settings dialog already had a method,
  because its section mixins call `self._tr`. One method serves both
  shapes and costs no closure per window.
- **`TintPopover` is not one of these.** The audit counted it as the
  eighth QDialog, but it is a frameless `Qt.Popup` that RECEIVES its
  `tr` from the section building it — no title bar, no stay-on-top, no
  overlay of its own. It is a picker, not a window.
