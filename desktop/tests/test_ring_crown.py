"""RING VERDICTS round (owner decree 2026-08-05): the crown-text
WHITELIST (a `QValidator` derived from `constants.RING_CROWN_TEXT_
CHARSET` rejects an unsupported keystroke outright) and the LOCATION
crown option (a per-ring toggle that replaces the crown text with the
active location's own "CITY, COUNTRY", following every location change
— `app.skin_builder._location_crown_text`/`_compose_skin`,
`WatchController._active_location_display`).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QApplication, QLineEdit

from app.controller import WatchController
from app.skin_builder import _location_crown_text, build_skin
from app.settings_store import Settings, replace
from app.watch_face.ring import _crown_text_validator
from config import constants


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


# --- The whitelist validator (widget level) ---------------------------------


def test_crown_text_validator_accepts_every_charset_character(app):
    """Every character `constants.RING_CROWN_TEXT_CHARSET` names — the
    exact set the crown-text renderer can draw one-per-character — is
    ACCEPTABLE, derived programmatically, never a hand-written list."""
    edit = QLineEdit()
    validator = _crown_text_validator(edit)
    text = "".join(sorted(constants.RING_CROWN_TEXT_CHARSET))
    state, _text, _pos = validator.validate(text, 0)
    assert state == QValidator.State.Acceptable


@pytest.mark.parametrize("bad", ["hello", "HELLO#", "café", "A,B", "A-B"])
def test_crown_text_validator_rejects_unsupported_characters(app, bad):
    """Lowercase letters, accents and the punctuation with no plate of
    its own are all OUTSIDE the crown-text renderer's drawable set — the
    validator must refuse them (the field's own keystroke, not merely a
    build-time drop). The library HAS a "!" and a "?" plate since the
    owner's 2026-08-07 drop, so the rejected sample uses "#"."""
    edit = QLineEdit()
    validator = _crown_text_validator(edit)
    state, _text, _pos = validator.validate(bad, 0)
    assert state == QValidator.State.Invalid


def test_crown_text_field_typing_stops_at_the_first_bad_character(app):
    """A `QLineEdit` wearing the validator never lands a disallowed
    character in its own text, even keystroke by keystroke — the real
    UI behaviour the validate()-only probes above cannot show by
    themselves."""
    edit = QLineEdit()
    edit.setValidator(_crown_text_validator(edit))
    # The DIGITS became typeable with the owner's 2026-08-07 plate drop
    # (`numerals/0-9.png`); 'l'/'o' are lowercase and still have none.
    for char in "AB1lo":
        edit.insert(char)
    assert edit.text() == "AB1"


# --- The LOCATION crown option -----------------------------------------------


def test_location_crown_text_filters_to_the_drawable_charset():
    """`_location_crown_text` uppercases and keeps only characters
    `constants.RING_CROWN_TEXT_CHARSET` names (the SAME set the widget
    validator enforces, Rule #5) — the comma and any other unsupported
    character simply vanish, collapsing to one word-gap."""
    assert _location_crown_text("Belgrade, Serbia") == "BELGRADE SERBIA"
    assert _location_crown_text("São Paulo") == "SO PAULO"    # ã has no glyph
    # An input with nothing drawable at all resolves to "".
    assert _location_crown_text(",,,") == ""


def test_location_crown_renders_the_active_location_on_a_bundled_preset():
    """Rule 3 (owner decree 2026-08-05): available for BUNDLED presets
    too — ticking Location on DOMY (which carries its own cross-word
    crown text) REPLACES that crown text with the active location text."""
    bare = build_skin(replace(Settings(), ring="DOMY"), "Belgrade, Serbia")
    located = build_skin(
        replace(Settings(), ring="DOMY", ring_crown_location={"DOMY": True}),
        "Belgrade, Serbia",
    )
    assert bare.ring.crown_text and bare.ring.crown_text[0]["text"] != "BELGRADE SERBIA"
    assert len(located.ring.crown_text) == 1
    assert located.ring.crown_text[0]["text"] == "BELGRADE SERBIA"


def test_location_crown_renders_on_a_custom_ring_too():
    """Rule 3: available for CUSTOM rings too — replacing the ring's own
    typed crown text (or drawing one where none was typed at all)."""
    custom = ({"name": "CROWNLOC", "outer": "bot_cross", "jewels": ["A", "B", "C", "D"]},)
    located = build_skin(
        replace(
            Settings(), ring="CROWNLOC", custom_rings=custom,
            custom_ring_crown_text={"CROWNLOC": "HELLO"},
            ring_crown_location={"CROWNLOC": True},
        ),
        "Athens, Greece",
    )
    assert len(located.ring.crown_text) == 1
    assert located.ring.crown_text[0]["text"] == "ATHENS GREECE"


def test_location_crown_absent_context_leaves_the_ring_untouched():
    """No controller context at all (every direct/test caller of
    `build_skin`) must never crash — the Location crown simply draws
    nothing extra, the same graceful-absence pattern the custom crown
    text already uses."""
    skin = build_skin(
        replace(Settings(), ring="DOMY", ring_crown_location={"DOMY": True})
    )
    assert skin.ring.crown_text == build_skin(replace(Settings(), ring="DOMY")).ring.crown_text


# --- Follows a live location change (controller level) -----------------------


@pytest.fixture
def controller(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = WatchController(app)
    yield made
    for dialog in (made._encyclopedia, made._observatory, made._watch_face):
        if dialog is not None:
            dialog.close()
    made._fast_travel_flash.close()
    made._profiling_timer.stop()
    made._tray.hide()


def test_location_crown_follows_a_live_location_change(controller):
    """The Location crown must FOLLOW a location change (owner verdict)
    — a Quick Jump (Ctrl+Space, Greenwich) recomposes the skin through
    the SAME `_flash_location` R-30's own flash/tray-title path uses, so
    the crown reads the LANDED place immediately, never the home city
    frozen from construction."""
    controller._settings = replace(
        controller._settings, ring_crown_location={"DOMY": True},
    )
    controller._install_skin(
        build_skin(controller._settings, controller._active_location_display)
    )
    before = controller._skin.ring.crown_text[0]["text"]
    controller._jump_to_place("greenwich")
    after = controller._skin.ring.crown_text[0]["text"]
    assert after != before
    assert "GREENWICH" in after
