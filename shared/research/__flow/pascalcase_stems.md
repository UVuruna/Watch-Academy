# PascalCase Stems — Flow

**About:** [description](../__about/pascalcase_stems.md)

## Algorithm

```mermaid
flowchart TB
    A[Walk every .png under weeks/ calendars/ archetypes/] --> B["pascal_name(): peel off _gem/_gpt and\n_vN suffixes, Titlecase the remaining tokens"]
    B --> C{new name != old name?}
    C -- yes --> D[add to the rename plan]
    C -- no --> E[skip]
    D --> F["detect collisions: two sources -> one target,\nor a different pre-existing file"]
    F --> G{collision?}
    G -- yes --> H[ABORT — print every collision]
    G -- no --> I{--execute?}
    I -- no --> J[print the plan — dry run]
    I -- yes --> K["git mv each (two-step through a temp\nname when the rename is case-only)"]
    K --> L[recount files; verify before == after]
```

Pseudocode (language-neutral):

    FOR EACH png UNDER weeks/, calendars/, archetypes/:
        tokens = stem split on "_"
        peel a trailing source tag (_gem/_gpt) off the tokens, keep it verbatim
        peel a trailing _vN version tag off the tokens, keep it verbatim
        Titlecase every remaining token that has no uppercase letter already
        new_name = the Titlecased tokens + the peeled tail, rejoined
        IF new_name != old_name: PLAN a rename

    DETECT collisions: two different sources renaming onto the same target,
    or a target that already exists as a genuinely DIFFERENT file
    IF any collision: ABORT, print them all

    IF --execute:
        FOR EACH planned rename:
            IF old and new differ only by case: git mv through a temp name
            ELSE: git mv directly
        recount files; verify the total is unchanged
    ELSE:
        print the plan only
