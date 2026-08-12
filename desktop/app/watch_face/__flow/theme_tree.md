# Content Tree — Flow

**About:** [description](../__about/theme_tree.md)

## Layout

🍞 Breadcrumb row (hidden on Level 1)
📑 Level 1 tabs — Weekday themes / Complications / Astrology /
   Ascendant / Chinese zodiac, filtered when `full_face=True`:
   `kinds = watch_face_kinds(pointer, pointer_shape)`
   "Weekday themes" shows only if `"week" IN kinds`; the other four
   never show at full face (no rendering path today — see themes.md)
IF no kind survives the filter:
   📄 explanatory note ("this pointer carries no full-face content" /
      "the Rose polygon carries only Cube content — not wired here")
ELSE, inside the active Level-1 tab:
   IF tab == "Weekday themes":
     IF `_nav.weekday_group is None`:
       📦 Level 2 — one tile per kinship group (`weekday_group_titles`)
     ELSE:
       🍞 "← <group title>" back button
       📦 Level 3 — that group's own theme tiles, the pointer's default
          theme starred ("★ ")
   IF tab == "Complications":
     📦 one pill per `SLOT_COMPLICATION_TITLES` entry
   IF tab IN ("Astrology", "Ascendant", "Chinese zodiac"):
     📦 one pill per style in `ZODIAC_SLOT_STYLES`/`CHINESE_SLOT_STYLES`

## Behaviour (pseudocode)

    ON a Level-1 tab click:
        _nav.kind = tab                # pure navigation, no setter
        rebuild in place

    ON a Level-2 group tile click:
        _nav.weekday_group = group     # pure navigation, no setter
        rebuild in place

    ON the "← back" click:
        _nav.weekday_group = None      # pure navigation, no setter
        rebuild in place

    ON a Level-3 theme tile click:
        descriptor.set_weekday(theme)  # a REAL setter — applies AND
                                        # refreshes the whole window
                                        # (see controller._slot_descriptors)

    ON a Complications/style pill click:
        descriptor.set_mode(mode)  /  descriptor.set_style_mode(family, style)

State (`_nav`, module-level — see theme_tree.md Design Decisions):
`kind` (which Level-1 tab), `weekday_group` (`None` = Level 2, else the
open group's title = Level 3).
