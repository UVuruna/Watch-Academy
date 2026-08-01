# Rewrite Sheet Paths — Flow

**About:** [description](../__about/rewrite_sheet_paths.md)

## Algorithm

```mermaid
flowchart TB
    A[Walk every research/prompts/**/*.md] --> B[Find each backticked assets/...png svg path]
    B --> C["transform(path): same family rules as\nbuild_relocation_manifest.new_path, sourceless"]
    C --> D{path changed?}
    D -- yes --> E[substitute in text, count it]
    D -- no --> F[leave untouched]
    E --> G[write the file back if any path changed]
    F --> G
    G --> H[print total paths rewritten / files touched]
```

Pseudocode (language-neutral):

    FOR EACH sheet UNDER research/prompts/ (recursively):
        text = read the sheet
        FOR EACH backticked "assets/....png" or "....svg" path found in text:
            new_path = transform(path)   # same per-root rules as the
                                          # relocation manifest, minus the
                                          # source-folder collapse and suffix
            IF new_path != path: substitute it, count the change
        IF the sheet's text changed: write it back
    PRINT total paths rewritten, total files touched
