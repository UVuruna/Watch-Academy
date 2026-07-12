"""Translate-once-then-cache (owner spec): corpus collection, the
hash-tracked cache, the Serbian transliteration and the repository
overlay — all offline (the network client is exercised manually)."""

from data.symbolism import SymbolismRepository
from data.translations import TranslationStore, collect_corpus, transliterate_sr


def test_corpus_covers_every_article_family():
    corpus = collect_corpus()
    assert len(corpus) > 300
    assert "articles/planets/sun/base" in corpus
    assert "articles/religion_alt/venus/variants/trio" in corpus
    assert "zodiac_articles/Aries/base" in corpus
    assert "chinese_articles/Horse/base" in corpus
    assert "chinese_elements/Fire/base" in corpus
    assert "trio_articles/Faith/base" in corpus
    assert all(text.strip() for text in corpus.values())


def test_store_translates_only_what_changed(tmp_path):
    store = TranslationStore(tmp_path, bundled=tmp_path / "none")
    corpus = {"a/base": "Hello", "b/base": "World"}
    assert store.load("sr") == {}
    assert store.missing("sr", corpus) == corpus
    store.save("sr", corpus, {"a/base": "Zdravo", "b/base": "Svete"})
    assert store.load("sr") == {"a/base": "Zdravo", "b/base": "Svete"}
    assert store.missing("sr", corpus) == {}
    # An English edit invalidates ONLY its own entry.
    corpus["b/base"] = "World, changed"
    assert store.missing("sr", corpus) == {"b/base": "World, changed"}


