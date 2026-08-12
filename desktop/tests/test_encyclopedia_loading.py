"""The Encyclopedia's LAZY loading law (owner order 2026-07-26: "the
Encyclopedia BLOCKED the main thread for minutes — solve it once and
for all"). Root cause pinned here forever: `metal_variant_file` used to
GENERATE every cold gold/silver recolor at PATH-RESOLUTION time, and
`app.encyclopedia.topics()` resolves a couple hundred such paths while
the dialog is being BUILT, on the GUI thread — every art rename wave /
shade change / METAL_SWAP_VERSION bump invalidated the mtime-keyed
raster cache and the next open paid minutes of numpy recolors again
(and a source file deleted by a rename wave CRASHED the open outright,
on the unguarded `stat()`).

The law now: naming a variant (`metal_variant_path`) is pure; pixels
build in `ensure_variant` — on first display (the open page's few
images at most) or in the background warm (`app.encyclopedia_warm`).
These tests pin every clause.
"""

from datetime import date
from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from config import paths
from render.asset_recolor import (
    ensure_variant, metal_variant_path, variant_pending,
)
from render.assets import AssetCache


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def isolated_cache(tmp_path, monkeypatch):
    """Raster-cache writes land in tmp — the tests below must see a
    COLD cache regardless of what the dev machine's real one holds."""
    monkeypatch.setattr(
        paths, "settings_path",
        lambda watch_index=1: tmp_path / "settings.json",
    )
    return tmp_path


def _bronze_source(tmp_path: Path) -> Path:
    source = tmp_path / "plate.png"
    image = QImage(8, 8, QImage.Format.Format_RGBA8888)
    image.fill(QColor("#B08050"))    # squarely inside the warm-bronze mask
    assert image.save(str(source))
    return source


def _forbid_recolor(monkeypatch, message: str) -> None:
    def boom(*_args, **_kwargs):
        raise AssertionError(message)
    monkeypatch.setattr(AssetCache, "_recolored", staticmethod(boom))


def test_topic_table_build_runs_no_metal_recolor(
    app, isolated_cache, monkeypatch
):
    """THE 2026-07-26 REGRESSION PIN: building the whole topic table —
    every theme, every pantheon block, the chinese animals — must not
    touch the recolor kernel, even on a stone-cold cache."""
    _forbid_recolor(monkeypatch, "metal recolor ran during the topic build")
    from app import encyclopedia

    topics = encyclopedia.topics(date(2026, 7, 26))
    assert "greek" in topics and "chinese" in topics and "wolf" in topics


def test_dialog_open_runs_no_metal_recolor(app, isolated_cache, monkeypatch):
    """The full dialog OPEN (construction + the gallery screen) is
    equally clean — the block the owner reported lived exactly here."""
    _forbid_recolor(monkeypatch, "metal recolor ran during dialog open")
    from app.encyclopedia import EncyclopediaDialog

    dialog = EncyclopediaDialog()
    assert dialog.topic_key is None        # the home screen is up
    dialog.deleteLater()


def test_metal_variant_path_is_pure_and_ensure_materializes(
    app, isolated_cache, tmp_path
):
    source = _bronze_source(tmp_path)
    lazy = metal_variant_path(source, "gold")
    assert lazy != source
    assert not lazy.exists()               # named, not built — pure
    assert variant_pending(lazy)
    out = ensure_variant(lazy)             # first use builds it
    assert out == lazy
    assert lazy.exists()
    assert not variant_pending(lazy)
    assert not QImage(str(lazy)).isNull()


def test_metal_variant_path_missing_source_never_crashes(tmp_path):
    """A rename wave used to CRASH the Encyclopedia open on the eager
    `stat()` of a source no longer on disk — now the canonical path
    passes through and the exists() filter simply hides the look."""
    ghost = tmp_path / "ghost.png"
    assert metal_variant_path(ghost, "gold") == ghost
    assert not variant_pending(ghost)


def test_warm_encyclopedia_materializes_recorded_variants(
    app, isolated_cache, tmp_path, monkeypatch
):
    from app import encyclopedia_warm

    source = _bronze_source(tmp_path)
    lazy = metal_variant_path(source, "silver")
    assert not lazy.exists()
    fake_topics = {
        "one": {
            "title": "One",
            "icon": source,
            "entries": [{
                "looks": (("Silver", ((lazy,),)),),
                "name": "X",
                "article": ("emblem", "x", "X"),
                "accents": (),
            }],
            "variants": (("", 0, 1),),
        },
    }
    # The warm walk reads the SAME inventory the dialog does; the fake
    # stands in for it at the one import site (SESSION 27: the builder
    # is `app.encyclopedia.tree.topics`, re-exported by the package).
    monkeypatch.setattr(
        encyclopedia_warm, "encyclopedia_topics",
        lambda travel_date=None: fake_topics,
    )
    built = encyclopedia_warm.warm_encyclopedia()
    assert lazy.exists()
    assert built >= 1


def test_pending_looks_survive_into_the_reader(app, isolated_cache):
    """A cold cache must not HIDE the Gold/Silver looks: a recorded,
    not-yet-built variant counts as present in the reader's filter and
    materializes only when its look is actually displayed."""
    from app.encyclopedia import EncyclopediaDialog

    dialog = EncyclopediaDialog(initial_topic="wolf", initial_entry=1)
    state = dialog._reader._look_state
    assert state is not None
    assert "Gold" in state["titles"]
    assert "Silver" in state["titles"]
    dialog.deleteLater()
