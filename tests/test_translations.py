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
    store = TranslationStore(tmp_path)
    corpus = {"a/base": "Hello", "b/base": "World"}
    assert store.load("sr") == {}
    assert store.missing("sr", corpus) == corpus
    store.save("sr", corpus, {"a/base": "Zdravo", "b/base": "Svete"})
    assert store.load("sr") == {"a/base": "Zdravo", "b/base": "Svete"}
    assert store.missing("sr", corpus) == {}
    # An English edit invalidates ONLY its own entry.
    corpus["b/base"] = "World, changed"
    assert store.missing("sr", corpus) == {"b/base": "World, changed"}


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