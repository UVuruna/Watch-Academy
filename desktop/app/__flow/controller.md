# Watch Controller — Flow

**About:** [description](../__about/controller.md)

## Algorithm — tick flow

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    W["WM_TIMECHANGE / resume from sleep
    (BROADCAST to every top-level window,
    run through EVERY installed filter)"] --> WC["_on_wake:
    re-aim _wake_timer (restartable single-shot)"]
    WC --> WR["_refresh_after_jump — ONE per burst"]
    WR --> B
    A[MinuteScheduler fires] --> B["_on_tick(clock_jumped)"]
    B --> C["now = wall clock in the active timezone
    (or the frozen simulation moment, while one runs)"]
    C --> D{"day_changed = (local date, UTC offset) changed
    or no day context yet"}
    D -- "day_changed OR clock_jumped" --> E["self._day = build_day_context(...)
    (repositories: seasons, moon, deep time — all PROCESS-WIDE)"]
    D -- neither --> F[keep self._day]
    E --> S{"day_changed?"}
    S -- yes --> HW["_start_hover_warm -> the manager's ONE queue"]
    S -- "no (a bare clock correction)" --> F
    HW --> F
    F --> G["tick = build_tick_state(self._day, now, ...)"]
    G --> H["widget.set_tick(tick) -> repaint"]
```

Unreadable or out-of-coverage astronomical data raises OUT of
`build_day_context` — the controller shows a visible dialog and exits
rather than let the dial silently render something wrong.

**The two seams marked above are the 2026-08-06 fix.** A clock jump
rebuilds the day CONTEXT (it may have crossed midnight, a zone or a
travel target) but never starts the hover sweep — an NTP correction of a
few seconds speaks no new article, and the sweep is 7,201 pure-Python
probes measured at 58.2 s. And because Windows broadcasts the message to
every window while Qt runs it through every installed filter, N watches
saw one SYNC as N² wakes until the coalescer collapsed the burst.

## What moved out (WA-R14, 2026-08-19)
The menu tree is [Controller Menu — Flow](controller_menu.md); the jump
arithmetic and the flowing simulated moment are
[Controller Simulation — Flow](controller_simulation.md). What is drawn
here is what the composition root itself still runs.

## Responsibility map — one class, six modules

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    subgraph ROOT["controller.py — the composition root"]
        RUN["__init__ / run / quit
        _on_tick / _on_wake
        _install_skin / _apply_language
        _position_widget / _poll_hover"]
    end
    subgraph SKIN["skin_builder.py (R10)"]
        BS["build_skin -> apply_display_settings"]
    end
    subgraph MENU["controller_menu.py"]
        BM["_build_menu / _refresh_menu_gating"]
    end
    subgraph DISP["controller_display.py"]
        SET["_set_* / _rotate_theme"]
    end
    subgraph DLG["controller_dialogs.py"]
        OPEN["_open_* / _reopen_live / _watch_face_setters"]
    end
    subgraph SC["controller_shortcuts.py"]
        ONSC["_on_shortcut + its families"]
    end
    subgraph TT["controller_simulation.py"]
        CJ["_compute_jump / _start_simulation"]
    end
    ROOT --> SKIN
    ROOT --> MENU
    ROOT --> DLG
    MENU --> DISP
    MENU --> DLG
    SC --> DISP
    SC --> TT
    DLG --> DISP
    DISP --> SKIN
    TT --> ROOT
```

All five are MIXINS of `WatchController`, so every arrow above is a
plain `self.` call — no back-channels, and no call site changed when
they were cut out.
