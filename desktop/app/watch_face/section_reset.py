"""The per-section Reset (owner order 2026-08-15: every section ends
with a Reset button that returns that section's settings to defaults).

The hard part is not the button, it is knowing WHICH settings a section
owns — and a hand-kept list per section is exactly the kind of record
that goes stale the first time somebody adds a control (the whole reason
this project's laws distrust declarations that nothing checks). So the
list is not declared at all: `RecordingSetters` wraps the setters dict a
section builder is handed and records every key the builder ASKS FOR
while it builds. Whatever the page reached for is, by definition, what
the page controls.

Two filters then decide what is resettable, both exact:

- the key must be a real field of `Settings` — which drops the data
  PROVIDERS a page also asks for (`slot_descriptors`,
  `opacity_skin_defaults`, `ring_has_crown_text`, `open_custom_ring`);
- the setter must take one value — which drops the few that take a
  target plus a value (`theme_metal`, `palettes`); those belong to a
  compound control and are left alone rather than reset wrongly.

A section with nothing resettable gets NO button (the same grammar as
verdict 8A: a control with nothing to offer is absent, not greyed).
"""

import dataclasses
import inspect

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from app.settings_store import Settings
from app.ui_style import tooltip_wrap


class RecordingSetters(dict):
    """The setters dict, plus a record of which keys were asked for.

    A `dict` subclass rather than a proxy object because the builders
    treat their `setters` as a plain mapping and some pass it on to
    helpers — anything less than a real dict would break at the first
    `setters.get` or `**setters`."""

    def __init__(self, wrapped: dict):
        super().__init__(wrapped)
        self._wrapped = wrapped
        self.asked: list = []

    def __getitem__(self, key):
        if key not in self.asked:
            self.asked.append(key)
        return self._wrapped[key]

    def get(self, key, default=None):
        if key in self._wrapped and key not in self.asked:
            self.asked.append(key)
        return self._wrapped.get(key, default)


def _takes_one_value(setter) -> bool:
    """True when `setter` accepts exactly one positional value. Anything
    unreadable (a builtin, a C-level partial) is treated as NOT
    resettable — the honest side of the guess."""
    try:
        signature = inspect.signature(setter)
    except (TypeError, ValueError):
        return False
    positional = [
        parameter for parameter in signature.parameters.values()
        if parameter.kind in (
            parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    required = [p for p in positional if p.default is p.empty]
    return len(required) == 1


def resettable_keys(asked, setters: dict) -> tuple[str, ...]:
    """The subset of `asked` this module is willing to reset, in the
    order the page asked for them."""
    fields = {field.name for field in dataclasses.fields(Settings)}
    # Indexed, never `in`: every asked key came OUT of this mapping, and
    # a `defaultdict` answers `in` with False for a key it would happily
    # produce — so membership would drop keys that genuinely exist.
    return tuple(
        key for key in asked
        if key in fields and _takes_one_value(setters[key])
    )


def reset_row(asked, settings, setters: dict, tr) -> QWidget | None:
    """The bottom row of a section: one right-aligned Reset button that
    puts every setting the section owns back to its factory value.

    Returns None when the section owns nothing resettable, so a page
    that is pure navigation grows no button it cannot honour."""
    keys = resettable_keys(asked, setters)
    if not keys:
        return None
    factory = Settings()
    button = QPushButton(tr("Reset"))
    button.setToolTip(tooltip_wrap(tr(
        "Put this section's settings back to their factory values."
    )))

    def apply() -> None:
        for key in keys:
            setters[key](getattr(factory, key))

    button.clicked.connect(apply)
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch(1)                 # the button sits at the right edge
    layout.addWidget(button)
    return row
