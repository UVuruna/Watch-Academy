"""Merge the staged pantheon/religion/ninth articles into the live
databases (owner execution wave, 2026-07-15).

Reads research/articles_staging/*.json, then:
- adds the four pantheon article sets to Database/symbolism.json
  (validating shape: 7 bodies; non-$ref entries carry base + exactly
  the six pointer/palette variant keys),
- applies the Religion rework moves (Christianity → sun with the new
  ruler/servant faces, Sikhism → venus, Eleusis into the Ancient set;
  the displaced Freemasonry/Sikhism seat entries leave the article
  tables — Freemasonry re-lives as the theme's ninth),
- adds the new ninths to Database/encyclopedia.json,
- lands every staged Serbian text in the sr-Latn bundle (hash-keyed
  against the merged English) and prunes orphaned bundle keys,
- prints the audit: bundle == corpus, missing/stale/orphans.

Run from the project root:  python research/merge_articles.py
Idempotent — re-running overwrites the same keys with the same data.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VARIANT_KEYS = {
    "hexa_paint", "hexa_light", "octa_paint", "octa_light",
    "cross", "trio",
}
STAGING = ROOT / "research" / "articles_staging"
SYMBOLISM = ROOT / "Database" / "symbolism.json"
ENCYCLOPEDIA = ROOT / "Database" / "encyclopedia.json"
BUNDLE = ROOT / "Database" / "translations" / "sr-Latn.json"


def check_entry(name: str, entry: dict) -> None:
    if "$ref" in entry:
        ref = entry["$ref"]
        assert (
            isinstance(ref, list) and len(ref) == 2
        ), f"{name}: bad $ref {ref!r}"
        return
    assert entry.get("base", "").strip(), f"{name}: empty base"
    variants = entry.get("variants", {})
    assert set(variants) == VARIANT_KEYS, (
        f"{name}: variant keys {sorted(variants)}"
    )
    for combo, text in variants.items():
        assert text.strip(), f"{name}/{combo}: empty variant"


def main() -> None:
    symbolism = json.loads(SYMBOLISM.read_text(encoding="utf-8"))
    encyclopedia = json.loads(ENCYCLOPEDIA.read_text(encoding="utf-8"))
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    articles = symbolism["articles"]
    staged_sr: dict[str, str] = {}

    # --- The four pantheon sets --------------------------------------------------
    for stem in (
        "greek_pantheon", "egypt_pantheon",
        "norse_pantheon", "slavic_pantheon",
    ):
        staging = json.loads(
            (STAGING / f"{stem}.json").read_text(encoding="utf-8")
        )
        assert staging["set"] == stem
        bodies = staging["articles"]
        assert set(bodies) == {
            "sun", "moon", "mars", "mercury", "jupiter", "venus",
            "saturn",
        }, f"{stem}: bodies {sorted(bodies)}"
        for body, entry in bodies.items():
            check_entry(f"{stem}/{body}", entry)
            if "$ref" in entry:
                ref_set, ref_body = entry["$ref"]
                assert ref_body in articles[ref_set], entry["$ref"]
        articles[stem] = bodies
        for name, base in staging.get("ninths", {}).items():
            assert base.strip(), f"{stem} ninth {name}"
            encyclopedia["ninths"][name] = {"base": base}
        staged_sr.update(staging["sr"])
        print(f"{stem}: {len(bodies)} bodies, "
              f"{len(staging.get('ninths', {}))} ninth(s), "
              f"{len(staging['sr'])} SR keys")

    # --- The Religion rework -----------------------------------------------------
    religion = json.loads(
        (STAGING / "religion_and_ninths.json").read_text(encoding="utf-8")
    )
    creeds = articles["religion"]
    ancient = articles["religion_alt"]
    sun_entry = dict(religion["religion_sun"])
    sun_entry["faces"] = religion["religion_faces"]
    sun_entry["name"] = "Christianity"     # the religion sets carry
    check_entry("religion/sun", sun_entry)  # hover NAMES per entry
    venus_entry = dict(religion["religion_venus"])
    venus_entry["name"] = "Sikhism"
    check_entry("religion/venus", venus_entry)
    eleusis = dict(religion["articles"]["religion_alt_jupiter"])
    eleusis["name"] = "Eleusinian Mysteries"
    check_entry("religion_alt/jupiter", eleusis)
    creeds["sun"] = sun_entry          # Christianity enthroned (was freemasonry)
    creeds["venus"] = venus_entry      # Sikhism moves in (was christianity)
    ancient["jupiter"] = eleusis       # Eleusis (was sikhism)
    for name, base in religion["ninths"].items():
        assert base.strip(), f"ninth {name}"
        encyclopedia["ninths"][name] = {"base": base}
    staged_sr.update(religion["sr"])
    print(f"religion rework: sun/venus/ancient-jupiter replaced, "
          f"{len(religion['ninths'])} ninths, {len(religion['sr'])} SR keys")

    SYMBOLISM.write_text(
        json.dumps(symbolism, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    ENCYCLOPEDIA.write_text(
        json.dumps(encyclopedia, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    # --- The Serbian bundle ------------------------------------------------------
    from data.translations import collect_corpus

    corpus = collect_corpus()
    missing_sr = [
        key for key in corpus
        if key not in bundle["texts"] and key not in staged_sr
    ]
    for key, serbian in staged_sr.items():
        assert key in corpus, f"staged SR key not in corpus: {key}"
        assert serbian.strip(), f"empty SR: {key}"
        bundle["hashes"][key] = hashlib.sha1(
            corpus[key].encode("utf-8")
        ).hexdigest()
        bundle["texts"][key] = serbian
    orphans = [key for key in list(bundle["texts"]) if key not in corpus]
    for key in orphans:
        bundle["texts"].pop(key)
        bundle["hashes"].pop(key, None)
    BUNDLE.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    stale = [
        key for key, digest in bundle["hashes"].items()
        if key in corpus and digest != hashlib.sha1(
            corpus[key].encode("utf-8")
        ).hexdigest()
    ]
    print(f"bundle {len(bundle['texts'])} = corpus {len(corpus)}")
    print(f"missing {len(missing_sr)} / stale {len(stale)} / "
          f"orphans pruned {len(orphans)}")
    for key in missing_sr[:12]:
        print(" ! missing SR:", key)
    for key in stale[:6]:
        print(" ! stale:", key)


if __name__ == "__main__":
    main()
