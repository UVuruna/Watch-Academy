# Symbolism Repository — Flow

**About:** [description](../__about/symbolism.md)

## Algorithm — `article()`: `$ref` reseat resolution

A pantheon "reseat" — the same mythic figure serving a new seat — does
not duplicate its base text; it POINTS at its source entity so the text
translates exactly once. The reseat may still carry its OWN `variants`
(a cross-seat reseat's positions differ from the source's) and its OWN
`faces` (a pantheon Sunday dual), which override the merged result.

```mermaid
flowchart TB
    A[article(set, body)] --> B[load node = articles[set][body]]
    B --> C{"$ref" in node?}
    C -- no --> D[localize node under its own prefix, return]
    C -- yes --> E[recurse: article(ref_set, ref_body)]
    E --> F[merged = source article, drop its faces]
    F --> G{node has own variants?}
    G -- yes --> H[overwrite merged.variants, localized under RESEAT keys]
    G -- no --> I
    H --> I{node has own faces?}
    I -- yes --> J[overwrite merged.faces, localized under RESEAT keys]
    I -- no --> K[return merged]
    J --> K
```

Pseudocode (language-neutral):

    FUNCTION article(article_set, body):
        node = database.articles[article_set][body]
        prefix = "articles/{article_set}/{body}"
        IF "$ref" not in node:
            RETURN localize(prefix, node)      # base, variants, faces overlaid from translation

        ref_set, ref_body = node["$ref"]
        merged = article(ref_set, ref_body)     # RECURSE into the source entity
        remove merged.faces                     # the source's own faces never leak through
        IF node has "variants":
            merged.variants = localize_each(node.variants, under prefix)  # reseat's OWN positions
        IF node has "faces":
            merged.faces = localize_each(node.faces, under prefix)        # reseat's OWN dual text
        RETURN merged

`localize(prefix, node)` copies `node`, then for each of `base` /
`variants` / `faces` present, overlays the translated text found at
`{prefix}/{field}` (or `{prefix}/{field}/{key}`), falling back to the
English original when no translation exists yet.
