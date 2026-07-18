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
- [Native](native.md) — `assert_topmost` to ride above the topmost dial

### Used by
- [Clock Widget](widget.md) — mouse-move/leave hover driving
- [App Controller](controller.md) — owns the instance; the click-through
  cursor poller drives it the same way

## Classes

### LegendPopup
Frameless tooltip-class window (never takes focus), dark tooltip
styling, a rich-text QLabel inside a QScrollArea. Carries
`WindowStaysOnTopHint` so it sits in the TOPMOST band (owner 15h item
3A, Session 21: the legend was appearing BEHIND the dial in its "top"
z-mode — invisible, because the top-mode dial is native-topmost AND
focused). `WA_ShowWithoutActivating` keeps it from ever stealing focus.

#### Methods
- `show_html(html, anchor)`: sets the content and SIZES BY MEASURING —
  the html is laid out in a QTextDocument at the width cap and
  `idealWidth` gives the width the content actually asks for
  (declared table columns hold, nowrap lines stay natural); the label
  is fixed to that width so the justified prose wraps inside its
  column (owner regression 2026-07-13: QLabel's own wordWrap sizing
  squeezes declared columns, and no wordWrap at all sized the label
  to the UNWRAPPED document). Content wider than the cap (the hexa
  two-column legend on a small screen) scrolls SIDEWAYS instead of
  clipping. Then positions beside the cursor and clamps fully on
  screen (unchanged content only repositions) and finally re-asserts
  native topmost (`native.assert_topmost`, `SWP_NOACTIVATE` — no focus
  theft) so a freshly shown legend rides ABOVE even the native-topmost,
  focused dial in "top" z-mode
- `hide_unless_hovered()`: hides unless the cursor is inside the popup
  (crossing from the dial INTO the popup must not close it)
- `leaveEvent`: hides when the cursor leaves the popup itself

## Design note (proposed, not implemented) — Sunday dual portraits

Moved verbatim from the retired `research/prompts/weekday/sunday_duality.md`
(2026-07-12); this is a mechanism proposal, not an image prompt, so it
never belonged in a per-theme prompt file — this popup doc is its
correct home.

Grounded in the actual mechanism (`render/compositor.py`): every
weekday hover is one block of HTML built by `_article_html()` and
shown in this popup, a `QLabel` in `Qt.TextFormat.RichText` — a
`QTextDocument` subset that already supports basic `<table>` markup,
not just a single `<img>`. Today `_weekday_tooltip()` passes ONE
`image` path into `_article_html()`; for `body == "sun"` it would pass
a PAIR instead, so every dual-plate theme (Professions' Ruler/Servant
and any other theme that grows a Sunday dual) can show both portraits
on hover.

**Layout** — a two-column row above the shared title, each column its
own portrait + caption, divided by a small centered glyph so the pair
reads as one duality rather than two unrelated pictures:

```
┌───────────────┬───┬───────────────┐
│   Ruler.png    │ ⚖ │  Servant.png   │
│    "Ruler"     │   │   "Servant"    │
└───────────────┴───┴───────────────┘
        Ruler · Servant                 <- existing display name, unchanged
   Thursday... (only on the active day)
   [ the base article + active variant — already narrates both faces ]
```

- The divider glyph is the dial's own yin-yang shorthand already named
  in the Ruler article ("the dial's own yin-yang") — a small ☯ or a
  vertical hairline rule both read fine in Qt rich text; ☯ is more
  legible at hover size.
- Caption color continues the existing `accents=defaults.BODY_ACCENT_HUES[body]`
  mechanism: "Ruler" in warm gold, "Servant" in cool silver/gray — no
  new plumbing, just two `<span style='color:...'>` labels next to
  captions that don't exist for any other body today.
- The shared title stays exactly what it already is —
  `defaults.WEEKDAY_THEME_NAMES[...]["sun"]` already resolves to
  "Ruler · Servant" — so no new string is needed there.
- Every other body keeps the single-image path untouched; this is a
  `body == "sun"` branch inside `_weekday_tooltip()`/`_article_html()`,
  not a redesign of the popup.
- The mechanism generalizes for free to any OTHER theme that grows a
  second Sunday plate — the branch keys off `body == "sun"`, not off
  the Professions theme specifically, so Egypt/Norse/Japan/etc. get the
  same two-portrait hover the day their art lands.
