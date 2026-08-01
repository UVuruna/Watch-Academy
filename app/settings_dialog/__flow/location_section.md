# Location Section — Flow

**About:** [description](../__about/location_section.md)

## Layout

📦 **Location** (`QGroupBox`, `QFormLayout`)
  🔍 Search (`QLineEdit`) + status label ("N found" / "not found")
  📋 results list (`QListWidget`, hidden until ≥2 characters typed)
  🔽 Continent combo
  🔽 Subregion combo
  🔽 Country combo
  🔽 Region combo ("—" = the country's direct cities)
  🔽 City combo
  🔢 Latitude spinbox (4 decimals)
  🔢 Longitude spinbox (4 decimals)
  🏷️ Timezone label (read-only)

📦 **Quick Jump cities** (`QGroupBox`, `QFormLayout`)
  🔍 Add (`QLineEdit`, same 45k-city search index)
  📋 jump results list (click → adds to the jump list)
  📋 Cities list (the user's saved jump cities)
  🔘 "Remove selected" button
  🏷️ note label (word-wrapped)

## Behaviour (pseudocode)

    ON continent/subregion/country/region changed at level L:
        repopulate every combo BELOW level L from the location tree
        IF L ≤ 3: refresh the country's "major cities" suggestions
        re-run city selection

    ON city selected:
        look up the record for (group path, city name)
        fill city_name, timezone, latitude, longitude from the record

    ON search text changed (≥ 2 chars):
        fold the typed text; match against ALL 45k cities (loaded once,
        cached in self._all_cities)
        sort: prefix matches first, then alphabetical
        show the top 30 in the results list
        click a result → jump the combo cascade to that path

    ON Quick Jump search match clicked:
        resolve the city record
        IF not already in the jump list: append it
        refresh the jump list widget

    ON "Remove selected":
        delete the jump list's current row from the working jump_cities list
