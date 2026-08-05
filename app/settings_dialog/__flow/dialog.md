# Settings Dialog — Flow

**About:** [description](../__about/dialog.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph SHELL["SettingsDialog window (square, 50% of screen height)"]
        subgraph BODY["ordinary path — body QHBoxLayout"]
            NAV["QListWidget nav column (170px)
            Location ▸
            Language ▸
            System ▸"]
            STACK["QStackedWidget
            one scrollable panel per section,
            each panel's own QScrollArea"]
        end
        HIDDEN["initial_section='Custom art' path
        ONE QScrollArea, no nav column —
        Custom ring + Custom hands groups only"]
        BUTTONS["QDialogButtonBox — OK | Cancel"]
    end
    NAV -- "currentRowChanged → setCurrentIndex" --> STACK
    BODY --> BUTTONS
    HIDDEN --> BUTTONS
```

Each ordinary panel hosts that section's group boxes — built by the three
mixins (see the [folder doc](../___settings_dialog.md)'s layout table for
which groups belong to which section). Phase 6 FINAL cleanup retired the
Display/Colors/Themes sections (their content lives LIVE-APPLY in the Watch
Face window instead) and added the SEPARATE hidden path for Custom art.

## Lifecycle (pseudocode)

    ON open(settings, skin, overlay, initial_section):
        IF initial_section == "Custom art":
            build ONE page: Custom ring group + Custom hands group
            wrap it in a QScrollArea, no nav column (_nav_list/_stack stay None)
        ELSE:
            build 3 (title, [group_boxes]) sections from the 3 mixins
            FOR EACH section:
                add nav row "title ▸"
                wrap its groups in a scrollable panel, add to the stack
            wire nav.currentRowChanged -> stack.setCurrentIndex
            select nav row 0 (or initial_section's row, if named)
        size window: square at 50% of screen height,
                     width = max(content width, nav width + panel floor)
        IF NOT custom-art-only AND settings.city_path exists:
            restore the combo cascade to that path
            re-seed city_name / timezone / latitude / longitude from settings
                (the combo cascade must NOT silently win over the stored values)
            arm suggestion popups — only react to USER input from here on

    ON OK (accepted):
        result_settings():
            custom-art-only -> replace(settings, custom_rings=...) ONLY
            ordinary -> replace(settings, city_name=..., language=..., z_mode=..., ...)
                        every OTHER field (Watch-Face-owned) passes through
                        UNCHANGED, never read off a widget that no longer exists
        the caller (Watch Controller) applies the result

    ON done(result):                      # both OK and Cancel funnel here
        release the location repository's tree (harmless no-op in the
        custom-art-only mode too — the repository is always constructed)
        proceed with the normal QDialog close
