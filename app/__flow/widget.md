# Clock Widget — Flow

**About:** [description](../__about/widget.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["ClockWidget — frameless, translucent, square window"]
        MARGIN["transparent margin (letter overhang, halo, event glow)"]
        DIAL["dial_diameter × dial_diameter
        painted entirely by compositor.paint()"]
    end
    WIN -. "left click" .-> MOVE[native OS window move]
    WIN -. "right click" .-> MENU[shared QMenu — Show hidden here]
    WIN -. "double-click Omega" .-> REVEAL[toggle reveal-week]
    WIN -. "SPACE / hover" .-> ENC[open_encyclopedia signal]
```

## Algorithm — key input dispatch (`keyPressEvent`)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[keyPressEvent] --> B{key == Space AND no modifier?}
    B -- yes --> C[_trigger_space_jump]
    B -- no --> D["held = modifiers & ~KeypadModifier"]
    D --> E{"(key, held) matches a
    SHORTCUTS entry?"}
    E -- yes --> F["shortcut_triggered.emit(action_id)"]
    E -- no --> G{event.text() printable?}
    G -- yes --> H["typed.emit(text)"]
    G -- no --> I[super().keyPressEvent — Qt default]
```

## Algorithm — hover / SPACE-without-focus

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[mouseMoveEvent] --> B{bypass modifier held?}
    B -- yes --> C["set_hover off-canvas, dismiss legend,
    clear _last_hover, uninstall SPACE hook"]
    B -- no --> D["_last_hover = cursor pos
    compositor.set_hover(...)"]
    D --> E{compositor.tooltip_at returns text?}
    E -- yes --> F["show legend popup
    target = encyclopedia_target(...)
    install SPACE hook"]
    E -- no --> G["dismiss legend
    uninstall SPACE hook"]
    F -.-> H(("KeyboardHook fires
    on a real SPACE press,
    off the GUI thread"))
    H -- queued signal --> I[_trigger_space_jump]
    C2[keyPressEvent bare SPACE] --> I
    I --> J{_last_hover set AND
    encyclopedia_target found?}
    J -- yes --> K["open_encyclopedia.emit(topic, entry)"]
    J -- no --> L[no-op]
```

Both the focused path (`keyPressEvent`) and the unfocused path (the
native `KeyboardHook`, queued through `_space_pressed`) converge on the
SAME `_trigger_space_jump()` — the hook consumes SPACE at the OS level,
so the two paths can never double-fire.
