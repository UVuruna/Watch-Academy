# Legend Popup

**Script:** [Legend Popup (script)](legend_popup.py)

## Purpose
The hover window that replaces `QToolTip` (owner decision): QToolTip
neither scrolls nor shrinks, so article hovers taller than a small
screen (1080p) were clipped at its edge. This popup caps itself to a
fraction of the screen, grows a vertical scrollbar when the content is
taller, and STAYS OPEN while the cursor is over it — the wheel scrolls
the article.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — size caps, colors, offsets

### Used by
- [Clock Widget](widget.md) — mouse-move/leave hover driving
- [App Controller](controller.md) — owns the instance; the click-through
  cursor poller drives it the same way

## Classes

### LegendPopup
Frameless tooltip-class window (never takes focus), dark tooltip
styling, a rich-text QLabel inside a QScrollArea.

#### Methods
- `show_html(html, anchor)`: sets the content, sizes to it (capped to
  the screen fractions), positions beside the cursor and clamps fully
  on screen; unchanged content only repositions
- `hide_unless_hovered()`: hides unless the cursor is inside the popup
  (crossing from the dial INTO the popup must not close it)
- `leaveEvent`: hides when the cursor leaves the popup itself
