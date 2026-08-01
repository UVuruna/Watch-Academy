# Shortcuts — Flow

**About:** [description](../__about/shortcuts.md)

## Table shapes

```
📁 shortcuts.py
  SHORTCUTS: tuple of (action_id, key_name, modifier_names, description)
    e.g. ("cycle_ring", "Key_R", ("ControlModifier",), "Cycle to the next Ring preset")
    21 rows — menu actions, slot cycling (1/2/3 x complication/theme),
    Fast Travel (theme/option/past/future), Locations (poles/Greenwich/cities)

  FAST_TRAVEL_THEMES: tuple of dicts
    {id, title, icon_key, emoji, options: tuple of {id, title, jump_stem}}
    "sun"      -> any / solstice / equinox
    "moon"     -> full / new / quarter / eclipse
    "calendar" -> day / month / year / century / millennium
```

## shortcut_display resolution

```mermaid
flowchart TB
    A["shortcut_display(action_id)"] --> B[scan SHORTCUTS for matching action_id]
    B --> C{found?}
    C -- no --> D[raise KeyError]
    C -- yes --> E["key_label = _SHORTCUT_KEY_DISPLAY_OVERRIDES.get(key,\nkey without 'Key_' prefix)"]
    E --> F["mod_label = '+'.join(_SHORTCUT_MODIFIER_DISPLAY[m] for m in modifiers)"]
    F --> G["return f'{mod_label}+{key_label}'\ne.g. 'Ctrl+R'"]
```

## Fast Travel dispatch

```mermaid
flowchart LR
    A[Ctrl+bracket: cycle theme/option] --> B[WatchController picks\nFAST_TRAVEL_THEMES entry]
    B --> C[flash icon_key or emoji fallback]
    A2[Ctrl+minus/plus: step] --> D["_compute_jump('next_'+jump_stem\nor 'prev_'+jump_stem)"]
    D --> E[chained from the active\nrunning simulation]
```
