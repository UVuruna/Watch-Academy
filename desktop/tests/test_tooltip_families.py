"""THE TOOLTIP FAMILY SPLIT's safety net (WA-R13b, owner 2026-08-19).

`render/tooltip_composer.py` was 2,239 logic lines — every hover the dial
answers, one short named method per element — and the owner ruled it be
cut BY FAMILY: the sky, the ring, the calendar, and the "what article
does this open" targets. A cut like that is only safe if the HTML the
dial says is byte-identical afterwards, so this file is the proof.

It sweeps a deterministic grid of hover points over seven dial
configurations at ONE frozen instant and records, for every point that
answers at all:

* a **SHA-256 of the exact `tooltip_at` HTML** plus the exact
  `encyclopedia_target` tuple — 959 points, so one changed character
  anywhere in any family fails and names the point; and
* the **full HTML, verbatim**, of the six longest answers per
  configuration — 42 representative tooltips spanning every family, so
  a failure can be READ rather than only detected.

The recording lives in `tests/tooltip_goldens.json` and was CAPTURED
BEFORE the split, from the un-split composer (commit `6aa49db`).

It is not a snapshot test that ratifies whatever the code does today: it
is a MOVE test. Re-recording it is legitimate only when a hover's TEXT is
deliberately changed, and then the diff belongs in that session's report:

    DOMY_TOOLTIP_REBASELINE=1 python -m pytest tests/test_tooltip_families.py
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor

GOLDENS = Path(__file__).resolve().parent / "tooltip_goldens.json"

#: One frozen instant, chosen so the sky is BUSY: mid-July, minutes past
#: solar noon, inside a waxing lunation — the sun face, the moon marker,
#: the season row and the twilight bands all have something to say.
WHEN = datetime(2026, 7, 16, 12, 15)

SIZE = 720.0

#: The dial configurations swept. Between them they mount every family:
#: the hexa pointer's weekday bodies and its ring, the calendar pointer's
#: two wheels and its mounts, the trio's archetype arms, the octa's slots.
CONFIGS = {
    "hexa": {},
    "calendar_zodiac": {"pointer": "calendar", "palette_style": "primary"},
    "calendar_almanac": {"pointer": "calendar", "palette_style": "secondary"},
    "trio": {"pointer": "trio"},
    "octa": {"pointer": "octa"},
    "cross": {"pointer": "cross"},
    "rose": {"pointer": "rose"},
}

#: A 15×15 grid over the dial, plus the exact centre. Coarse enough to
#: stay fast, fine enough that every seat, wedge, arm, jewel and band on
#: a 720 px dial is hit by at least one point.
STEP = SIZE / 14

#: How many of a configuration's answers are kept as FULL HTML rather
#: than as a digest — the longest ones, because a long tooltip is a rich
#: one and reads as the family's own voice.
REPRESENTATIVES = 6


def _digest(tip: str | None) -> str | None:
    if tip is None:
        return None
    return hashlib.sha256(tip.encode("utf-8")).hexdigest()


def _points():
    for row in range(15):
        for col in range(15):
            yield round(col * STEP, 3), round(row * STEP, 3)
    yield SIZE / 2, SIZE / 2


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _day_tick(when):
    city = defaults.DEFAULT_CITY
    now = when.replace(tzinfo=ZoneInfo(city["timezone"]))
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _sweep(app) -> dict:
    """Every answer the dial gives, over every configuration and point."""
    day, tick = _day_tick(WHEN)
    out: dict[str, dict[str, object]] = {}
    for name, overrides in CONFIGS.items():
        skin = dataclasses.replace(defaults.DEFAULT_SKIN, **overrides)
        dial = Compositor(skin, AssetCache())
        dial.render_offscreen(SIZE, 1.0, day, tick)
        answers: dict[str, object] = {}
        full: dict[str, str] = {}
        for x, y in _points():
            key = f"{x}x{y}"
            tip = dial.tooltip_at(x, y, SIZE)
            target = dial.encyclopedia_target(x, y, SIZE)
            if tip is None and target is None:
                continue
            answers[key] = {
                "sha256": _digest(tip),
                "target": list(target) if target else None,
            }
            if tip is not None:
                full[key] = tip
        longest = sorted(full, key=lambda k: -len(full[k]))[:REPRESENTATIVES]
        out[name] = {
            "points": answers,
            "representative_html": {k: full[k] for k in sorted(longest)},
        }
    return out


def test_every_hover_the_dial_answers_is_unchanged_by_the_family_split(app):
    """THE MOVE PROOF: the recorded HTML, character for character.

    A family that moved into `render/tooltip_sky.py`, `tooltip_ring.py`,
    `tooltip_calendar.py` or `encyclopedia_targets.py` must answer
    exactly what it answered from inside `tooltip_composer.py`.
    """
    fresh = _sweep(app)
    if os.environ.get("DOMY_TOOLTIP_REBASELINE"):
        GOLDENS.write_text(
            json.dumps(fresh, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        pytest.skip("goldens re-recorded — the diff belongs in the report")

    golden = json.loads(GOLDENS.read_text(encoding="utf-8"))
    assert set(fresh) == set(golden), "a dial configuration appeared or vanished"

    drift = []
    for config in sorted(golden):
        was, now = golden[config]["points"], fresh[config]["points"]
        for key in sorted(set(was) | set(now)):
            before, after = was.get(key), now.get(key)
            if before != after:
                drift.append(f"{config} @ {key}:\n    was {before}\n    now {after}")
        was_html = golden[config]["representative_html"]
        now_html = fresh[config]["representative_html"]
        for key in sorted(set(was_html) | set(now_html)):
            if was_html.get(key) != now_html.get(key):
                drift.append(
                    f"{config} @ {key} — the HTML itself:\n"
                    f"    was {was_html.get(key)!r}\n"
                    f"    now {now_html.get(key)!r}"
                )
    assert not drift, (
        "THE TOOLTIP FAMILY SPLIT changed what the dial SAYS — it was a "
        "move, so nothing may differ. "
        f"{len(drift)} hover(s) drifted:\n  " + "\n  ".join(drift[:12])
    )


def test_the_sweep_actually_covers_every_family(app):
    """A silent net is worse than none: the recording must contain at
    least one answer from each family, or a family could be broken
    without the test above noticing."""
    golden = json.loads(GOLDENS.read_text(encoding="utf-8"))
    blob = json.dumps(golden, ensure_ascii=False)
    answers = sum(len(v["points"]) for v in golden.values())
    assert answers > 200, f"only {answers} recorded hovers — the sweep went blind"
    for family, needle in (
        ("sky / the moon", "Moon"),
        ("sky / the season row", "Solstice"),
        ("calendar / the wedges", "Cancer"),
        ("targets / the Encyclopedia jump", '"target": ['),
    ):
        assert needle in blob, f"the sweep records nothing from {family}"
