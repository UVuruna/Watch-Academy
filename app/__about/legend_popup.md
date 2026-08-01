# Legend Popup

**Script:** [Legend Popup (script)](../legend_popup.py) · **Flow:** [diagram](../__flow/legend_popup.md)

## Purpose
The hover window that replaces `QToolTip`: `QToolTip` neither scrolls
nor shrinks, so an article hover taller than a small screen was clipped
at its edge. This popup caps itself to a fraction of the screen, grows a
vertical scrollbar when the content is taller, and stays open while the
cursor is over it so the wheel can scroll the article.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `encyclopedia_ui` size
  caps/padding, `palette` colors
- [Native](native.md) — `assert_topmost`, to ride above the natively
  topmost "top"-z-mode dial

### Used by
- [Clock Widget](widget.md) — mouse-move/leave drives it, `on_link`
  wired to the widget's own Encyclopedia jump
- [Watch Controller](controller.md) — owns the one instance; the
  click-through cursor poller drives it the same way

## Classes

### LegendPopup(QWidget)
Frameless, `Qt.WindowType.ToolTip`-class window that never takes focus
(`WA_ShowWithoutActivating`), carrying `WindowStaysOnTopHint` so it
lands in the same topmost band as a "top"-z-mode dial (otherwise it
would render BEHIND the dial, invisible). A rich-text `QLabel` inside a
`QScrollArea`.

#### Methods
- `show_html(content, anchor)`: sizes by MEASURING — lays the HTML out
  in an internal `QTextDocument` at the screen-fraction width cap and
  reads `idealWidth()` (declared table columns hold their width, nowrap
  lines stay natural — `QLabel`'s own word-wrap sizing would otherwise
  squeeze declared columns). The label is fixed to that width so
  justified prose wraps inside its column; content wider than the cap
  scrolls sideways instead of clipping. Positions beside `anchor`,
  clamped fully on-screen, then re-asserts native topmost.
- `hide_unless_hovered()`: hides unless the cursor is inside the popup
  (crossing from the dial INTO the popup must not close it)
- `dismiss()` / `leaveEvent()`: hide and clear the cached HTML
- `_link_activated(href)`: the footer's LEARN MORE anchor — routes to
  the `on_link` callable the owner installs (the widget wires the same
  Encyclopedia jump SPACE makes); no handler installed, no-op

## Design note (proposed, not implemented) — Sunday dual portraits
Grounded in `render/compositor.py`: every weekday hover is one block of
HTML shown in this popup — a `QTextDocument` subset that already
supports basic `<table>` markup, not just a single `<img>`. A dual-plate
theme (Ruler/Servant pairs) could show both portraits side by side on
hover, divided by a small centered glyph (☯ reads legibly at hover
size), instead of the single-image path every other body uses today.
Not built — recorded here as the mechanism sketch since it depends on
this popup's own HTML rendering, not on the dial.
