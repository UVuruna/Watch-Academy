# Contract Pack Generator — Flow

**About:** [description](../__about/make_contract_pack.md)

## Algorithm — two independent export passes, one manifest

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[sys.path.insert desktop/] --> B[Import core, config.registry, data repositories]

    subgraph VECTORS["build_golden_vectors()"]
        V1["Call each of the 7 group builders<br/>(belgrade_dst, tromso_regimes,<br/>moon_illumination, mockup_day,<br/>equinoxes, hand_angles,<br/>hexagram_rotation)"]
        V1 --> V2["Each builder calls the REAL core<br/>function(s) and returns<br/>[{name, inputs, expected, tolerance}]"]
        V2 --> V3[Write golden_vectors.json]
    end

    subgraph TABLES["build_* per table"]
        T1["Call the real registry accessor<br/>(config.registry.week.WEEK,<br/>availability, pointers,<br/>config.palette, config.encyclopedia_tree,<br/>data.rings._bundled_presets())"]
        T1 --> T2[Write tables/&lt;name&gt;.json]
    end

    B --> VECTORS
    B --> TABLES
    VECTORS --> M[sha256 every written file]
    TABLES --> M
    M --> N["Write manifest.json:<br/>pack_version, created_at (git log -1),<br/>per-file sha256, vector group names"]
    N --> DONE[[print summary]]
```

Pseudocode (language-neutral):

    insert desktop/ onto sys.path
    import core.*, config.registry.*, data.* (the real desktop packages)

    # --- golden vectors ---------------------------------------------------
    groups = {}
    FOR EACH (group_name, builder) IN VECTOR_GROUPS:
        groups[group_name] = builder()     # calls real core functions,
                                            # returns named input/expected/
                                            # tolerance vectors
    write golden_vectors.json { meta, groups }

    # --- table exports ------------------------------------------------------
    FOR EACH (table_name, builder) IN TABLE_BUILDERS:
        payload = builder()                # reads the real registry module
        write tables/<table_name>.json (payload)

    # --- manifest ------------------------------------------------------------
    hashes = { path: sha256(path) FOR EACH written file }
    manifest = {
        pack_version: "1",
        created_at: `git log -1 --format=%cI`,   # never wall clock
        vector_groups: sorted(groups.keys()),
        files: hashes,
    }
    write manifest.json

    print "N vector groups (M vectors), K tables -> shared/contract/"
