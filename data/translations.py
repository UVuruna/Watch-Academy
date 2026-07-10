"""Translate-once-then-cache (owner spec): we ship ONLY English.

The user picks a language; their machine translates the whole corpus
through the keyless Google gtx endpoint (the owner's "simple option" —
no account, no key) and caches it per language with a source hash per
entry, so edits re-translate only what changed and an interrupted run
resumes. `sr-Latn` is Serbian plus a local Cyrillic→Latin
transliteration.
"""

import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from config import constants, defaults, paths
from data._io import load_json_checked

_SR_LATN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "đ", "е": "e",
    "ж": "ž", "з": "z", "и": "i", "ј": "j", "к": "k", "л": "l", "љ": "lj",
    "м": "m", "н": "n", "њ": "nj", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "ћ": "ć", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "č",
    "џ": "dž", "ш": "š",
}


def transliterate_sr(text: str) -> str:
    """Serbian Cyrillic → Latin (deterministic, local). Digraphs (lj,
    nj, dž) follow their word's case: NJEGOŠ, Njegoš, njegoš."""
    out = []
    for index, ch in enumerate(text):
        latin = _SR_LATN.get(ch.lower())
        if latin is None:
            out.append(ch)
        elif not ch.isupper():
            out.append(latin)
        else:
            neighbor = text[index + 1] if index + 1 < len(text) else (
                text[index - 1] if index else ""
            )
            out.append(
                latin.upper() if neighbor.isupper() else latin.capitalize()
            )
    return "".join(out)


def collect_corpus() -> dict:
    """key → English text for everything translatable (Phase 1: the
    reading content — articles, blurbless hover corpora, guide
    captions)."""
    canon = load_json_checked(
        paths.database_dir() / "symbolism.json", "Symbolism database"
    )
    corpus: dict = {}
    for article_set, bodies in canon["articles"].items():
        for body, article in bodies.items():
            corpus[f"articles/{article_set}/{body}/base"] = article["base"]
            for combo, text in article.get("variants", {}).items():
                corpus[f"articles/{article_set}/{body}/variants/{combo}"] = text
    for group in ("zodiac_articles", "chinese_articles",
                  "chinese_elements", "trio_articles"):
        for name, article in canon[group].items():
            corpus[f"{group}/{name}/base"] = article["base"]
            for combo, text in article.get("variants", {}).items():
                corpus[f"{group}/{name}/variants/{combo}"] = text
    captions = defaults.GUIDE_DIR / "captions.json"
    if captions.exists():
        for stem, text in json.loads(
            captions.read_text(encoding="utf-8")
        ).items():
            corpus[f"guide/{stem}"] = text
    return corpus


def translate_texts(texts: dict, target: str, progress=None) -> dict:
    """Translate `texts` (key → English) to `target`, one request per
    entry through the gtx endpoint. Raises on network failure — the
    caller must surface it (Rule #1); already-translated entries are
    saved by the caller, so a retry resumes."""
    google_target = "sr" if target == "sr-Latn" else target
    translated: dict = {}
    for index, (key, text) in enumerate(texts.items()):
        url = (
            defaults.TRANSLATE_ENDPOINT
            + "?client=gtx&sl=en&dt=t&tl="
            + urllib.parse.quote(google_target)
            + "&q="
            + urllib.parse.quote(text)
        )
        with urllib.request.urlopen(
            url, timeout=defaults.TRANSLATE_TIMEOUT_S
        ) as response:
            payload = json.loads(response.read())
        result = "".join(part[0] for part in payload[0])
        if target == "sr-Latn":
            result = transliterate_sr(result)
        translated[key] = result
        if progress is not None:
            progress(index + 1, len(texts))
    return translated


class TranslationStore:
    """Per-language overlay cache: {hashes: {key: sha1(en)}, texts:
    {key: translated}} — hash-tracked so corpus edits re-translate only
    the changed entries."""

    def __init__(self, directory: Path | None = None):
        self._dir = directory or (paths.settings_path().parent / "translations")

    def _path(self, lang: str) -> Path:
        return self._dir / f"{lang}.json"

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def load(self, lang: str) -> dict:
        """key → translated text (empty when nothing is cached yet)."""
        path = self._path(lang)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))["texts"]

    def missing(self, lang: str, corpus: dict) -> dict:
        """The corpus entries not yet translated for `lang` — new keys
        AND entries whose English source changed since caching."""
        path = self._path(lang)
        hashes = {}
        if path.exists():
            hashes = json.loads(path.read_text(encoding="utf-8"))["hashes"]
        return {
            key: text
            for key, text in corpus.items()
            if hashes.get(key) != self._hash(text)
        }

    def save(self, lang: str, corpus_slice: dict, texts: dict) -> None:
        """Merge freshly translated entries into the cache (atomic)."""
        path = self._path(lang)
        data = {"hashes": {}, "texts": {}}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        for key, translated in texts.items():
            data["texts"][key] = translated
            data["hashes"][key] = self._hash(corpus_slice[key])
        self._dir.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        os.replace(tmp, path)
