"""THE ONE COPY RULE, second pass (owner 2026-08-06).

His question after the SYNC freeze was the general one: *"jel ima jos
nekih nelogicnosti da ucitavamo vise puta istu stvar ili da ucitavamo na
vise mesta"*. What an audit found was not more JSON parsing but repeated
FILESYSTEM work on the paint path, plus two places where the same job was
started once per watch instead of once per process.

Measured on one real dial, thirty consecutive paints:

    before   31 Path.exists() + 6 Path.iterdir() per paint
    after     0 + 0

Every cache below remembers ONLY what it FOUND. A miss is never cached,
because art appears at runtime in this app — the owner drops files in and
a recolor drain lands derived work — and a remembered "not there" would
keep a dial standing in with its gold master until the next restart. That
exact failure already happened here once (0.14.707). The tests that pin
this rule are the important half of this module.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import threading
from pathlib import Path

import pytest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.watch_manager import AppController
from config import pantheon, paths
from data import locations, translations
from render import archetype_geometry, painting


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def painted(app):
    """A watch that has ticked and painted once, so every cache below is
    in the state a running dial is actually in."""
    watch = WatchController(app)
    watch._on_tick(clock_jumped=False)
    size = float(watch._settings.diameter)
    image = QImage(
        int(size), int(size), QImage.Format.Format_ARGB32_Premultiplied
    )
    tick = watch._widget._tick

    def repaint():
        painter = QPainter(image)
        try:
            watch._compositor.paint(painter, size, 1.0, tick)
        finally:
            painter.end()

    repaint()
    yield watch, repaint
    watch._teardown_windows()


class _Counter:
    """Counts Path.exists()/iterdir() while the block runs."""

    def __enter__(self):
        self.exists = 0
        self.iterdir = 0
        self._real_exists, self._real_iterdir = Path.exists, Path.iterdir
        counter = self

        def exists(path, *a, **k):
            counter.exists += 1
            return counter._real_exists(path, *a, **k)

        def iterdir(path, *a, **k):
            counter.iterdir += 1
            return counter._real_iterdir(path, *a, **k)

        Path.exists, Path.iterdir = exists, iterdir
        return self

    def __exit__(self, *exc):
        Path.exists, Path.iterdir = self._real_exists, self._real_iterdir
        return False


# --- the paint path stops touching the disk ------------------------------------

def test_a_steady_state_repaint_touches_no_files(painted):
    """The dial repaints every tick — by default every SECOND, per watch.
    Nothing it draws can change on disk between two frames, so a settled
    dial must resolve everything from memory."""
    _watch, repaint = painted

    with _Counter() as counted:
        repaint()

    assert (counted.exists, counted.iterdir) == (0, 0)


def test_clearing_the_caches_makes_the_work_come_back(painted):
    """Proves the test above measures the CACHES and not some unrelated
    short circuit — clear them and the filesystem work reappears."""
    _watch, repaint = painted
    paths.reset_art_file_cache()
    pantheon.reset_rotation_cache()
    archetype_geometry.reset_art_size_cache()

    with _Counter() as counted:
        repaint()

    assert counted.exists > 0, "the caches were not what made it quiet"


# --- a miss is never cached ----------------------------------------------------

def test_missing_art_is_never_remembered_as_missing(tmp_path):
    """THE SAFETY RULE. Art lands at runtime in this app; a cached
    absence would hide it until the next restart."""
    paths.reset_art_file_cache()
    canonical = tmp_path / "Figure.png"

    first = paths.art_file(canonical)
    assert first == canonical                    # nothing on disk yet
    assert paths.existing_art_file(canonical) is None

    (tmp_path / "Figure_gem.png").write_bytes(b"not really a png")

    assert paths.art_file(canonical) == tmp_path / "Figure_gem.png"
    assert paths.existing_art_file(canonical) is not None


def test_an_empty_rotation_pool_is_never_remembered(tmp_path):
    """Same rule one layer up: a seat whose art has not been generated
    yet must be rescanned, not written off."""
    pantheon.reset_rotation_cache()
    stems = ("Figure",)

    assert pantheon._rotation_candidates_in(tmp_path, stems) == []

    (tmp_path / "Figure.png").write_bytes(b"not really a png")

    assert pantheon._rotation_candidates_in(tmp_path, stems) != []


def test_a_found_art_file_is_remembered(tmp_path):
    """The other half — otherwise the cache would do nothing."""
    paths.reset_art_file_cache()
    canonical = tmp_path / "Figure.png"
    (tmp_path / "Figure_gem.png").write_bytes(b"not really a png")
    paths.art_file(canonical)

    with _Counter() as counted:
        paths.art_file(canonical)
        paths.existing_art_file(canonical)

    assert counted.exists == 0


def test_new_art_landing_clears_every_resolution_cache(app, monkeypatch):
    """The drain that BUILDS art must invalidate what resolved it, or a
    pool scanned before a sibling version landed stays one file short."""
    manager = object.__new__(AppController)
    manager._watches = []
    cleared = []
    monkeypatch.setattr(paths, "reset_art_file_cache",
                        lambda: cleared.append("art_file"))
    monkeypatch.setattr(pantheon, "reset_rotation_cache",
                        lambda: cleared.append("rotation"))
    monkeypatch.setattr(archetype_geometry, "reset_art_size_cache",
                        lambda: cleared.append("art_size"))

    manager._emit_art_ready()

    assert set(cleared) == {"art_file", "rotation", "art_size"}


# --- pure work is measured once ------------------------------------------------

def test_the_label_fit_is_measured_once_per_name(app):
    """`name_label_px` shapes text through QFontMetricsF and is called
    for every weekday (or archetype) label on every tick."""
    painting.name_label_px.cache_clear()

    first = painting.name_label_px("Jupiter", 120.0)
    for _ in range(20):
        painting.name_label_px("Jupiter", 120.0)

    info = painting.name_label_px.cache_info()
    assert info.misses == 1 and info.hits == 20
    assert painting.name_label_px("Jupiter", 120.0) == first


# --- one job per process, not one per watch ------------------------------------

def test_only_one_watch_translates_a_language():
    """Five watches sharing a language used to start five workers on the
    same corpus, all writing one cache file."""
    translations.release_translation("sr-Latn")
    try:
        assert translations.claim_translation("sr-Latn") is True
        assert translations.claim_translation("sr-Latn") is False
        assert translations.claim_translation("de") is True
    finally:
        translations.release_translation("sr-Latn")
        translations.release_translation("de")


def test_a_released_language_can_be_claimed_again():
    """The run is resumable by design — a claim left standing would block
    every later retry for the rest of the session."""
    assert translations.claim_translation("de") is True
    translations.release_translation("de")

    assert translations.claim_translation("de") is True
    translations.release_translation("de")


def test_the_translation_cache_write_is_serialized(tmp_path):
    """The read-merge-write is not atomic just because `os.replace` is.
    Two unlocked writers lose whatever the first one persisted."""
    store = translations.TranslationStore(
        directory=tmp_path, bundled=tmp_path / "absent"
    )
    corpus = {f"k{i}": f"text {i}" for i in range(40)}

    def write(keys):
        chunk = {key: corpus[key] for key in keys}
        store.save("de", chunk, {key: f"de {key}" for key in keys})

    first = list(corpus)[:20]
    second = list(corpus)[20:]
    threads = [
        threading.Thread(target=write, args=(first,)),
        threading.Thread(target=write, args=(second,)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    saved = store.load("de")
    assert set(saved) == set(corpus), "a writer's entries were lost"


def test_the_corpus_is_built_once():
    """It re-reads symbolism.json (1.12 MB) and encyclopedia.json
    (439 KB); it used to run once per watch and again in the worker."""
    translations._CORPUS = None
    first = translations.collect_corpus()

    with _Counter() as counted:
        again = translations.collect_corpus()

    assert again is first
    assert counted.exists == 0


# --- the city database ---------------------------------------------------------

def test_the_city_database_is_shared_and_reference_counted():
    """5.6 MB, the largest bundled JSON. Two open pickers must share one
    tree — and the FIRST to close must not pull it from the second."""
    repository = locations.shared_locations()
    assert repository is locations.shared_locations()
    repository._holders = 0
    repository._tree = None

    repository.acquire()
    repository.acquire()
    assert repository._tree is not None

    repository.release()
    assert repository._tree is not None, "a sibling picker was still open"

    repository.release()
    assert repository._tree is None, "the last close must free 5.6 MB"


def test_extra_releases_cannot_drive_the_count_negative():
    repository = locations.shared_locations()
    repository._holders = 0

    repository.release()
    repository.release()
    repository.acquire()

    assert repository._tree is not None
    repository.release()


# --- the Sunday dual answers the same question, without the extra stat ------

def test_the_sunday_dual_probe_agrees_with_the_form_it_replaced(app):
    """`sunday_dual_face` used `art_file(...).exists()` — a stat on the
    PAINT path, on a file the resolver had just found (the very pattern
    this module exists to remove). It now asks `existing_art_file`,
    which answers the SAME question without the stat.

    Behaviour-identical, proved rather than asserted: across every
    weekday theme the app ships, both doors must return the same verdict
    for the same skin. If they ever diverge, a Servant seat silently
    appears or vanishes."""
    from app.skin_builder import build_skin
    from app.settings_store import Settings, replace
    from config import constants
    from render.slot_layout import sunday_dual_face

    checked = 0
    for theme in constants.WEEKDAY_THEMES:
        skin = build_skin(replace(
            Settings(), pointer="octa", weekday_theme=theme,
        ))
        spec = skin.weekday_set
        if spec.dual_asset is None:
            continue
        old_form = paths.art_file(spec.dual_asset).exists()
        new_form = paths.existing_art_file(spec.dual_asset) is not None
        assert old_form == new_form, theme
        # The predicate's own verdict follows that answer: with the art
        # missing there is no Servant face, whatever else the skin says.
        if not new_form:
            assert not sunday_dual_face(skin), theme
        checked += 1
    assert checked >= 5, "the themes with a dual asset are the point of this"
