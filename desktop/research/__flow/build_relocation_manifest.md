# Build Relocation Manifest — Flow

**About:** [description](../__about/build_relocation_manifest.md)

## Algorithm

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[Walk every .png/.svg under assets/] --> B[Split root + optional source folder]
    B --> C{root value?}
    subgraph DISPATCH["new_path() dispatch"]
        C -- weekday --> D[theme -> group via THEME_GROUP / renames / WOW-CP-SW blocks]
        C -- emblem --> E[weeks/inner_wheel/family]
        C -- "archetype / badge / eclipse / era / earth" --> F[archetypes|celestial mapping,<br/>alt/ flattened via ALT_FIGURE]
        C -- "zodiac / months / instrument / hands / ring / icons / guide / subdial" --> G[calendars|instrument mapping]
    end
    D --> H[new assets-relative path]
    E --> H
    F --> H
    G --> H
    H --> I[collect (old, new) pairs; count per-root before/after]
    I --> J{--emit-mv flag?}
    J -- yes --> K[print git mv commands]
    J -- no --> L[write research/relocation_manifest.md]
```

Pseudocode (language-neutral):

    FOR EACH file UNDER assets/ (png or svg):
        root = the file's first path segment
        (source, rest) = split an optional gemini/chatgpt segment off the path
        IF root is a KNOWN family:
            apply that family's own relocation rule (theme-group lookup,
            alt/ flattening, figure renames) — every oddball is a named
            table entry, never an inferred branch
            new_path = new-hierarchy path, source folded into a filename suffix
        ELSE:
            new_path = UNRESOLVED marker
    COUNT files per root, before and after; verify total in == total out
    IF --emit-mv:
        PRINT "git mv <old> <new>" for every changed pair
    ELSE:
        WRITE relocation_manifest.md — counts table, full old->new list,
        any UNRESOLVED entries
