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

from config import constants, defaults, paths, profiling, ui_text
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
            for face, text in article.get("faces", {}).items():
                # The dual Sunday's Ruler/Servant face texts (2026-07-13).
                corpus[f"articles/{article_set}/{body}/faces/{face}"] = text
    for group in ("zodiac_articles", "chinese_articles",
                  "chinese_elements", "trio_articles"):
        for name, article in canon[group].items():
            corpus[f"{group}/{name}/base"] = article["base"]
            for combo, text in article.get("variants", {}).items():
                corpus[f"{group}/{name}/variants/{combo}"] = text
    encyclopedia = paths.database_dir() / "encyclopedia.json"
    if encyclopedia.exists():
        # The Encyclopedia's own content (owner expansion 2026-07-13):
        # instrument articles, week day pages, emblem entries.
        data = json.loads(encyclopedia.read_text(encoding="utf-8"))
        for section in ("instrument", "week", "seasons"):
            for key, node in data.get(section, {}).items():
                corpus[f"encyclopedia/{section}/{key}/title"] = node["title"]
                corpus[f"encyclopedia/{section}/{key}/base"] = node["base"]
        for family in ("virtues", "sins", "moods", "duality",
                       "ninths", "intelligence"):
            for name, node in data[family].items():
                corpus[f"encyclopedia/{family}/{name}/base"] = node["base"]
    captions = defaults.GUIDE_DIR / "captions.json"
    if captions.exists():
        for stem, text in json.loads(
            captions.read_text(encoding="utf-8")
        ).items():
            corpus[f"guide/{stem}"] = text
    pages = defaults.GUIDE_DIR / "pages.json"
    if pages.exists():
        for index, page in enumerate(
            json.loads(pages.read_text(encoding="utf-8"))["pages"]
        ):
            corpus[f"guide_page/{index}"] = page["title"]
    # Phase 2 (owner spec): the UI chrome — menu, dialogs, balloons,
    # hover labels and name tables. The English string IS the key.
    for text in ui_text.UI_STRINGS:
        corpus[f"ui/{text}"] = text
    return corpus


@profiling.timed("Translate chunk")
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
    the changed entries. Languages with a BUNDLED ORIGINAL (owner
    decision 2026-07-11: English and Serbian Latin ship hand-written —
    Database/translations/<lang>.json) read the bundle first; the
    user's cache only overlays entries whose English changed after
    the release."""

    def __init__(self, directory: Path | None = None,
                 bundled: Path | None = None):
        self._dir = directory or (paths.settings_path().parent / "translations")
        self._bundled = bundled or (paths.database_dir() / "translations")

    def _path(self, lang: str) -> Path:
        return self._dir / f"{lang}.json"

    def _bundled_data(self, lang: str) -> dict:
        path = self._bundled / f"{lang}.json"
        if not path.exists():
            return {"hashes": {}, "texts": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def load(self, lang: str) -> dict:
        """key → translated text. The bundled original wins whenever
        it was made from the SAME English as the user's cached entry
        (an original beats a machine draft of the same source — e.g. a
        pre-release MT cache); the user's entry wins only where its
        English moved on after the release."""
        bundled = self._bundled_data(lang)
        texts = dict(bundled["texts"])
        path = self._path(lang)
        if path.exists():
            user = json.loads(path.read_text(encoding="utf-8"))
            for key, text in user["texts"].items():
                if (key not in texts
                        or user["hashes"].get(key) != bundled["hashes"].get(key)):
                    texts[key] = text
        return texts

    def missing(self, lang: str, corpus: dict) -> dict:
        """The corpus entries not yet translated for `lang` — new keys
        AND entries whose English source matches NEITHER the bundled
        original NOR the user's cache."""
        bundled = self._bundled_data(lang)["hashes"]
        user = {}
        path = self._path(lang)
        if path.exists():
            user = json.loads(path.read_text(encoding="utf-8"))["hashes"]
        return {
            key: text
            for key, text in corpus.items()
            if self._hash(text) not in (bundled.get(key), user.get(key))
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