def test_bundled_original_serves_without_network(tmp_path):
    """Owner decision 2026-07-11: EN + SR-Latn ship hand-written. A
    bundled file answers load() and missing() by itself; the user
    cache only overlays entries whose English changed later."""
    import json

    bundled = tmp_path / "bundled"
    bundled.mkdir()
    store = TranslationStore(tmp_path / "user", bundled=bundled)
    corpus = {"a/base": "Hello", "b/base": "World"}
    (bundled / "sr-Latn.json").write_text(
        json.dumps({
            "hashes": {key: store._hash(text) for key, text in corpus.items()},
            "texts": {"a/base": "Zdravo", "b/base": "Svete"},
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    assert store.missing("sr-Latn", corpus) == {}          # nothing to fetch
    assert store.load("sr-Latn")["a/base"] == "Zdravo"
    # A PRE-release machine cache of the same English must NOT shadow
    # the shipped original (same source hash -> the bundle wins).
    store.save("sr-Latn", corpus, {"a/base": "MT-Zdravo"})
    assert store.load("sr-Latn")["a/base"] == "Zdravo"
    # A post-release English edit: only that entry re-translates, and
    # the fresh user-cache text WINS over the stale bundled one.
    corpus["b/base"] = "World, changed"
    assert store.missing("sr-Latn", corpus) == {"b/base": "World, changed"}
    store.save("sr-Latn", corpus, {"b/base": "Svete, novi"})
    assert store.load("sr-Latn") == {"a/base": "Zdravo", "b/base": "Svete, novi"}
    assert store.missing("sr-Latn", corpus) == {}


def test_phase2_chrome_speaks_the_overlay():
    """Phase 2 (owner spec): the menu and dialog chrome resolve through
    ui/<text> overlay entries — with a marker overlay every Settings
    group title and the Time Travel labels come back translated."""
    import os
    import tempfile
    from pathlib import Path

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QGroupBox

    from app.controller import build_skin
    from app.settings_dialog import SettingsDialog
    from app.settings_store import SettingsStore
    from app.time_travel import TimeTravelDialog
    from config import ui_text

    QApplication.instance() or QApplication([])
    overlay = {f"ui/{text}": f"№{text}" for text in ui_text.UI_STRINGS}
    store = SettingsStore(Path(tempfile.mkdtemp()) / "settings.json")
    settings = store.load()
    dialog = SettingsDialog(settings, build_skin(settings), overlay)
    titles = {group.title() for group in dialog.findChildren(QGroupBox)}
    assert "№Location" in titles
    assert "№Language" in titles
    assert "№Custom ring" in titles
    travel = TimeTravelDialog(44.0, 20.0, overlay=overlay)
    assert "№Time Travel" in travel.windowTitle()
    # The English fallback stays intact without an overlay.
    bare = SettingsDialog(settings, build_skin(settings))
    assert "Location" in {g.title() for g in bare.findChildren(QGroupBox)}


def test_phase2b_hover_lines_speak_the_overlay():
    """Phase 2b: the hover INFO lines translate — labels, day/month/
    phase names, dot ordinals — while the English path keeps the
    raised suffixes."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral
    from PySide6.QtWidgets import QApplication

    from app.controller import build_skin
    from app.settings_store import Settings
    from config import defaults
    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    QApplication.instance() or QApplication([])
    overlay = {
        "ui/Sunday": "nedelja", "ui/July": "jul", "ui/Sun": "Sunce",
        "ui/Illumination": "Osvetljenost", "ui/Summer": "Leto",
        "ui/{season} {ordinal} of {total} Days": "{season} {ordinal} od {total} dana",
    }
    city = defaults.DEFAULT_CITY
    now = datetime(2026, 7, 12, 12, 0, tzinfo=ZoneInfo(city["timezone"]))
    day = build_day_context(
        now,
        astral.Observer(latitude=city["latitude"], longitude=city["longitude"]),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    sr = Compositor(build_skin(Settings()), AssetCache(), overlay=overlay)
    sr._day, sr._last_tick = day, tick
    title = sr._weekday_tooltip("sun", active=True)
    assert "Sunce" in title and "nedelja, 12. jul 2026" in title
    assert "Leto 22. od 94 dana" in sr._season_row()
    assert "Osvetljenost" in sr._moon_text()
    en = Compositor(build_skin(Settings()), AssetCache())
    en._day, en._last_tick = day, tick
    assert "12<sup>th</sup> July 2026" in en._weekday_tooltip("sun", True)


def test_theme_rotation_cycles_and_persists(tmp_path):
    """Owner spec 2026-07-12: the checked weekday themes rotate every
    N minutes — the cycle helper wraps, a current theme outside the
    list restarts it, and the three settings round-trip."""
    from app.controller import _next_rotation_theme
    from app.settings_store import Settings, SettingsStore, replace

    assert _next_rotation_theme("greek", ("planets", "greek", "egypt")) == "egypt"
    assert _next_rotation_theme("egypt", ("planets", "greek", "egypt")) == "planets"
    assert _next_rotation_theme("norse", ("planets", "greek")) == "planets"
    store = SettingsStore(tmp_path / "settings.json")
    store.save(replace(
        Settings(),
        theme_rotation=True,
        theme_rotation_minutes=120,
        theme_rotation_themes=("greek", "egypt"),
    ))
    loaded = store.load()
    assert loaded.theme_rotation is True
    assert loaded.theme_rotation_minutes == 120
    assert loaded.theme_rotation_themes == ("greek", "egypt")


def test_serbian_transliteration():
    assert transliterate_sr("Месец носи Спокој") == "Mesec nosi Spokoj"
    assert transliterate_sr("Џак и Љиљана, ЊЕГОШ") == "Džak i Ljiljana, NJEGOŠ"
    assert transliterate_sr("100% latinice ostaje") == "100% latinice ostaje"


def test_repository_overlay_wins_with_english_fallback():
    overlay = {
        "articles/planets/sun/base": "PREVEDENO",
        "articles/planets/sun/variants/trio": "TRIO-PREVOD",
    }
    repo = SymbolismRepository(overlay=overlay)
    article = repo.article("planets", "sun")
    assert article["base"] == "PREVEDENO"
    assert article["variants"]["trio"] == "TRIO-PREVOD"
    # Untranslated variants keep the English original.
    assert article["variants"]["cross"] not in ("", None)
    assert article["variants"]["cross"] != "TRIO-PREVOD"
    # No overlay -> the untouched originals.
    assert SymbolismRepository().article("planets", "sun")["base"] != "PREVEDENO"