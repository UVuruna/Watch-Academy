# Native — Flow

**About:** [description](../__about/native.md)

## Algorithm — `nchittest_falls_outside` (the circular hit test)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[WM_NCHITTEST message] --> B{message.message == WM_NCHITTEST?}
    B -- no --> C[False — not our message]
    B -- yes --> D["x, y <- signed low/high WORD of lParam
    (screen-space, physical pixels)"]
    D --> E["rect <- GetWindowRect(hWnd)
    center <- rect center
    radius <- min(width, height) / 2"]
    E --> F{"(x-center.x)² + (y-center.y)²
    > radius² ?"}
    F -- yes --> G[True — outside the inscribed circle]
    F -- no --> H[False — inside, ordinary hit testing applies]
```

The caller ([Clock Widget](../__about/widget.md)'s `nativeEvent`) returns
`winapi.HTTRANSPARENT` when this is True, so a click on the window's
square corner falls through to whatever lies beneath instead of hitting
the transparent margin.

## State machine — KeyboardHook

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    U[uninstalled] -- "install()" --> I[installed]
    I -- "uninstall()" --> U
    I -- "SPACE keydown, not already down" --> F["_on_space() fires
    (queued hop to Qt loop)"]
    F --> D[space_down = True, key consumed]
    D -- "SPACE keyup" --> I
    I -- "any other key" --> P[CallNextHookEx — passes through]
```

`install()`/`uninstall()` are both idempotent; the widget arms the hook
on hover-enter of a page-bearing target and disarms it on hover-leave,
`hideEvent`, click-through toggle and quit, so SPACE is only ever
consumed during a deliberate hover.
