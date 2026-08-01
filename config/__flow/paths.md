# Paths — Flow

**About:** [description](../__about/paths.md)

## Display context lifecycle

```mermaid
flowchart TB
    A[Settings change / skin install] --> B["display_context(art_source, subdial_set, metal_shades)"]
    B --> C{every value valid?}
    C -- no --> D[raise ValueError immediately]
    C -- yes --> E[new frozen DisplayContext]
    E --> F["watch.skin.display = context"]
    F --> G["render/hover/dialog entry point:\nwith paths.display(watch.skin.display):"]
    G --> H[_active_display.context = watch's context\n(thread-local)]
    H --> I[body of the call runs — every\nart_source()/subdial_set()/metal_shade()\nread inside sees THIS watch's context]
    I --> J[on exit: _active_display.context restored\nto whatever it was before (nesting-safe)]
```

Pseudocode:

    in_display(method):                 # decorator on Compositor/WatchController entry points
        WRAP method(self, *a, **kw):
            WITH display(self._skin.display):
                RETURN method(self, *a, **kw)

    display(context):                   # context manager
        previous <- active_display.context
        active_display.context <- context
        TRY: YIELD
        FINALLY: active_display.context <- previous

Because `_active_display` is `threading.local()`, the GUI thread
painting watch A and a background warm thread pre-building watch B's
assets never observe each other's `art_source()`/`metal_shade()` — each
sees only the context installed on ITS OWN thread.

## Art file resolution

```mermaid
flowchart TB
    A["art_file(canonical_path)\ne.g. assets/.../Lion.png"] --> B[normalize path,\nstrip a leading ../ step-up]
    B --> C{suffix is .png\nAND stem has no _gem/_gpt already?}
    C -- no --> Z[return path unchanged]
    C -- yes --> D["active = ART_SUFFIX[current_display().art_source]"]
    D --> E["ordered = [active, the OTHER source]"]
    E --> F{"<stem>_<suffix>.png exists\nfor suffix in ordered, in order?"}
    F -- yes --> G[return that file]
    F -- no --> H{suffix-less canonical path exists?}
    H -- yes --> I[return canonical path\n(owner hand-made art)]
    H -- no --> J[return canonical path anyway\n(caller owns the missing-art fallback)]
```

The fallback order is always: the ACTIVE source's suffixed file, then
the OTHER source's suffixed file (cross-source fallback — partial
ChatGPT coverage), then the suffix-less name, then give up gracefully.
